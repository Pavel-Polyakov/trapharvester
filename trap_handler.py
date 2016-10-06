#!/usr/bin/python
__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.6"

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
from tasks import notify, parse_raw


if __name__ == "__main__":
    raw = sys.stdin.read()
    parse_raw.delay(raw)
