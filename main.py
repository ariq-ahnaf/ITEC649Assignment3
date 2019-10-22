import random
from bottle import Bottle, template, static_file, request, redirect, HTTPError

import model
import session

app = Bottle()

#The index page generates and displays the homepage for the webapp
@app.route('/')
def get_index_page(db):
    session.get_or_create_session(db)
    data = model.product_list(db)
    info = {
        'title': "The WT Store",
        'message': data,
    }

    return template('index', info)

# This function generates the about page with the data given by the message
@app.route('/about')
def get_about_page(db):
    session.get_or_create_session(db)
    info = {
        'title': "The WT Store",
        'message': "Welcome to WT! The innovative online store. You will find beautifully designed and artistically crafted items"
                   "for all your needs.",
    }

    return template('about', info)

# The category function checks for the name data in the category field. If a match is found, then all the products matching
# that category will be retrieved and displayed using the category_page view.
# Otherwise a 'No item found' message is displayed using the category_error_page
@app.route('/category/<name>')
def get_category_page(db, name):
    pro_cat = model.product_list(db, name)
    print(name)
    if name == 'men' or name == 'women':
        info = {
            'title': "The WT Store",
            'data': pro_cat,
            }
        return template('category_page', info)
    else:
        return template('category_error_page')

# This function will dynamically generate a page to display individual product data to the user
# The user will have the option to purchase the product by clicking on the form below the product description
# It will only generate pages for valid products in the database and will otherwise display a 404 error
@app.route('/product/<id>')
def get_product_page(db, id):
    sessionid = session.get_or_create_session(db)
    data = model.product_get(db, id)
    if int(id) > 20:
        return HTTPError(404)
    else:
        info = {
            'data': data
        }
        session.response.set_cookie(sessionid, "", path="/")
        return template('product_page', info)

# The get_cart function will create a session and get the contents of the cart for current session
# It will retrieve the products in cart by the associated id and set its data into a empty array for
# manipulation. The total cost is calculated here by handling data from the post_cart function and
# added to each update of the session
#
@app.route('/cart', method="GET")
def get_cart_page(db):
    sessionid = session.get_or_create_session(db)
    cart_items = session.get_cart_contents(db)
    products = []
    total = 0
    for each in cart_items:
        dbresponse = model.product_get(db, each['id'])
        product = {
            'id': dbresponse['id'],
            'name': dbresponse['name'],
            'image_url': dbresponse['image_url'],
            'description': dbresponse['description'],
            'inventory': dbresponse['inventory'],
            'cost': each['cost'],
            'quantity': each['quantity']
        }
        total += each['cost']
        products.append(product)
        session.response.set_cookie(sessionid)
    return template('cart', {'products': products, 'total': total, 'title': "Your Shopping Cart contains..."})

# The post_cart function updates the current session with the user input of quantity and associated product id
# The update is passed on to the get_cart method to calculate total price of the current cart contents
# It then continues the session by redirecting to the cart page
@app.route('/cart', method="POST")
def post_cart_page(db):
    session.get_or_create_session(db)
    new_product= request.forms.get("product")
    new_quantity = request.forms.get("quantity")
    session.add_to_cart(db, new_product, new_quantity)
    session.get_or_create_session(db)
    redirect('/cart')


@app.route('/static/<filename:path>')
def static(filename):
    return static_file(filename=filename, root='static')


if __name__ == '__main__':
    from bottle.ext import sqlite
    from dbschema import DATABASE_NAME

    # install the database plugin
    app.install(sqlite.Plugin(dbfile=DATABASE_NAME))
    app.run(debug=True, port=8010)

# REFERENCES USED
# https://bottlepy.org/docs/dev/tutorial.html
# http://pwp.stevecassidy.net/bottle/sessions.html
# https://www.w3schools.com/python/python_json.asp
# https://realpython.com/python-json/
# http://pwp.stevecassidy.net/bottle/forms-processing.html
# https://pythonschool.net/server-side-scripting/processing-the-form-data/
# https://www.w3schools.com/python/python_mysql_getstarted.asp
# https://docs.python.org/3/library/sqlite3.html
# https://www.programcreek.com/python/example/14949/bottle.HTTPError
