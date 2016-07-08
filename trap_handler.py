#!/usr/bin/python
__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.1"

from models import connect_db
from processor import Processor

if __name__ == "__main__":
    raw = sys.stdin.read()

    processor = Processor()
    trap = processor.work(raw)

    session.add(trap)
    session.commit()
