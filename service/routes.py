"""
My Service

Describe what your service does here
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Shopcart, Item

# Import Flask application
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

# Place your REST API code here ...
######################################################################
# CREATE A NEW shopcart
######################################################################
@app.route("/shopcarts", methods=["POST"])
def create_shopcarts():
    """
    Creates an shopcart
    This endpoint will create an shopcart based the data in the body that is posted
    """
    app.logger.info("Request to create an shopcart")
    
    # Create the shopcart
    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())
    shopcart.create()

    # Create a message to return
    message = shopcart.serialize()
    location_url = url_for("create_shopcarts", shopcart_id=shopcart.id, _external=True)

    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

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


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )