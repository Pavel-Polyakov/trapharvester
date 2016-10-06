#!/usr/bin/python
__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.6"

import sys
from tasks import parse_raw

if __name__ == "__main__":
    raw = sys.stdin.read()
    parse_raw.delay(raw)
