#!/usr/bin/python
__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.3"

import sys
from models import connect_db, BlackPort, Port
from mailer import send_mail
from config import MAIL_TO
from html_templates import mail_template_trap, mail_template_full, mail_template_style

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
        for w in whitelist:
            w.unblock(s)
        text_traps = ''
        text_title = ''
        if len(blacklist) > 0:
            text_title += 'Still flapping: '.upper()+', '.join([x.ifAlias if x.ifAlias is not None else x.ifName for x in blacklist])+' '
            text_traps += ''.join([x.for_html(event='Still flapping'.upper(),mood='problem') for x in blacklist])
        if len(whitelist) > 0:
            text_title += 'Stopped flapping: '.upper()+', '.join([x.ifAlias if x.ifAlias is not None else x.ifName for x in whitelist])+' '
            text_traps += ''.join([x.for_html(event='Stop flapping'.upper(),mood='ok') for x in whitelist])

        text_main = mail_template_full.format(traps=text_traps,style=mail_template_style)
        send_mail(text_title, MAIL_TO, text_main)
