#!/usr/bin/python
__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.1"

import sys
from models import connect_db
from processor import Processor
import logging

logging.basicConfig(format = u'[%(asctime)s] %(message)s', level = logging.INFO, filename = u'/var/log/trap_handler.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')

if __name__ == "__main__":
    raw = sys.stdin.read()
    logging.info('\nRecieved trap:\n'+raw)
    processor = Processor()
    trap = processor.work(raw)
    logging.info(trap)
    session, e = connect_db()
    session.add(trap)
    session.commit()
