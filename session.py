"""
Code for handling sessions in our web application
"""

from bottle import request, response
import uuid
import json

import model
import dbschema

COOKIE_NAME = 'session'


def get_or_create_session(db):
    """Get the current sessionid either from a
    cookie in the current request or by creating a
    new session if none are present.

    If a new session is created, a cookie is set in the response.

    Returns the session key (string)
    """
    get_cookie = request.get_cookie(COOKIE_NAME)
    cursor1 = db.cursor()
    keylist = None
    # Checking to see if the cookie exists
    if get_cookie:
        cursor1.execute("SELECT sessionid FROM sessions WHERE sessionid = ?", (get_cookie,))
        keylist = cursor1.fetchone()
        if keylist:
            get_cookie = keylist['sessionid']
    # if the cookie does not exist, creating a new cookie and saving it to the sessions table
    if not keylist:
        get_cookie = str(uuid.uuid4())
        data = "[]"
        cursor2 = db.cursor()
        cursor2.execute("INSERT INTO sessions (sessionid, data) VALUES(?,?)", (get_cookie, data))
        db.commit()
        response.set_cookie(COOKIE_NAME, get_cookie)
    #returning the cookie response to the main program
    return get_cookie


def add_to_cart(db, itemid, quantity, update=False):
    """Add an item to the shopping cart"""
    # getting a cookie response from the previous function
    key = get_or_create_session(db)
    product = model.product_get(db, itemid)
    cost = int(quantity) * int(product[5])
    # getting the current cart data from the function below
    cart_data = get_cart_contents(db)
    # checking if the product is new or not
    check_item = False
    for eachitem in cart_data:
        if itemid == eachitem['id']:
            check_item = True
    # if the product is a new item to be added to the cart, update the cart accordingly
    if check_item is True:
        eachitem['quantity'] = int(quantity) + int(eachitem['quantity'])
        eachitem['cost'] = eachitem['cost'] +  product[5]
    else:
        update = {
                'id': itemid,
                'quantity': quantity,
                'name': product['name'],
                'cost': cost
            }
        cart_data.append(update)

    data = json.dumps(cart_data)

    cursor4 = db.cursor()
    cursor4.execute("UPDATE sessions set data = ? WHERE sessionid = ?",(data, key))
    db.commit()


def get_cart_contents(db):
    """Return the contents of the shopping cart as
    a list of dictionaries:
    [{'id': <id>, 'quantity': <qty>, 'name': <name>, 'cost': <cost>}, ...]
    """
    # first getting the cookie response to check if whether it is a new session
    # then it retrieves the data associated with that sessionid or creates a new session
    # and returns the current contents to the main program
    key = get_or_create_session(db)
    cursor3 = db.cursor()
    cursor3.execute("SELECT data FROM sessions WHERE sessionid=?", (key,))
    item_row = cursor3.fetchone()
    products = []
    if item_row['data']:
        products = json.loads(item_row['data'])
    return products
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
