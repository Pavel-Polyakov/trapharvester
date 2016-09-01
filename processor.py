__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.5"

import re
import time
from models import Port
from functions import getSnmp, parseTrap

class Processor(object):
    def work(self, data):
        trap = parseTrap(data)
        oid = trap.get('snmpTrapOID.0', None)
	if oid in ['IF-MIB::linkUp','IF-MIB::linkDown']:
            processor = PortProcessor()
            return processor.job(trap)
        else:
            return None

def find_state(message):
    try:
        return re.search('(up|down)',message,re.IGNORECASE).group().lower()
    except AttributeError:
        return None

class PortProcessor(object):
    """
    Return Trap object.

    Trap example:
    UDP: [192.168.168.222]:59010->[192.168.168.100]:162
    UDP: [192.168.168.222]:59010->[192.168.168.100]:162
    DISMAN-EVENT-MIB::sysUpTimeInstance 5:5:34:58.39
    SNMPv2-MIB::snmpTrapOID.0 IF-MIB::linkUp
    IF-MIB::ifIndex.567 567
    IF-MIB::ifAdminStatus.567 1
    IF-MIB::ifOperStatus.567 1
    IF-MIB::ifName.567 ge-0/0/21.0"""

    def job(self, trap):
        host = trap['host']
        hostname = getSnmp(host, 'SNMPv2-MIB::sysName.0')
        event = trap['snmpTrapOID.0']
        ifIndex = trap.get('ifIndex')
        ifName = trap.get('ifName', getSnmp(host,'IF-MIB::ifName.'+ifIndex))
        ifAlias = trap.get('ifAlias', getSnmp(host,'IF-MIB::ifAlias.'+ifIndex))
        
        ifAdminStatus = trap.get('ifAdminStatus', getSnmp(host,'IF-MIB::ifAdminStatus.'+ifIndex))
        ifAdminStatus = find_state(ifAdminStatus)
        ifOperStatus = trap.get('ifOperStatus', getSnmp(host,'IF-MIB::ifOperStatus.'+ifIndex))
        ifOperStatus = find_state(ifOperStatus)
        if ifAdminStatus or ifOperStatus:
            return Port(
                    host = host,
                    hostname = hostname,
                    event = event,
                    ifIndex = ifIndex,
                    ifName = ifName,
                    ifAlias = ifAlias,
                    ifAdminStatus = ifAdminStatus,
                    ifOperStatus = ifOperStatus)
        else:
            return None
