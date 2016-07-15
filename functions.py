__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.3"

from subprocess import check_output, CalledProcessError
import re

from html_templates import mail_template_full, mail_template_style, template_host, template_port, template_port_additional, template_event, template_port_still_flapping, template_port_stop_flapping
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
        text_hosts = ''
        hosts = set([(x.host,x.hostname) for x in traps])
        for host in hosts:
            host_traps = [x for x in traps if x.host == host[0]]
            text_hosts += for_html_host(host_traps)
        return mail_template_full.format(text_hosts=text_hosts,style=mail_template_style)

def for_html_host(traps):
    if len(traps) > 0:
        trap = traps[-1]
        hostip = trap.host
        hostname = trap.hostname
        ports = set([x.ifName for x in traps])
        ports_text = ''
        for port in ports:
            port_traps = [x for x in traps if x.ifName == port]
            ports_text += for_html_port(port_traps)
        host_text = template_host.format(hostname=hostname,hostip=hostip,ports=ports_text)
        return host_text

def for_html_port(traps):
    if len(traps) > 0:
        trap = traps[-1]
        name = trap.ifName
        description = trap.ifAlias if trap.ifAlias not in (None,'') else 'NO DESCRIPTION'
        additional = get_additional(trap)
        mood = get_mood(additional)
	if additional == 'Still Flapping':
	    return template_port_still_flapping.format(name=name,description=description,mood=mood,additional=additional)
	elif additional == 'Stop Flapping':
	    return template_port_stop_flapping.format(name=name,description=description,mood=mood,additional=additional,event=for_html_event(trap))
        events = ''
        for trap in traps:
            events += for_html_event(trap)
        template = template_port_additional if additional else template_port
        text_port = template.format(name=name,description=description,mood=mood,additional=additional,events=events)
        return text_port

def get_additional(trap):
    if hasattr(trap, 'additional'):
        return trap.additional
    else:
        additional = None
        if trap.is_flapping():
            additional = 'Flapping'
            if trap.is_blocked():
                additional = 'Blocked'
            return additional

def for_html_event(trap):
    time = trap.time
    event = clean_event(trap.event)
    mood = get_mood(event)
    text_event = template_event.format(time=time,mood=mood,event=event)
    return text_event

def clean_event(event):
    return event.replace('IF-MIB::link','')

def get_mood(event):
    if event is not None:
        if 'Up' in event:
            mood = 'Ok'
        elif 'Down' in event:
            mood = 'Problem'
        elif event in ['Flapping','Still Flapping', 'Blocked']:
            mood = 'Problem'
        elif event in ['Stop Flapping']:
            mood = 'Ok'
        else:
            mood = 'Neutral'
        return mood
    else:
        return None

def get_additional_or_event(trap):
    result = get_additional(trap)
    if result is None:
	result = trap.event
    return result

def for_html_title(traps):
    if len(set([(x.ifName,x.host) for x in traps])) == 1:
        trap = traps[0]
        additional = get_additional(trap)
        if additional is None:
            if len(traps) > 1:
                event = clean_event(traps[0].event+traps[-1].event)+' ({})'.format(len(traps))
            else:
                event = trap.event.replace('IF-MIB::link','')
        else:
            event = additional
        host = trap.hostname if trap.hostname else trap.host
        description = trap.ifAlias if trap.ifAlias else 'NO DESCRIPTION'
        return 'Harvey. {host}: {port} ({description}) {event}'.format(
                                                                    host=host,
                                                                    port=trap.ifName,
                                                                    description=description,
                                                                    event=event)
    if len(traps) > 1:
        for trap in traps:
            trap.event = trap.event.replace('IF-MIB::link','')

        text_hosts = []
        hosts = set([(x.host,x.hostname) for x in traps])
	
	additionals = set([get_additional_or_event(x) for x in traps])
	if len(additionals) == 1:
	    return 'Harvey. '+', '.join([x[1] if x[1] else x[0] for x in hosts])+': '+additionals.pop()
        for host in hosts:
            host_text = host[1] if host[1] else host[0]

            host_traps = [x for x in traps if x.host == host[0]]
            host_events = [get_additional(x) for x in host_traps]

            events_pre = []
            for event in set(host_events):
                count = len([x for x in host_events if x == event])
                event_text = "{event}: {count}".format(event=event, count=count)
                events_pre.append(event_text)
            events_text = ', '.join(events_pre)

            text_hosts.append("{host} ({events})".format(host=host_text,events=events_text))
        return 'Harvey. '+', '.join(text_hosts)
