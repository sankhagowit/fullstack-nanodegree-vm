from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, Category, User
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

ore = Category(name="Ore", author=me.email)
session.add(ore)
session.commit()

apple = Item(name="Apple", description="Delicious Fruit, one a day keeps the doctor away", category_name="Food", author=me.email)
session.add(apple)
session.commit()

orange = Item(name="Orange", description="From Florida or California, incredible", category_name="Food", author=me.email)
session.add(orange)
session.commit()

diamond = Item(name="Diamond", description="Shiney rock, coveted by humans, oddly expensive for its actual supply", category_name="Ore", author=me.email)
session.add(diamond)
session.commit()

flint = Item(name="Flint", description="Shiney rock, makes sparks and arrowheads", category_name="Ore", author=me.email)
session.add(flint)
session.commit()
