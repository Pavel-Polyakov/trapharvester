# -*- coding: utf-8 -*-
# mail_template_trap = u"""<h4><span class="label label-{mood}">{event}</span>
# 			 <span class="label label-primary">{hostname}</span>
# 			 <span class="label label-primary">{port} ({description})</span>
# 			 <span class="label label-info">{time}</span></h4>"""
mail_template_trap = u"""<span class="label label-{mood}">{event}</span><white> | </white>
			 <span class="label label-primary">{hostname}</span><white> : </white>
			 <span class="label label-primary">{port} ({description})</span><white> | </white>
			 <span class="label label-info">{time}</span><br>"""
mail_template_full = u"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
  </head>
  <style>
  {style}
  </style>
  <body>
    <div>
      {traps}
    </div>
  </body>
</html>"""

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
    background-color: #337ab7;
}
.label-success {
    background-color: #5cb85c;
}
.label-ok {
    background-color: #5cb85c;
}
.label-problem {
    background-color: #d9534f;
}
.label-neutral {
    background-color: #5bc0de;
}
.label-info {
    background-color: #5bc0de;
}
.label-danger {
    background-color: #d9534f;
}
.label {
    display: inline;
    padding: .2em .6em .3em;
    line-height: 2;
    color: #fff;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: .25em;
}
.small {
    font-size: 85%;
}"""

