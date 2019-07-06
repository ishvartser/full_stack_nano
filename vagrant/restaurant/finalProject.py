from flask import Flask

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from restaurant_model import Restaurant, Base, MenuItem


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine 
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurant/new/', methods=['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST':
        new_restaurant = Restaurant(name=request.form['name'])
        session.add(new_restaurant)
        session.commit()
        flash('New restaurant {} created!'.format(new_restaurant.name))
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('new_restaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one_or_none()
    if not restaurant:
        flash('Restaurant not found!')
        return redirect(url_for('showRestaurants'))

    if request.method == 'POST':
        if request.form['name']:
            restaurant.name = request.form['name']
        session.add(restaurant)
        session.commit()
        flash('Restaurant {} updated!'.format(restaurant.name))
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('edit_restaurant.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one_or_none()
    if not restaurant:
        flash('Restaurant not found!')
        return redirect(url_for('showRestaurants'))

    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        flash('Restaurant {} deleted!'.format(restaurant.name))
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('delete_restaurant.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one_or_none()
    if not restaurant:
        flash('Restaurant not found!')
        return redirect(url_for('showRestaurants'))

    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return render_template('menu.html', restaurant=restaurant, items=items)

@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one_or_none()
    if not restaurant:
        flash('Restaurant not found!')
        return redirect(url_for('showRestaurants'))

    if request.method == 'POST':
        new_item = MenuItem(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            restaurant_id=restaurant_id)
        session.add(new_item)
        session.commit()
        flash('Menu item {} created!'.format(new_item.name))
        return redirect(url_for('showMenu', restaurant_id=restaurant.id))
    else:
        return render_template('new_menu_item.html', restaurant=restaurant)
    
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one_or_none()
    if not restaurant:
        flash('Restaurant not found!')
        return redirect(url_for('showRestaurants'))

    item = session.query(MenuItem).filter_by(restaurant_id=restaurant_id, id=menu_id).one_or_none()
    if not item:
        flash('Menu item not found!')
        return redirect(url_for('showMenu', restaurant_id=restaurant.id))

    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        session.add(item)
        session.commit()
        flash('Menu item {} updated!'.format(restaurant.name))
        return redirect(url_for('showMenu', restaurant_id=restaurant.id))
    else:
        return render_template('edit_menu_item.html', restaurant=restaurant, item=item)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one_or_none()
    if not restaurant:
        flash('Restaurant not found!')
        return redirect(url_for('showRestaurants'))

    item = session.query(MenuItem).filter_by(restaurant_id=restaurant_id, id=menu_id).one_or_none()
    if not item:
        flash('Menu item not found!')
        return redirect(url_for('showMenu', restaurant_id=restaurant.id))

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Menu item {} deleted!'.format(item.name))
        return redirect(url_for('showMenu', restaurant_id=restaurant.id))
    else:
        return render_template('delete_menu_item.html', restaurant=restaurant, item=item)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True  # Flask reloads the web app if it noticed changes.
    app.run(host='0.0.0.0', port=5000, threaded=False)