import datetime
import httplib2
import json
import random
import requests
import string

from flask import (
    Flask, render_template, request, redirect,
    jsonify, url_for, flash, make_response)
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
    return render_template(
        'category.html',
        categories=categories,
        items=items,
        user=login_session.get('username'))


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
        category = Category(
            name=request.form['name'], user_id=login_session['user_id'])
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
            user_id=login_session['user_id'])
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


@app.route('/login')
def login():
    # Create anti-forgery state token
    state = ''.join(
      random.choice(string.ascii_uppercase + string.digits) for x in xrange(32)
    )
    login_session['state'] = state
    return render_template('login.html', state=state, client_id=client_id)


@app.route('/logout')
def logout():
    if not login_session.get('access_token'):
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Revoke the access token.
    response = requests.post(
        'https://accounts.google.com/o/oauth2/revoke',
        params={'token': login_session['access_token']},
        headers={'content-type': 'application/x-www-form-urlencoded'})

    if response.status_code == 200:
        del login_session['logged_in']
        del login_session['access_token']
        del login_session['google_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        flash('You have been logged out.')
        return redirect(url_for('show_categories'))
    else:
        flash('Failed to revoke token for given user!')
        return redirect(url_for('show_categories'))


@app.route('/connect', methods=['POST'])
def connect():
    """Exchange the one-time authorization code for a token and
    store the token in the session. Ensure that the request is
    not a forgery and that the user sending this connect request
    is the expected user."""

    if request.args.get('state', '') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'credentials/client_secret_oauth.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}' \
        .format(credentials.access_token)

    http_obj = httplib2.Http()
    result = json.loads(http_obj.request(url, 'GET')[1])

    # Check for errors.
    if result.get('error'):
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verification against token IDs.
    google_id = credentials.id_token['sub']
    if result['user_id'] != google_id:
        response = make_response(
            json.dumps('Token user ID does not match given user ID.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != client_id:
        response = make_response(
            json.dumps('Token client ID does not match that of the app.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    session_access_token = login_session.get('access_token')
    session_google_id = login_session.get('google_id')

    # Check if user is already logged in.
    if session_access_token and google_id == session_google_id:
        response = make_response(
            json.dumps('Current user is already logged in.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the token.
    login_session['access_token'] = credentials.access_token
    login_session['google_id'] = google_id

    # Store user information.
    user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    user_info_response = requests.get(
        user_info_url, params={
            'access_token': credentials.access_token,
            'alt': 'json'}
    )

    login_session['logged_in'] = True
    login_session['provider'] = 'google'
    login_session['username'] = user_info_response.json()['name']
    login_session['picture'] = user_info_response.json()['picture']
    login_session['email'] = user_info_response.json()['email']

    flash('Hi, {}. You are logged in!'.format(login_session['username']))

    return render_template(
        'login_success.html',
        username=login_session['username'],
        image_url=login_session['picture'])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
