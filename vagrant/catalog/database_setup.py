import sys

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String, nullable=False)
    author_id = Column(String, ForeignKey('user.id'))
    #dateCreated = Column(DateTime) # TODO Make this datetime, automatic
    #lastModified = Column(DateTime) # TODO Make this datetime
    hearts = Column(String)
    sell_price = Column(Integer)
    buy_price = Column(Integer)
    picture = Column(String)


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class ItemCategory(Base):
    __tablename__ = 'itemCategory'

    item_id = Column(Integer, ForeignKey('item.id'))
    item = relationship(Item)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadate.create_all(engine)
