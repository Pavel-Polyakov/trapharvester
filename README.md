# TrapHarvester #

### What is it? ###

* The system for handle SNMP-traps and sending combined notifications.
* Version 0.5

<h1> How do I can deploy it on my network? </h1>
  <ol>
    <li>
      <h2>Install needed packages</h2>
        <pre>
yum -y install net-snmp net-snmp-utils
yum -y install mysql
yum -y install epel-release
yum -y install -y python-pip
pip install sqlalchemy
pip install pymysql
        </pre>
    </li>
    <li>
      <h2>Configure mySQL</h2>
      <ul>
      <li>
      <h3>login to mysql</h3>
      <pre>
$ mysql
      </pre>
      </li>
      <li>
      <h3>create database</h3>
      <pre>
create database traps;
      </pre>
      </li>
      <li>
      <h3>create user</h3>
      <pre>
CREATE USER 'flap'@'localhost' IDENTIFIED BY 'flapmyport';
GRANT ALL PRIVILEGES ON * . traps TO 'flap'@'localhost';
GRANT ALL PRIVILEGES ON `traps`.* TO `flap`@`localhost`;
FLUSH PRIVILEGES;
      </pre>
      </li>
    </ul>
    </li>
    <li>
      <h2>Configure snmptrapd</h2>
      <ul>
        <li>
        <h3>Edit /etc/snmp/snmptrapd.conf</h3>
          <pre>
disableAuthorization yes
sqlMaxQueue 10
sqlSaveInterval 0
outputOption X
traphandle default /usr/local/src/trapharvester/trap_handler.py
          </pre>
        </li>
        <li>
        <h3>and start snmtrapd</h3>
          <pre>
sudo snmptrapd -fnLo &
          </pre>
        </li>
        </ul>
    </li>
    <li>
      <h2>Configure trap harvester</h2>
      <ul>
      <li>
        <h3>Clone this repo to <b>/usr/local/src/trapharvester/</b></h3>
          <pre>
cd /usr/local/src
git clone http://github.com/Pavel-Polyakov/trapharvester.git
cd trapharvester
          </pre>
       </li>
       <li>
        <h3>Rename <b>config_default.py</b> to <b>config.py</b></h3>
          <pre>
mv config_default.py config.py
          </pre>
        </li>
        <li>
<h3>Edit <b>config.py</b> with your favorite text editor</h3>
configure it for your mysql database
your_username: instead 'flap'
your_server: instead 'localhost'
your_database: instead 'traps'
<pre>
DB_URL = 'mysql+pymysql://flap:flapmyport@localhost/traps'
</pre>
Change <b>from</b> and <b>to</b> mail-adresses
<pre>
MAIL_FROM = 'trap_harvester@yourdomain.com'
MAIL_TO = ['user_first@yourdomain.com','user_second@yourdomain.com']
</pre>
Configure SNMP_COMMUNITY — it's needed for getting description of interface and hostname of device
<pre>
SNMP_COMMUNITY = 'your_SNMP_community'
</pre>
This parameter change only if you understand what you do

<i>Flapping interface</i> flaps more then <b>FLAP_THR_COUNT</b> in the last <b>FLAP_THR_MINUTES</b>
<pre>
FLAP_THR_MINUTES = 15
FLAP_THR_COUNT = 20
</pre>
Set this variable to <b>True</b> for receive mails in Russian
<pre>
TRANSLATE = False
</pre>
</li>
</ul>
</ol>
