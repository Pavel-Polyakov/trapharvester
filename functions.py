from subprocess import check_output, CalledProcessError
import re

from config import SNMP_COMMUNITY

def getSnmp(host,oid):
    if host is not None:
        try:
            raw = check_output(["snmpget", "-v2c", "-c"+SNMP_COMMUNITY, host, oid])
            return re.sub('^.*STRING: ','',raw).strip()
        except CalledProcessError:
            return None
    else:
        return None

def parseTrap(data):
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

