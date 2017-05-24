import sys

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    author = Column(String)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id' : self.id,
            'category_name' : self.name,
            'author' : self.author, # is this last comma needed?
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    # Names will actually be unique as we are using them in the routing
    name = Column(String(80), nullable=False, unique=True)
    description = Column(String, nullable=False)
    category_name = Column(String, ForeignKey('category.name'))
    category = relationship(Category)
    author = Column(String, ForeignKey('user.email'))
    dateCreated = Column(DateTime, nullable=False, default=func.now())


    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id' : self.id,
            'item' : self.name,
            'author' : self.author, # is this last comma needed?
            'description' : self.description,
            'category' : self.category_name,
        }


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    # How do I know that 250 is enough? Too much? figure this out eventually
    email = Column(String(250), nullable=False, unique=True)
    picture = Column(String(250))


engine = create_engine('postgresql:///itemcatalog')
Base.metadata.create_all(engine)
