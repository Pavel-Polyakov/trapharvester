__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.6"

from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from config import DB_URL, FLAP_THR_MINUTES, FLAP_THR_COUNT

from sqlalchemy.orm.session import Session

def connect_db(db_url=DB_URL, do_echo=False):
    engine = create_engine(db_url, echo=do_echo)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    return (Session(), engine)

Base = declarative_base()
metadata = Base.metadata

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    trap_id = Column(Integer)
    host = Column(String(255))

class BasePort(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    time = Column(DateTime(timezone=True), default=func.now())
    host = Column(String(255))
    ifIndex = Column(String(255))

    def _get_session(self):
        return Session.object_session(self)

    def save(self):
        self._get_session().add(self)
        self._get_session().commit()

class Port(BasePort):
    __tablename__ = "ports"

    hostname = Column(String(255))
    event = Column(String(255))
    ifName = Column(String(255))
    ifAlias = Column(String(255))
    ifAdminStatus = Column(String(255))
    ifOperStatus = Column(String(255))

    def __repr__(self):
        template = "Port Trap. {host}: {ifname} ({ifalias})"
        return template.format(host = self.hostname,
                    ifname = self.ifName,
                    ifalias = self.ifAlias)

    def is_blocked(self,s):
        b = s.query(BlackPort).\
                    filter(BlackPort.host == self.host).\
                    filter(BlackPort.ifIndex == self.ifIndex).first()
        return bool(b)

    def is_flapping(self,s):
        minutes = FLAP_THR_MINUTES
        threshold = FLAP_THR_COUNT
        count = s.query(Port).\
                    filter(Port.host == self.host).\
                    filter(Port.ifIndex == self.ifIndex).\
                    filter(Port.time > self.time - timedelta(minutes=minutes)).count()
        return count > threshold

    def is_flapping_now(self,s):
        minutes = FLAP_THR_MINUTES
        threshold = FLAP_THR_COUNT
        before = func.now() - timedelta(minutes=minutes)
        count = s.query(Port).\
                    filter(Port.host == self.host).\
                    filter(Port.ifIndex == self.ifIndex).\
                    filter(Port.time > before).count()
        return count > threshold

    def block(self,s):
        b = BlackPort(host = self.host, ifIndex = self.ifIndex, added='auto')
        s.add(b)
        s.commit()

    def unblock(self,s):
        s.query(BlackPort).\
                    filter(BlackPort.host == self.host).\
                    filter(BlackPort.ifIndex == self.ifIndex).delete()
        s.commit()

    def get_tasks(self,s):
        tasks = s.query(Task).filter(Task.host==self.host).all()
	tasks_ids = [x.trap_id for x in tasks]
        return tasks_ids

    def is_last(self,s):
        tasks = s.query(Task).filter(Task.host==self.host).all()
	if not tasks:
	    return True
	tasks_ids = [x.trap_id for x in tasks]
	if len(tasks) > 0:
            return self.id == tasks_ids[-1]
        else:
            return False

    def add_to_queue(self,s):
        s.add(Task(trap_id=self.id,host=self.host))
        s.commit()

    def del_from_queue(self,s):
        s.query(Task).filter(Task.trap_id == self.id).delete()
        s.commit()

    def getcircuit(self,s):
        queue = s.query(Task).filter(Task.host==self.host).all()
        queue_ids = [x.trap_id for x in queue]
        queue_traps = s.query(Port).filter(Port.id.in_([x for x in queue_ids])).all()
        return queue_traps

class BlackPort(BasePort):
    __tablename__ = "blacklist"

    added = Column(Enum('auto','manual'))

    def __repr__(self):
        template = "BlackPort. {host}: {ifindex}"
        return template.format(host = self.host,ifindex = self.ifIndex)
