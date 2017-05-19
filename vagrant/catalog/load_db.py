from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, Category, ItemCategory, User
from application import getUserID, getUserInfo, createUser

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Make my email address a user
I_exist = getUserID("rksankha@gmail.com")
if I_exist:
    print "You do exist!"
    me = getUserInfo(I_exist)
else:
    print "Making new Bobby"
    user1 = User(name="Bobby", email="rksankha@gmail.com")
    session.add(user1)
    session.commit()
    me = session.query(User).filter_by(email="rksankha@gmail.com").one()

food = Category(name="Food", author=me.email)
session.add(food)
session.commit()

# critters = Category(name="Critters", author=me.email)
# monster = Category(name="Monster Parts", author=me.email)
# guardian = Category(name="Guardian Parts", author=me.email)

ore = Category(name="Ore", author=me.email)
session.add(ore)
session.commit()
