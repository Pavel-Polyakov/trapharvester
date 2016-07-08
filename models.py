from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta

def connect_db(db_url='mysql+pymysql://trap:0o9i8u@localhost/traps', do_echo=False):
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

    def is_blocked(self, session):
        b = session.query(BlackPort).\
                    filter(BlackPort.host == self.host).\
                    filter(BlackPort.ifIndex == self.ifIndex).first()
        return bool(b)

    def is_flapping(self, session):
        minutes = 10
        threshold = 4
        count = session.query(Port).\
                    filter(Port.host == self.host).\
                    filter(Port.ifIndex == self.ifIndex).\
                    filter(Port.time > datetime.now() - timedelta(minutes=minutes)).count()
        return count > threshold

    def block(self, session):
        b = BlackPort(host = self.host, ifIndex = self.ifIndex)
        session.add(b)
        session.commit()

    def unblock(self, session):
        session.query(BlackPort).\
                    filter(BlackPort.host == self.host).\
                    filter(BlackPort.ifIndex == self.ifIndex).delete()
        session.commit()

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
    def for_mail(self):
        template = "{mood}: {hostname} {ifname} ({ifalias}) {event}"
        if 'Up' in self.event:
            mood = 'OK'
        elif 'Down' in self.event:
            mood = 'PROBLEM'
        else:
            mood = 'Something'
        text = template.format(mood = mood,
                    hostname = self.host if self.hostname is None else self.hostname,
                    ifname = self.ifName,
                    ifalias = self.ifAlias,
                    event = self.event.replace('IF-MIB::',''))
        return text


class BlackPort(BasePort):
    __tablename__ = "blacklist"

    def __repr__(self):
        template = "BlackPort. {host}: {ifindex}"
        return template.format(host = self.host,ifindex = self.ifIndex)
