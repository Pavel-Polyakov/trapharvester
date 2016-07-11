# TrapHarvester #

### What is it? ###

* The system for handle SNMP-traps and sending combined notifications.
* Version 0.3

### How do I get set up? ###

* Download and install snmptrapd
* Edit config.py for your mysql database settings
* Add the next row in /etc/snmp/snmptrapd.conf: "traphandle default ${PATH}/trap_handler.sh"