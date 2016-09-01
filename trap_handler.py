#!/usr/bin/python
__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.5"

import sys
from models import connect_db
from processor import Processor
from mailer import send_mail
import logging
import time
from config import MAIL_TO
from functions import for_html_trap_list, for_html_title
import os

logging.basicConfig(format = u'[%(asctime)s] %(message)s', level = logging.INFO, filename = u'/var/log/trap_handler.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')

def notify(trap):
    time.sleep(30)
    if trap.is_last():
        # the trap is last in sequence from this host
        # so we notify about all the traps in the sequence
        traps_raw = trap.getcircuit()
        traps_for_notification = []
        for trap in traps_raw:
            if trap.ifName is not None:
                # ignore subinterfaces
                if '.' not in trap.ifName:
                    if not trap.is_blocked():
                        traps_for_notification.append(trap)

                    for trap in traps_raw:
                        if not trap.is_blocked() and trap.is_flapping():
                            trap.block()

                    for trap in traps_raw:
                        trap.del_from_queue()
        
        text_main = for_html_trap_list(traps_for_notification)
        text_title = for_html_title(traps_for_notification)
        send_mail(text_title, MAIL_TO, text_main)
        logging.info(text_title)


if __name__ == "__main__":
    raw = sys.stdin.read()
    
    # parse trap 
    processor = Processor()
    trap = processor.work(raw)
    logging.info(raw)
    if trap is None:
        logging.info("I don't know how to deal with it:\n\n"+raw)
    else:
        logging.info(trap)
        
        # add to the database
        s,e = connect_db()
        s.add(trap)
        s.commit()
        
        # add to the notification queue 
        trap.add_to_queue()
        
        # try to notify in background process 
        pid = os.fork()
        if not pid:
            notify(trap)
        else:
            exit()
