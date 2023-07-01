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
from service.common.error_handlers import request_validation_error, bad_request, not_found, internal_server_error, \
    mediatype_not_supported
from service.models import Shopcart, Item, DataValidationError
from . import app

DEFAULT_CONTENT_TYPE = "application/json"


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

def is_expected_content_type(expected_content_type):
    """ Verify and abort if not expected content type """
    content_type = request.headers.get("Content-Type")
    if not content_type or content_type != expected_content_type:
        app.logger.error("Invalid Content-Type: %s", content_type)
        return False
    return True


######################################################################
# S H O P C A R T   A P I S
######################################################################

@app.route("/shopcarts", methods=["POST"])
def create_shopcart():
    """ Creates a new shopcart """
    if not is_expected_content_type(DEFAULT_CONTENT_TYPE):
        return mediatype_not_supported(f"Content-Type must be {DEFAULT_CONTENT_TYPE}")

    try:
        app.logger.info(f"Start creating a shopcart")
        shopcart = Shopcart()
        shopcart.deserialize(request.get_json())
        app.logger.info(f"Request body deserialized to shopcart")
    except DataValidationError as e:
        return request_validation_error(e)
    except Exception as e:
        return internal_server_error(e)

    try:
        shopcart.create()
        app.logger.info(f"New shopcart created with id={shopcart.id}")
        shopcart_js = shopcart.serialize()
        return make_response(jsonify(shopcart_js), status.HTTP_201_CREATED)
    except Exception as e:
        return internal_server_error(e)

######################################################################
# I T E M   A P I S
######################################################################
