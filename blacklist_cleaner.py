#!/usr/bin/python
__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.3"

import sys
from models import connect_db, BlackPort, Port
from mailer import send_mail
from config import MAIL_TO
from functions import for_html_trap_list, for_html_title

if __name__ == "__main__":
    s,e = connect_db()
    blackports = s.query(BlackPort).all()
    ports = [s.query(Port).\
                filter(Port.host == x.host).\
                filter(Port.ifIndex == x.ifIndex).\
                order_by(Port.id.desc()).first() for x in blackports]

    if len(ports) > 0:
        whitelist = [x for x in ports if not x.is_flapping_now()]
        for p in whitelist:
            p.unblock()
            p.additional = 'Stop Flapping'
        for p in [x for x in ports if x not in whitelist]:
            p.additional = 'Still Flapping'
        text_main = for_html_trap_list(ports)
        text_title = for_html_title(ports)
        send_mail(text_title, MAIL_TO, text_main)
