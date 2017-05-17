from sqlalchemy import create_engine
from sqlalchemy.orm imprt sessionmaker
from database_setup import Base, Item, Category, ItemCategory, User

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
