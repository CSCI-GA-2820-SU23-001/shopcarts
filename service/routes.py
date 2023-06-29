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






######################################################################
# RETRIEVE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:customer_id>", methods=["GET"])
def get_shopcarts(customer_id):
    """
    Retrieve a single Shopcart
    This endpoint will return an Shopcart based on related customer id
    """
    app.logger.info("Request for Shopcart with id: %s", customer_id)
    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(customer_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{customer_id}' could not be found.",
        )
    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


# RETRIEVE A ITEM FROM SHOPCART
######################################################################
@app.route("/shopcarts/<int:customer_id>/items/<int:item_id>", methods=["GET"])
def get_items(customer_id, item_id):
    """
    Get a Item

    This endpoint returns just a item
    """
    app.logger.info(
        "Request to retrieve Item %s for Shopcart id: %s", item_id, customer_id)

    # See if the item exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{item_id}' could not be found.",
        )

    app.logger.info("Returning item: %s", item.id)
    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)


