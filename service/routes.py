"""
Shopcarts Service

The shopcarts service allows customers to make a collection of products that they want to purchase. It contains a
reference to a product and the quantity the customer wants to buy. It also contains the price of the product at the time
they placed it in the cart. A customer will only have one shopcart.

Shopcart API Paths:
----
GET  /shopcarts - Returns a list of shopcarts in the system
POST /shopcarts - Creates a new shopcart
GET  /shopcarts/{shopcart_id} - Returns the shopcart
PUT  /shopcarts/{shopcart_id} - Updates the shopcart
DELETE /shopcarts/{shopcart_id} - Deletes the shopcart

Item API Paths:
----
GET  /shopcarts/{shopcart_id}/items - Returns a list of items in the shopcart
POST /shopcarts{shopcart_id}/items - Creates a new item in the shopcart
GET  /shopcarts/{shopcart_id}/items/{item_id} - Returns the item in the shopcart
PUT  /shopcarts/{shopcart_id}/items/{item_id} - Updates the item in the shopcart
DELETE /shopcarts/{shopcart_id}/items/{item_id} - Delete the item from the shopcart
"""

from flask import jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Shopcart, Item

from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

######################################################################
# S H O P C A R T   A P I S
######################################################################

######################################################################
# I T E M   A P I S
######################################################################
