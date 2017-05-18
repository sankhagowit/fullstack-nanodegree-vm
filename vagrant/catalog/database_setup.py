import sys

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String, nullable=False)
    author_id = Column(String, ForeignKey('user.id'))
    dateCreated = Column(DateTime, nullable=False, default=func.now())
    lastModified = Column(DateTime, nullable=False, default=func.now())
    hearts = Column(String) # Ultimately this will be a picture? from another DB?
    sell_price = Column(Integer)
    buy_price = Column(Integer)
    picture = Column(String) # will be picture, from another DB?

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id' : self.id,
            'item_name' : self.name,
            'author' : self.author, # is this last comma needed?
            'description' : self.description,
            'hearts' : self.hearts,
            'sell_price' : self.sell_price,
            'buy_price' : self.buy_price,
            'picture' : self.picture,
        }

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    author = Column(String)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id' : self.id,
            'category_name' : self.name,
            'author' : self.author, # is this last comma needed?
        }


class ItemCategory(Base):
    __tablename__ = 'itemCategory'
    # I need to identify a primary key, this is a requirement in SQLAlchemy?
    item_id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    item = relationship(Item)
    category_id = Column(Integer, ForeignKey('category.id'), primary_key=True)
    category = relationship(Category)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    # How do I know that 250 is enough? Too much? figure this out eventually
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)
