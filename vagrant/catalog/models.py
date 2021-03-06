import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    google_id = Column(String, nullable=False)


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    created_on = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_on = Column(DateTime, default=datetime.datetime.utcnow)

    # Foreign keys.
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)

    @property
    def serialize(self):
        return {
           'name': self.name,
           'id': self.id,
           'user_id': self.user_id
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(500), nullable=False)
    created_on = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_on = Column(DateTime, default=datetime.datetime.utcnow)

    # Foreign keys.
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)

    @property
    def serialize(self):
        return {
           'id': self.id,
           'name': self.name,
           'description': self.description,
           'category_id': self.category_id
        }


engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.create_all(engine)
