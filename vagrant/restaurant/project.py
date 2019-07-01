from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from restaurant_model import Restaurant, Base, MenuItem


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine 
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

# API Endpoint for all menu items.
@app.route('/restaurants/<int:restaurant_id>/menu/json')
def restaurant_menu_json(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()

    return jsonify(MenuItems=[i.serialize for i in items])

# API Endpoint for specific menu item.
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/json')
def restaurant_menu_item_json(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()

    return jsonify(MenuItem=item.serialize)

@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurant_menu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)

    return render_template('menu.html', restaurant=restaurant, items=items)

@app.route('/restaurant/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def new_menu_item(restaurant_id):
    if request.method == 'POST':
        new_item = MenuItem(name=request.form['name'], restaurant_id=restaurant_id)
        session.add(new_item)
        session.commit()
        flash('New menu item created.')
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template('new_menu_item.html', restaurant_id=restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET', 'POST'])
def edit_menu_item(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        session.add(item)
        session.commit()
        flash('Item {} edited!'.format(request.form['name']))
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template(
            'edit_menu_item.html', restaurant_id=restaurant_id, menu_id=menu_id, item=item)

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET', 'POST'])
def delete_menu_item(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Item {} deleted!'.format(item.name))
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template(
            'delete_menu_item.html', item=item
        )

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True  # Flask reloads the web app if it noticed changes.
    app.run(host='0.0.0.0', port=5000, threaded=False)