import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

### End of File Stuff ###
engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.create_all(engine)

class Shelter(Base):
    __tablename__ = 'shelter'
    
    name = Column(String(80), nullable = False)
    address = Column()
    city = Column()
    state = Column()
    zipCode = Column()
    website = Column()
    id = Column(Integer, primary_key = True)

class Puppy(Base):
    __tablename__ = 'puppy'

    name = Column(String(80), nullable = False)
    dob
    gender
    weight
    shelter_id = Column(Integer, ForeignKey('shelter.id'))
