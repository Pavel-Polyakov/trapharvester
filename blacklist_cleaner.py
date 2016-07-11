#!/usr/bin/python
__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.3"

import sys
from models import connect_db, BlackPort, Port
from mailer import send_mail
from config import MAIL_TO
from html_templates import mail_template_trap, mail_template_full, mail_template_style, mail_template_list

if __name__ == "__main__":
    s,e = connect_db()
    blackports = s.query(BlackPort).all()
    ports = [s.query(Port).\
                filter(Port.host == x.host).\
                filter(Port.ifIndex == x.ifIndex).\
                order_by(Port.id.desc()).first() for x in blackports]

    if len(ports) > 0:
        # whitelist = [x for x in ports if not x.is_flapping(s)]
        whitelist = [x for x in ports if not x.is_flapping(s)]
        blacklist = [x for x in ports if x not in whitelist]
        for p in whitelist:
            p.unblock(s)
        for p in whitelist:
            p.event = 'Stopped Flapping'
        for p in blacklist:
            p.event = 'Still Flapping'

        text_list = ''
        hosts = set([(x.host,x.hostname) for x in whitelist+blacklist])
        for host in hosts:
            ports = [x.for_html() for x in whitelist+blacklist if x.host == host[0]]
            text_ports = ''.join(ports)
            text_list += mail_template_list.format(host=host[0],hostname=host[1],traps=text_ports)

	text_title = 'trap_handler. '+', '.join([x[1] for x in hosts])
        text_main = mail_template_full.format(text_list=text_list,style=mail_template_style)
        send_mail(text_title, MAIL_TO, text_main)
