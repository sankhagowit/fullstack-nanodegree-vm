from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Shelter, Puppy

engine = create_engine('sqlite///puppyshelter.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
sess = DBSession()
