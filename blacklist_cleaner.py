#!/usr/bin/python
__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.5"

import sys
from models import connect_db, BlackPort, Port
from mailer import send_mail
from config import MAIL_TO
from functions import for_html_trap_list, for_html_title

if __name__ == "__main__":
    s,e = connect_db()
    blackports = s.query(BlackPort).filter(BlackPort.added == 'auto').all()
    ports_raw = [s.query(Port).\
                filter(Port.host == x.host).\
                filter(Port.ifIndex == x.ifIndex).\
                order_by(Port.id.desc()).first() for x in blackports]

    if len(ports_raw) > 0:
        hosts = set([x.host for x in ports_raw])
        for host in hosts:
            ports = [x for x in ports_raw if x.host == host]
            whitelist = [x for x in ports if not x.is_flapping_now()]
            for p in whitelist:
                p.unblock()
                p.additional = 'Stop Flapping'
            for p in [x for x in ports if x not in whitelist]:
                p.additional = 'Still Flapping'
            for p in ports:
                cir = p.getcircuit()
                for c in cir:
                    c.del_from_queue()
            text_main = for_html_trap_list(ports)
            text_title = for_html_title(ports)
            send_mail(text_title, MAIL_TO, text_main)
