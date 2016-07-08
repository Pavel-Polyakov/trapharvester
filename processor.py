import re
import time
from models import Link
from functions import getSnmp


class Processor(object):
    def work(self, data):
        trap = self._parse(data)
        type_ = trap.get('snmpTrapOID.0', None)
        if self.type_ in ['IF-MIB::linkUp','IF-MIB::linkDown']
            processor = LinkProcessor()
            return processor.job(trap)
        else:
            return None

    def _parse(data):
        """return dict with parsed trap"""
        res = {}
        data = data.split('\n')
        # common info for any trap
        host, server = re.findall('\[(.*?)\]', data[0])
        # specific info is only after second line
        # slice each row for 2 parts: header and value
        pre = [re.split(':\s*?:',x,1)[-1] for x in data[2:] if x != '']
        tuples = [tuple(re.split('\s',x,1)) for x in pre]
        headers = [re.sub('\[.*?\]','',x[0]) for x in tuples]
        values = [x[-1] for x in tuples]
        # merge it to dict
        res = dict(zip(headers,values))
        res['host'] = host
        res['server'] = server
        return res

class LinkProcessor(object):
    """Trap example:
    UDP: [192.168.168.222]:59010->[85.112.112.25]:162
    UDP: [192.168.168.222]:59010->[85.112.112.25]:162
    DISMAN-EVENT-MIB::sysUpTimeInstance 5:5:34:58.39
    SNMPv2-MIB::snmpTrapOID.0 IF-MIB::linkUp
    IF-MIB::ifIndex.567 567
    IF-MIB::ifAdminStatus.567 1
    IF-MIB::ifOperStatus.567 1
    IF-MIB::ifName.567 ge-0/0/21.0"""

    def job(self, trap):
        time = time.time()
        host = trap['host']
        hostname = getSnmp(host, 'SNMPv2-MIB::sysName.0')
        event = trap['snmpTrapOID.0']
        ifIndex = trap.get('ifIndex')
        ifName = trap.get('ifName', getSnmp(host,'IF-MIB::ifName.'+ifIndex))
        ifAlias = trap.get('ifAlias', getSnmp(host,'IF-MIB::ifAlias.'+ifIndex))

        return Link(time = timestamp,
                    host = host,
                    hostname = hostname,
                    event = event,
                    ifIndex = ifIndex,
                    ifName = ifName,
                    ifAlias = ifAlias)
