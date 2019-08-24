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

# Connect to Database and create database session
engine = create_engine(
    'sqlite:///catalog.db',
    connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# JSON to view catelog.
@app.route('/catalog/json')
def catalog_json():
    items = session.query(Category).all()
    return jsonify(categories=[i.serialize for i in items])


# Show all categories and items in the catalog.
@app.route('/')
@app.route('/catalog')
def show_category():
    categories = session.query(Category).all()
    # TODO: Update this to only return the latest items.
    items = session.query(Item).all()
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
@app.route('/catalog/new', methods=['GET', 'POST'])
def new_category():
    if request.method == 'POST':
        new_category = Category(name=request.form['name'], user_id=user_id)
        session.add(new_category)
        flash('New Category %s created!' % new_category.name)
        session.commit()
        return redirect(url_for('show_category'))
    else:
        return render_template('category_new.html')


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


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
