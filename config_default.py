# configure it for your mysql database
# your_username: instead 'flap'
# your_server: instead 'localhost'
# your_database: instead 'traps'
DB_URL = 'mysql+pymysql://flap:flapmyport@localhost/traps'
MAIL_FROM = 'trap_harvester@yourdomain.com'
MAIL_TO = ['user_first@yourdomain.com','user_second@yourdomain.com']

# it's neede for getting description of interface and hostname of device
SNMP_COMMUNITY = 'your_SNMP_community'

# flapping interface flaps more then FLAP_THR_COUNT in the last FLAP_THR_MINUTES
FLAP_THR_MINUTES = 15
FLAP_THR_COUNT = 20

# set it to True for receiving mails in Russian
TRANSLATE = False 
