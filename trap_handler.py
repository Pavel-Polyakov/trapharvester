#!/usr/bin/python
__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.2"

import sys
from models import connect_db
from processor import Processor
from mailer import send_mail
import logging

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
        if '.' not in trap.ifName:
            text = trap.for_mail()
            send_mail(text,'woolly@ihome.ru',text)
    else:
        logging.info("I don't know how to deal with it:\n\n"+raw)
