import datetime
import httplib2
import json
import random
import requests
import string

from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash, make_response
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from models import Base, User, Item, Category


app = Flask(__name__)
client_id = json.loads(
    open('credentials/client_secret_oauth.json', 'r').read()
)['web']['client_id']

# Connect to Database and create database session
engine = create_engine(
    'sqlite:///catalog.db',
    connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# JSON to view catalog.
@app.route('/catalog/json')
def catalog_json():
    items = session.query(Category).all()
    return jsonify(categories=[i.serialize for i in items])


# Show all categories and items in the catalog.
@app.route('/')
@app.route('/catalog')
def show_categories():
    categories = session.query(Category).all()
    current_time = datetime.datetime.utcnow()
    one_week_ago = current_time - datetime.timedelta(weeks=1)
    items = session.query(Item).filter(
        Item.updated_on > one_week_ago).all()
    return render_template('category.html', categories=categories, items=items)


# Show all items for a specific category in the catalog.
@app.route('/catalog/<int:category_id>/items')
def show_category_items(category_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(
        id=category_id).one_or_none()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template(
        'category_items.html',
        categories=categories,
        category=category,
        items=items)


# Add a new category in the catalog.
@app.route('/catalog/new_category', methods=['GET', 'POST'])
def new_category():
    if request.method == 'POST':
        category = Category(name=request.form['name'], user_id=1)
        session.add(category)
        flash('New Category %s created!' % category.name)
        session.commit()
        return redirect(
            url_for('show_category_items', category_id=category.id))
    else:
        return render_template('category_add.html')


# Add a new item in the catalog.
@app.route('/catalog/new_item', methods=['GET', 'POST'])
def new_item():
    if request.method == 'POST':
        category = session.query(Category).filter_by(
            name=request.form['category']).one_or_none()
        item = Item(
            name=request.form['name'],
            description=request.form['description'],
            category_id=category.id,
            user_id=1)
        session.add(category)
        flash('New Item %s created!' % item.name)
        session.commit()
        return redirect(
            url_for('show_category_items', category_id=category.id))
    else:
        categories = session.query(Category).all()
        return render_template('item_add.html', categories=categories)


# Show a description for a specific item in a category.
@app.route('/catalog/<int:category_id>/items/<int:item_id>')
def show_item(category_id, item_id):
    category = session.query(Category).filter_by(
        id=category_id).one_or_none()
    item = session.query(Item).filter_by(
        id=item_id, category_id=category_id).one_or_none()
    return render_template(
        'item.html',
        category=category,
        item=item)


# Edit a category's item.
@app.route('/catalog/<int:category_id>/items/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(category_id, item_id):
    item = session.query(Item).filter_by(
        id=item_id, category_id=category_id
    ).one_or_none()
    category = session.query(Category).filter_by(
        id=category_id).one_or_none()

    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        session.add(item)
        session.commit()
        flash('{category_name} Item {item_name} updated!'.format(
            category_name=category.name,
            item_name=item.name))
        return redirect(
            url_for('show_category_items', category_id=category.id))
    else:
        categories = session.query(Category).all()
        return render_template(
            'item_edit.html',
            categories=categories,
            category=category,
            item=item)


# Delete a category's item.
@app.route('/catalog/<int:category_id>/items/<int:item_id>/delete', methods=['GET', 'POST'])
def delete_item(category_id, item_id):
    category = session.query(Category).filter_by(
        id=category_id).one_or_none()
    item = session.query(Item).filter_by(
        id=item_id, category_id=category_id).one_or_none()

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('{category_name} item {item_name} deleted!'.format(
            category_name=category.name,
            item_name=item.name))
        return redirect(url_for(
            'show_category_items', category_id=category.id))
    else:
        return render_template(
            'item_delete.html',
            category=category,
            item=item)


"""AUTHENTICATION ENDPOINTS"""


# Create anti-forgery state token
@app.route('/login')
def show_login():
    state = ''.join(
      random.choice(string.ascii_uppercase + string.digits) for x in xrange(32)
    )
    login_session['state'] = state
    return render_template('login.html', state=state, client_id=client_id)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
