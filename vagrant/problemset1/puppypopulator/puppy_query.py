from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Shelter, Puppy

engine = create_engine('sqlite///puppyshelter.db', echo = True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()
