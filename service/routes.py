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



######################################################################
# READ A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["GET"])
def get_shopcarts(shopcart_id):
    """
    Retrieve a single Shopcart
    This endpoint will return an Shopcart based on its id
    """
    app.logger.info("Request for Shopcart with id: %s", shopcart_id)

    # See if the shopcart exists and abort if it doesn't
    # try:
    #     shopcart = Shopcart.get_by_id(shopcart_id)
    # except Exception as e:
    #     return internal_server_error(e)
    shopcart = Shopcart.get_by_id(shopcart_id)

    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )
    app.logger.info("Returning shopcart: %s", shopcart.id)
    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


    



# # RETRIEVE A ITEM FROM SHOPCART
# ######################################################################
# @app.route("/shopcarts/<int:customer_id>/items/<int:item_id>", methods=["GET"])
# def get_items(customer_id, item_id):
#     """
#     Get a Item

#     This endpoint returns just a item
#     """
#     app.logger.info(
#         "Request to retrieve Item %s for Shopcart id: %s", item_id, customer_id)

#     # See if the item exists and abort if it doesn't
#     item = Item.find(item_id)
#     if not item:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Shopcart with id '{item_id}' could not be found.",
#         )

#     app.logger.info("Returning item: %s", item.id)
#     return make_response(jsonify(item.serialize()), status.HTTP_200_OK)


# def check_content_type(content_type):
#     """Checks that the media type is correct"""
#     if "Content-Type" not in request.headers:
#         app.logger.error("No Content-Type specified.")
#         abort(
#             status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#             f"Content-Type must be {content_type}",
#         )
#     if request.headers["Content-Type"] == content_type:
#         return
#     app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
#     abort(
#         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#         f"Content-Type must be {content_type}",
#     )
