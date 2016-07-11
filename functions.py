__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.3"

from subprocess import check_output, CalledProcessError
import re

from html_templates import mail_template_trap, mail_template_full, mail_template_style, mail_template_list
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

def for_html_trap_list(traps):
    if len(traps) > 0:
        text_list = ''
        hosts = set([(x.host,x.hostname) for x in traps])
        for host in hosts:
            ports = [x.for_html() for x in traps if x.host == host[0]]
            text_ports = ''.join(ports)
            text_list += mail_template_list.format(host=host[0],hostname=host[1],traps=text_ports)
        return mail_template_full.format(text_list=text_list,style=mail_template_style)

def for_html_title(traps):
    if len(traps) > 1:
        text_hosts = []
        hosts = set([(x.host,x.hostname) for x in traps])
        for host in hosts:
            host_text = host[1] if host[1] else host[0]
            
            host_traps = [x for x in traps if x.host == host[0]]
            host_events = [x.event for x in host_traps]
            
            events_pre = []
            for event in set(host_events):
                count = len([x for x in host_traps if x.event == event])
                event_text = "{event}: {count}".format(event=event, count=count)
                events_pre.append(event_text)
            events_text = ', '.join(events_pre)
            
            text_hosts.append("{host} ({events})".format(host=host_text,events=events_text))
        return 'trap_handler. '+', '.join(text_hosts)
    if len(traps) == 1:
        trap = traps[0]
        return 'trap_handler. {host}: {port} ({alias}) {event}'.format(
                        host=trap.hostname if trap.hostname else trap.host,
                        port=trap.ifName,
                        alias=trap.ifAlias if trap.ifAlias else 'NO DESCRIPTION',
                        event=trap.event)
    else:
        return 'trap_handler. Something went wrong'
