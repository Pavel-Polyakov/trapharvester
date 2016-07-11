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
from html_templates import mail_template_trap, mail_template_full, mail_template_style, mail_template_list

# logging.basicConfig(format = u'[%(asctime)s] %(message)s', level = logging.INFO, filename = u'/var/log/trap_handler.log')
# formatter = logging.Formatter('%(asctime)s - %(message)s')

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
		    text_list = ''
                    trap.event = 'Flapping'
		    hosts = set([(x.host,x.hostname) for x in [trap]])
		    for host in hosts:
			ports = [x.for_html() for x in [trap] if x.host == host[0]]
			text_ports = ''.join(ports)
			text_list += mail_template_list.format(host=host[0],hostname=host[1],traps=text_ports)
		    text_title = 'trap_handler. {host}: {port} ({alias}) {event}'.format(
							host=trap.hostname if trap.hostname else trap.host,
							port=trap.ifName,
							alias=trap.ifAlias if trap.ifAlias else 'NO DESCRIPTION',
							event=trap.event)
		    text_main = mail_template_full.format(text_list=text_list,style=mail_template_style)
		    send_mail(text_title, MAIL_TO, text_main)
		    logging.info(text_title)
		else:
                    trap.event = trap.event.replace('IF-MIB::link','')
                    text_list = ''
                    hosts = set([(x.host,x.hostname) for x in [trap]])
                    for host in hosts:
                        ports = [x.for_html() for x in [trap] if x.host == host[0]]
                        text_ports = ''.join(ports)
                        text_list += mail_template_list.format(host=host[0],hostname=host[1],traps=text_ports)
                    text_title = 'trap_handler. {host}: {port} ({alias}) {event}'.format(
                                                        host=trap.hostname if trap.hostname else trap.host,
                                                        port=trap.ifName,
                                                        alias=trap.ifAlias if trap.ifAlias else 'NO DESCRIPTION',
                                                        event=trap.event)
                    text_main = mail_template_full.format(text_list=text_list,style=mail_template_style)
                    send_mail(text_title, MAIL_TO, text_main)
                    logging.info(text_title)
    else:
	logging.info("I don't know how to deal with it:\n\n"+raw)
