__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.3"

from sqlalchemy import Column, Integer, String, DateTime
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

class BasePort(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    time = Column(DateTime(timezone=True), default=func.now())
    host = Column(String(255))
    ifIndex = Column(String(255))

    def _get_session(self):
        return Session.object_session(self)

    def is_blocked(self):
        b = self._get_session().query(BlackPort).\
                    filter(BlackPort.host == self.host).\
                    filter(BlackPort.ifIndex == self.ifIndex).first()
        return bool(b)

    def is_flapping(self):
        minutes = FLAP_THR_MINUTES
        threshold = FLAP_THR_COUNT
        count = self._get_session().query(Port).\
                    filter(Port.host == self.host).\
                    filter(Port.ifIndex == self.ifIndex).\
                    filter(Port.time > self.time - timedelta(minutes=minutes)).count()
        return count > threshold

    def is_flapping_now(self):
        minutes = FLAP_THR_MINUTES
        threshold = FLAP_THR_COUNT
        before = func.now() - timedelta(minutes=minutes)
        count = self._get_session().query(Port).\
                    filter(Port.host == self.host).\
                    filter(Port.ifIndex == self.ifIndex).\
                    filter(Port.time > before).count()
        return count > threshold

    def block(self):
        b = BlackPort(host = self.host, ifIndex = self.ifIndex)
        self._get_session().add(b)
        self._get_session().commit()

    def unblock(self):
        self._get_session().query(BlackPort).\
                    filter(BlackPort.host == self.host).\
                    filter(BlackPort.ifIndex == self.ifIndex).delete()
        self._get_session().commit()

    def is_last(self):
        traps = self.getcircuit()
        if len(traps) == 1:
            return True
        else:
            return bool(self is traps[-1])

    def getcircuit(self):
        traps = self._get_session().query(Port).\
                    filter(Port.host == self.host).\
                    filter(Port.time > self.time - timedelta(seconds=30)).all()
        return traps

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

class BlackPort(BasePort):
    __tablename__ = "blacklist"

    def __repr__(self):
        template = "BlackPort. {host}: {ifindex}"
        return template.format(host = self.host,ifindex = self.ifIndex)
