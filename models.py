from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

def connect_db(db_url='mysql+pymysql://trap:0o9i8u@localhost/traps', do_echo=False):
    engine = create_engine(db_url, echo=do_echo)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    return (Session(), engine)

Base = declarative_base()
metadata = Base.metadata

class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True)
    time = Column(String(255))
    host = Column(String(255))
    hostname = Column(String(255))
    event = Column(String(255))
    ifIndex = Column(String(255))
    ifName = Column(String(255))
    ifAlias = Column(String(255))
    ifAdminStatus = Column(String(255))
    ifOperStatus = Column(String(255))

    def __repr__(self):
        return "Port Trap. {host}: {ifname} ({ifalias})".format(host = self.hostname,
                                                               ifname = self.ifName,
                                                               ifalias = self.ifAlias)
