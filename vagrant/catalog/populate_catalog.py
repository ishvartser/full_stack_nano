from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User, Category, Item

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create a user.
def create_user(name, email) {
    user = User(
        name=name,
        email=email
    )
    session.add(user)
    session.commit()
    return user
}


# Create a category.
def create_category(name, user) {
    category = Category(
        name=name,
        user_id=user.id
    )
    session.add(category)
    session.commit()
    return category
}


# Create an item.
def create_item(name, description, category, user) {
    item = Item(
        name=name,
        description=description,
        category_id=category.id,
        user_id=user.id
    )
    session.add(item)
    session.commit()
    return item
}

user_1 = create_user(
    name='Jane Appleseed',
    email='jane.appleseed@gmail.com'
)

category_1 = create_category(
    name='Golf',
    user=user_1
)

item_1 = create_item(
    name='Golf ball',
    description='A ball used for golf.',
    category=category_1,
    user=user_1
)

print('Done populating the catalog db!')
