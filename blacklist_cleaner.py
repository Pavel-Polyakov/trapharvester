#!/usr/bin/python
__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.3"

import sys
from models import connect_db, BlackPort, Port
from mailer import send_mail
from config import MAIL_TO

if __name__ == "__main__":
    s,e = connect_db()
    blackports = s.query(BlackPort).all()
    ports = [s.query(Port).filter(Port.host == x.host).filter(Port.ifIndex == x.ifIndex).order_by(Port.id.desc()).first() for x in blackports]
    if len(ports) > 0:
        whitelist = [x for x in ports if not x.is_flapping(s)]
        blacklist = [x for x in ports if x not in whitelist]
        for w in whitelist:
            w.unblock(s)
        text = ''
        
        if len(blacklist) > 0:
            text += "\nStill flapping: "+', '.join(['('+str(x)+')' for x in blacklist])
        if len(whitelist) > 0:
            text += "\nCleared: "+', '.join(['('+str(x)+')' for x in whitelist])
        
        send_mail('About blacklist', MAIL_TO, text)
