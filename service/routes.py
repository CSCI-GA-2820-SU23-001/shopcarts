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
from service.common.error_handlers import request_validation_error, bad_request, not_found, mediatype_not_supported
from service.models import Shopcart, Item, DataValidationError
from . import app

DEFAULT_CONTENT_TYPE = "application/json"


######################################################################
# GET INDEX
######################################################################

@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Shopcarts REST API Service",
            version="1.0",
            paths=url_for("list_shopcarts", _external=True),
        ),
        status.HTTP_200_OK)


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

@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """ List shopcart items """
    app.logger.info("Request for shopcart list")

    shopcarts = []
    name = request.args.get("name")
    if name:
        shopcarts = Shopcart.find_by_name(name)
    else:
        shopcarts = Shopcart.get_all()

    results = [shopcart.serialize() for shopcart in shopcarts]
    app.logger.info("Returning %d shopcarts", len(results))
    return jsonify(results), status.HTTP_200_OK


@app.route("/shopcarts", methods=["POST"])
def create_shopcart():
    """ Creates a new shopcart """
    if not is_expected_content_type(DEFAULT_CONTENT_TYPE):
        return mediatype_not_supported(f"Content-Type must be {DEFAULT_CONTENT_TYPE}")

    try:
        app.logger.info("Start creating a shopcart")
        shopcart = Shopcart()
        shopcart.deserialize(request.get_json())
        app.logger.info("Request body deserialized to shopcart")
    except DataValidationError as error:
        return request_validation_error(error)

    shopcart.create()
    app.logger.info("New shopcart created with id=%s", shopcart.id)
    shopcart_js = shopcart.serialize()
    return make_response(jsonify(shopcart_js), status.HTTP_201_CREATED)


@app.route("/shopcarts/<int:shopcart_id>", methods=["GET"])
def get_shopcarts(shopcart_id):
    """
    Retrieve a single Shopcart
    This endpoint will return an Shopcart based on its id
    """
    app.logger.info("Request for Shopcart with id: %s", shopcart_id)

    shopcart = Shopcart.get_by_id(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )
    app.logger.info("Returning shopcart: %s", shopcart.id)
    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


@app.route("/shopcarts/<int:shopcart_id>", methods=['PUT'])
def update_shopcarts(shopcart_id):
    """ Update shopcart content """
    if not is_expected_content_type(DEFAULT_CONTENT_TYPE):
        return mediatype_not_supported(f"Content-Type must be {DEFAULT_CONTENT_TYPE}")

    app.logger.info("Request to update shopcart with id: %s", shopcart_id)

    shopcart = Shopcart.get_by_id(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND, f"Shopcart with id '{shopcart_id}' was not found."
        )

    shopcart.deserialize(request.get_json())
    shopcart.id = shopcart_id
    shopcart.update()

    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["DELETE"])
def delete_shopcart(shopcart_id):
    """Deletes a shopcart
        Args:
            user_id (str): the user_id of the shopcart to delete
        Returns:
            str: always returns an empty string
    """
    app.logger.info("Start deleting shopcart %s...", shopcart_id)
    shopcart = Shopcart.get_by_id(shopcart_id)
    if shopcart:
        shopcart.delete()
        app.logger.info("Shopcart deleted with id= %s ", shopcart_id)
    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# I T E M   A P I S
######################################################################

@app.route("/shopcarts/<int:shopcart_id>/items", methods=["POST"])
def add_shopcart_item(shopcart_id):
    """ Adds a new item to shopcart, and return the newly created item """

    if not is_expected_content_type(DEFAULT_CONTENT_TYPE):
        return mediatype_not_supported(f"Content-Type must be {DEFAULT_CONTENT_TYPE}")

    shopcart = Shopcart.get_by_id(shopcart_id)

    if not shopcart:
        return not_found(f"Shopcart with id='{shopcart_id}' was not found.")
    app.logger.info("Found shopcart with id=%s", shopcart.id)

    app.logger.info("Start creating an item")
    item = Item()
    item.deserialize(request.get_json())  # validate request body schema
    app.logger.info("Request body deserialized to item.")

    # # item quantity should be greater than zero
    # if item.quantity <= 0:
    #     app.logger.error(f"Invalid item quantity assignment to {item.quantity}.")
    #     return bad_request(f"Item quantity should be a positive number.")
    if item.quantity != 1:
        app.logger.error("Invalid item quantity assignment to %s.", item.quantity)
        return bad_request("Quantity of a new item should always be one.")

    try:
        # item.create()
        # app.logger.info(f"New item with id={item.id} created.")
        shopcart.items.append(item)
        shopcart.update()
        app.logger.info("New item with id=%s added to shopcart with id=%s.", item.id, shopcart.id)

        item_js = item.serialize()
        return make_response(jsonify(item_js), status.HTTP_201_CREATED)
    except DataValidationError as error:
        return request_validation_error(error)


@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["GET"])
def get_items(shopcart_id, item_id):
    """
    Get a Item

    This endpoint returns just a item
    """
    app.logger.info(
        "Request to retrieve Item %s for Shopcart id: %s", item_id, shopcart_id)

    shopcart = Shopcart.get_by_id(shopcart_id)

    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    # See if the item exists and abort if it doesn't
    item = Item.get_by_id(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found.",
        )

    app.logger.info("Returning item: %s", item.id)
    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)


@app.route("/shopcarts/<int:shopcart_id>/items", methods=["GET"])
def list_shopcart_items(shopcart_id):
    """ Returns a list of items in the shopcart """
    app.logger.info("Get items in the shopcart with id=%s", shopcart_id)

    shopcart = Shopcart.get_by_id(shopcart_id)
    if not shopcart:
        return not_found(f"Shopcart with id='{shopcart_id}' was not found.")
    app.logger.info("Found shopcart with id=%s", shopcart.id)

    items = [item.serialize() for item in shopcart.items]
    return make_response(jsonify(items), status.HTTP_200_OK)


@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["PUT"])
def update_shopcart_item(shopcart_id, item_id):
    """ Updates an existing item in shopcart, and return the updated item """

    if not is_expected_content_type(DEFAULT_CONTENT_TYPE):
        return mediatype_not_supported(f"Content-Type must be {DEFAULT_CONTENT_TYPE}")

    req_body = request.get_json()
    req_body["shopcart_id"] = shopcart_id
    req_body["id"] = item_id
    req_item = Item()
    req_item.deserialize(req_body)  # validate request body schema
    app.logger.info("Request body deserialized to item.")

    if req_item.quantity < 1:
        app.logger.error('Invalid item quantity %s.', req_item.quantity)
        return bad_request("Item quantity should be at least one.")

    shopcart = Shopcart.get_by_id(shopcart_id)

    if not shopcart:
        return not_found(f"Shopcart with id='{shopcart_id}' was not found.")
    app.logger.info("Found shopcart with id=%s", shopcart_id)

    # search for the corresponding item in shopcart
    item = None
    for item_ in shopcart.items:
        if item_.id == item_id:
            item = item_
            break

    if item is None:
        return bad_request(f"Item with id='{item_id}' was not found in shopcart with id='{shopcart_id}'.")
    app.logger.info("Found item with id='%s' in shopcart with id='%s'.", item_id, shopcart_id)

    try:
        app.logger.info("Start updating item with id='%s' in shopcart with id='%s'.", item_id, shopcart_id)
        item.name = req_item.name
        item.quantity = req_item.quantity
        item.price = req_item.price
        item.update()
        app.logger.info("Done updating item with id='%s' in shopcart with id='%s'.", item_id, shopcart_id)

        item_js = item.serialize()
        return make_response(jsonify(item_js), status.HTTP_200_OK)
    except DataValidationError as error:
        return request_validation_error(error)


######################################################################
# DELETE AN ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(shopcart_id, item_id):
    """
    Delete an item

    This endpoint will delete an item based the id specified in the path
    """
    app.logger.info("Request to delete item with id='%s' in shopcart with id='%s'.", item_id, shopcart_id)

    item = Item.get_by_id(item_id)
    # See if the item exists and delete it if it does
    if item:
        item.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)
