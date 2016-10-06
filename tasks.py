import sys
from models import connect_db, Port
from processor import Processor
from mailer import send_mail
import logging
import time
from config import MAIL_TO
from functions import for_html_trap_list, for_html_title
import os
from celery import Celery
from celery.task.control import inspect

tasks = Celery('tasks', broker='amqp://localhost')

logging.basicConfig(format = u'[%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'/var/log/trap_handler.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')


@tasks.task
def parse_raw(raw):
    processor = Processor()
    trap = processor.work(raw)
    if trap is None:
        logging.info("I don't know how to deal with it:\n\n"+raw)
    else:
        logging.info(trap)
        if '.' not in trap.ifName:
            # add to the database
            s,e = connect_db()
            s.add(trap)
            s.commit()
            if not trap.is_blocked(s):
                s.refresh(trap)
                trap_id = trap.id
                # add to the notification queue.
                trap.add_to_queue(s)
                scheduled = inspect().scheduled()['celery@noc.ihome.ru']
                if scheduled:
                    same_host = [x for x in scheduled if trap.host in x['request']['args']]
                    if same_host:
                        for uuid in [x['request']['id'] for x in same_host]:
                            tasks.control.revoke(uuid, terminate=True)
                notify.apply_async(args=[trap_id,trap.host], countdown=30)
            s.close()
        else:
            logging.info('Ignore it')


@tasks.task
def notify(trap_id,host):
    s,e = connect_db()
    trap = s.query(Port).filter(Port.id == trap_id).first()
    if trap.is_last(s):
        # the trap is last in sequence from this host
        # so we notify about all the traps in the sequence
        traps_raw = trap.getcircuit(s)
        traps_for_notification = []
        for trap in traps_raw:
            if trap.ifName is not None:
                # ignore subinterfaces
                if '.' not in trap.ifName:
                    if not trap.is_blocked(s):
                        traps_for_notification.append(trap)

        for trap in traps_raw:
            if not trap.is_blocked(s) and trap.is_flapping(s):
                trap.block(s)

        for trap in traps_raw:
            trap.del_from_queue(s)
        text_main = for_html_trap_list(traps_for_notification,s)
        text_title = for_html_title(traps_for_notification,s)
        send_mail(text_title, MAIL_TO, text_main)
        logging.info(text_title)
    s.close()
