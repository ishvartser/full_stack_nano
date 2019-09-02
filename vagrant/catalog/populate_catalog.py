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
def create_user(name, email, google_id):
    user = User(
        name=name,
        email=email,
        google_id=google_id
    )
    session.add(user)
    session.commit()
    return user


# Create a category.
def create_category(name, user):
    category = Category(
        name=name,
        user_id=user.id
    )
    session.add(category)
    session.commit()
    return category


# Create an item.
def create_item(name, description, category, user):
    item = Item(
        name=name,
        description=description,
        category_id=category.id,
        user_id=user.id
    )
    session.add(item)
    session.commit()
    return item

users = [
    {'name': 'Jane Appleseed', 'email': 'jane.appleseed@gmail.com', 'google_id': '111'},
    {'name': 'Bo Crocker', 'email': 'bo.crocker@gmail.com', 'google_id': '222'},
    {'name': 'Clint Rosewood', 'email': 'clint.rosewood@gmail.com', 'google_id': '333'},
    {'name': 'Ann Nickols', 'email': 'ann.nickols@gmail.com', 'google_id': '444'}
]

catalog_golf = {
    'name': 'golf',
    'items': [
        {'name': 'golf ball', 'description': 'a ball used for golf'},
        {'name': 'clubs', 'description': 'hit the ball with these'},
        {'name': 'golf cart', 'description': 'used for transportation around the golf course'},
    ]
}
catalog_volleyball = {
    'name': 'volleyball',
    'items': [
        {'name': 'volleyball', 'description': 'a ball used for volleyball'},
        {'name': 'net', 'description': 'the net divides two halves of the volleyball court'},
        {'name': 'sand', 'description': 'the volleyball court floor is made of this!'}
    ]
}
catalog_ultimate = {
    'name': 'ultimate',
    'items': [
        {'name': 'frisbee', 'description': 'the disc we pass in ultimate frisbee'},
        {'name': 'headband', 'description': 'it keeps your sweat from your eyeballs'}
    ]
}
catalog_horseback_racing = {
    'name': 'horseback racing',
    'items': []
}


def create_catalog_row(catalog_user, catalog_category):
    user = create_user(
        name=catalog_user['name'],
        email=catalog_user['email'],
        google_id=catalog_user['google_id']
    )
    category = create_category(
        name=catalog_category['name'],
        user=user
    )
    for item in catalog_category['items']:
        create_item(
            name=item['name'],
            description=item['description'],
            category=category,
            user=user
        )


if __name__ == '__main__':
    create_catalog_row(users[0], catalog_golf)
    create_catalog_row(users[1], catalog_volleyball)
    create_catalog_row(users[2], catalog_ultimate)
    create_catalog_row(users[3], catalog_horseback_racing)

    print('Done populating the catalog DB!')
