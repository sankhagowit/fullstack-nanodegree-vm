import sys
sys.path.append('..')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Shelter, Puppy
import datetime

engine = create_engine('sqlite:///puppyshelter.db', echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

puppies = session.query(Puppy)
# Query all of the puppies and return the results in ascending alphabetical order
for puppy in puppies.order_by(Puppy.name):
    print puppy.name


# Query all of the puppies that are less than 6 months old organized by the youngest first
sixmonths = datetime.date.today() - datetime.timedelta(days=(6*30))
for puppy in puppies.filter(Puppy.dateOfBirth >= sixmonths).order_by(Puppy.dateOfBirth.desc()):
    print puppy.name, puppy.dateOfBirth

# Query all puppies by ascending weight (lowest to highest)
for puppy in puppies.order_by(Puppy.weight.desc()):
    print puppy.name, puppy.weight

# Query all puppies grouped by the shelter in which they are staying.
for puppy in puppies.group_by(Puppy.shelter_id):
    print puppy.shelter_id, puppy.name
