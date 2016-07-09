#!/usr/bin/python
__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.3"

import sys
from models import connect_db
from processor import Processor
from mailer import send_mail
import logging

from config import MAIL_TO
from html_templates import mail_template_trap, mail_template_full, mail_template_style

logging.basicConfig(format = u'[%(asctime)s] %(message)s', level = logging.INFO, filename = u'/var/log/trap_handler.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')

if __name__ == "__main__":
    raw = sys.stdin.read()
    processor = Processor()
    trap = processor.work(raw)
    if trap is not None:
        logging.info(trap)
        session, e = connect_db()
        session.add(trap)
        session.commit()
        # ignore subinterfaces
        if '.' not in trap.ifName:
            if not trap.is_blocked(session):
                if trap.is_flapping(session):
                    trap.block(session)
                    text_traps = trap.for_html(event='FLAPPING',mood='problem')
                    text_title = "BLOCKED: {host}: {port} ({alias})".format(
                                                          host=trap.hostname,
                                                          port=trap.ifName,
                                                          alias=trap.ifAlias)
                    text_main = mail_template_full.format(traps=text_traps,style=mail_template_style)
                    send_mail(text_title, MAIL_TO, text_main)
                    logging.info(text_title)
		else:
                    mood = 'ok' if 'Up' in trap.event else 'problem'
                    event = trap.event.replace('IF-MIB::link','').upper()
                    text_traps = trap.for_html(event=event,mood=mood)
                    text_title = "{mood}: {host}: {port} ({alias})".format(
                                                          mood=mood.upper(),
                                                          host=trap.hostname,
                                                          port=trap.ifName,
                                                          alias=trap.ifAlias)
                    text_main = mail_template_full.format(traps=text_traps,style=mail_template_style)
                    send_mail(text_title, MAIL_TO,text_main)
                    logging.info(text_title)
        else:
            logging.info("I don't know how to deal with it:\n\n"+raw)
