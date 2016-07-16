# -*- coding: utf-8 -*-
__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.4"

from subprocess import check_output, CalledProcessError
import re

from collections import Counter
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
                additional = 'Blocked for flapping'
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
        elif event in ['Flapping','Still Flapping', 'Blocked', 'Blocked for flapping']:
            mood = 'Problem'
        elif event in ['Stop Flapping']:
            mood = 'Ok'
        else:
            mood = 'Neutral'
        return mood
    else:
        return None


def for_html_title(traps):
    if len(traps) == 1:
        """single trap"""
        return for_html_title_one_trap(traps[0])
    if len(set([(x.ifName,x.host) for x in traps])) == 1:
        """single port"""
        return for_html_title_one_port(traps)
    if len(set([x.host for x in traps])) == 1:
        """single host"""
        return for_html_title_one_host(traps)
    else:
        return 'Harvey. TRAPS'

def get_hostname(trap):
    return trap.hostname if trap.hostname else trap.host

def get_description(trap):
    return trap.ifAlias if trap.ifAlias else 'NO DESCRIPTION'

def for_html_title_one_trap(trap):
    template = u'Harvey. {host}: {port} ({description}) {event}'

    host = get_hostname(trap)
    description = get_description(trap)

    # event variable
    event = get_event_for_one_port([trap])
    event = translate_one(event)

    return template.format(host=host,
                           port=trap.ifName,
                           description=description,
                           event=event)

def get_event_for_one_port(traps):
    # event variable
    trap = traps[0]
    additional = get_additional(trap)
    if additional == 'Stop Flapping':
        last_event = traps[-1].event
        event = '{} and {}'.format(additional,clean_event(traps[-1].event))
    elif additional is not None:
        event = additional
    else:
        first = clean_event(traps[0].event)
        last = clean_event(traps[-1].event)
        if first == last:
            event = (first)
        else:
            event = '{} and {}'.format(first,last)
    return event

def for_html_title_one_port(traps):
    template = u'Harvey. {host}: {port} ({description}) {event}'
    trap = traps[0]
    host = get_hostname(trap)
    description = get_description(trap)
    event = get_event_for_one_port(traps)
    event = translate_one(event)
    return template.format(host=host,
                           port=trap.ifName,
                           description=description,
                           event=event)

def for_html_title_one_host(traps):
    template = u'Harvey. {host}: {events}'
    template_event = u'{count} {noun} {event}'
    trap = traps[0]

    host = get_hostname(trap)
    description = get_description(trap)

    # events
    events_list = []
    ports = set([x.ifName for x in traps])
    for port in ports:
        port_traps = [x for x in traps if x.ifName == port]
        port_event = get_event_for_one_port(port_traps)
        events_list.append(port_event)

    events_count = Counter(events_list)
    events = []
    for event in events_count:
        count = events_count[event]
        if count == 1:
            events.append(template_event.format(count=u'1',
                                                noun=u'порт',
                                                event=translate_one(event)).lower())
        else:
            events.append(template_event.format(count=str(count),
                                                noun=translate_ports(count),
                                                event=translate_many(event)).lower())
    events_text = ', '.join(events)
    return template.format(host=host,
                           port=trap.ifName,
                           description=description,
                           events=events_text)

def translate_ports(count):
    variants = {
        '0': u'портов',
        '1': u'порт',
        '2': u'порта',
        '3': u'порта',
        '4': u'порта',
        '5': u'портов',
        '6': u'портов',
        '7': u'портов',
        '8': u'портов',
        '9': u'портов',
    }
    w = str(count)[-1]
    return variants.get(w, 'порт')

def translate_one(event):
    variants = {
        'still flapping': u'Всё ещё флапает',
        'stop flapping': u'Прекратил флапать',
        'stop flapping and down': u'Прекратил флапать и лежит',
        'stop flapping and up': u'Прекратил флапать и поднят',
        'blocked for flapping': u'Заблокирован из-за флапов',
        'down': u'Упал',
        'up': u'Поднялся',
        'down and up': u'Упал и Поднялся',
        'up and down': u'Поднялся и Упал',
    }
    return variants.get(event.lower(), event)

def translate_many(event):
    variants = {
        'still flapping': u'Всё ещё флапают',
        'stop flapping': u'Прекратили флапать',
        'stop flapping and down': u'Прекратили флапать и лежат',
        'stop flapping and up': u'Прекратили флапать и подняты',
        'blocked for flapping': u'Заблокированы из-за флапов',
        'down': u'Упали',
        'up': u'Поднялись',
        'down and up': u'Упали и Поднялись',
        'up and down': u'Поднялись и Упали',
    }
    return variants.get(event.lower(), event)
