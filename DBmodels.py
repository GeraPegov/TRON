from sqlalchemy import Column, Integer, String, Date, Time
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Wallet(Base):
    __tablename__ = 'wallet'

    id = Column(Integer, primary_key=True, index=True)
    namewallet = Column(String)
    data = Column(Date, index = True)
    time = Column(Time)
    ip = Column(String)

    