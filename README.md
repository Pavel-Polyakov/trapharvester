# TrapHarvester #

### What is it? ###

* The system for handle SNMP-traps and sending combined notifications.
* Version 0.3

### How do I get set up? ###

1 Download and install snmptrapd
2 Edit config.py for your mysql database settings
3 Add the next row in /etc/snmp/snmptrapd.conf: "traphandle default ${PATH}/trap_handler.sh"