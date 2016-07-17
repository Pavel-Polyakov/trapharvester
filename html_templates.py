# -*- coding: utf-8 -*-
template_host = u"""
<h3>{hostname} ({hostip})</h3>
<ul>
    {ports}
</ul>
"""

template_port_still_flapping = u"""
<li><b>{name} {description}</b><white> | </white><span class="label label-{mood}">{additional}</span></li>"""

template_port_stop_flapping = u"""
<li><b>{name} {description}</b><white> | </white><span class="label label-{mood}">{additional}</span>
    <ul>
	<b>Last:</b>{event}
    </ul>
</li>"""

template_port_additional = u"""
<li><b>{name} {description}</b><white> | </white><span class="label label-{mood}">{additional}</span>
    <ul>
        {events}
    </ul>
</li>"""

template_port = u"""
<li><b>{name} {description}</b>
    <ul>
        {events}
    </ul>
</li>"""

template_event = u"""
<li>
    {time}<white> | </white><span class="label label-{mood}">{event}</span>
</li>
"""

mail_template_full = u"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
  </head>
  <style>
  {style}
  </style>
  <body>
    <div>
    {text_hosts}
    </div>
  </body>
</html>
"""

mail_template_style = u"""
body {
    font-family: "Helvetica Neue",Helvetica,Arial,sans-serif;
    font-size: 14px;
    color: #333;
    background-color: #fff;
}
white {
    color: white;
    font-size: 2px;
}
h3 {
    font-size: 24px;
}
.label-primary {
    background-color: #036ec9;
}
.label-success {
    background-color: #5cb85c;
}
.label-primary2 {
    background-color: #0e2948;
}
.label-ok {
    background-color: #5cb85c;
}
.label-problem {
    background-color: #d9534f;
}
.label-neutral {
    background-color: #94afab;
}
.label-info {
    background-color: #afb2b7;
}
.label-danger {
    background-color: #d9534f;
}
.label {
    display: inline;
    padding: .2em .6em .3em;
    line-height: 2;
    text-size: 80%;
    color: #fff;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: .25em;
}
.small {
    font-size: 85%;
}"""

mail_template_trap_image = u"""
<table><tbody>
<tr><td>
<span class="label label-{mood}">{event}</span><white> | </white>
<span class="label label-primary2">{hostname}</span><white> : </white>
<span class="label label-primary">{port} ({description})</span><white> | </white>
<span class="label label-{opermood}">{time}</span>
</td></tr>
<tr><td>
<img style="display:block;" width="100%" height="100%" src='http://isweethome.ihome.ru/api/?ifindex={ifindex}&flapchart'>
</td></tr>
</tbody></table>"""
