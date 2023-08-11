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
from flask import jsonify, request, make_response, abort
from flask_restx import Resource, fields

from service.common import status  # HTTP Status Codes
from service.models import Shopcart, Item
from . import app, api

DEFAULT_CONTENT_TYPE = "application/json"

item_base_model = api.model(
    "ItemBaseModel",
    {
        "shopcart_id": fields.Integer(
            readOnly=True,
            description="Shopcart id where the item belongs"
        ),
        "name": fields.String(
            required=True,
            description="Item name"
        ),
        "quantity": fields.Integer(
            required=True,
            description="Item quantity",
        ),
        "price": fields.Float(
            required=True,
            description="Item unit price"
        )
    },
)

item_model = api.inherit(
    "ItemModel",
    item_base_model,
    {
        "id": fields.Integer(
            readOnly=True,
            description="Item id (an unique id assigned internally by service)"
        )
    },
)

shopcart_base_model = api.model(
    "ShopcartBaseModel",
    {
        "name": fields.String(
            required=True,
            description="Shopcart name"
        )
    },
)

shopcart_model = api.inherit(
    "ShopcartModel",
    shopcart_base_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
        "items": fields.List(fields.Nested(item_model))
    },
)


############################################################
# Health Endpoint
############################################################

@app.route("/health")
def health():
    """Health Status"""
    return {"status": 'OK'}, status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################

@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file('index.html')


@app.route('/shopcartsapi')
def shopcartsapi():
    """Shopcarts API URL"""
    return app.send_static_file('shopcarts.html')


@app.route('/itemsapi')
def itemsapi():
    """Items API URL"""
    return app.send_static_file('items.html')


######################################################################
#  U T I L I T Y  F U N C T I O N S
######################################################################

def check_content_type(expected_content_type):
    """ Verify and abort if not expected content type """
    content_type = request.headers.get("Content-Type")
    if not content_type:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {expected_content_type}"
        )

    if content_type != expected_content_type:
        app.logger.error("Invalid Content-Type: %s", content_type)
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {expected_content_type}"
        )


######################################################################
#  PATH: /shopcarts/{id}
######################################################################

@api.route("/shopcarts/<shopcart_id>")
@api.param("shopcart_id", "The Shopcart identifier")
class ShopcartResource(Resource):

    """
    ShopcartResource class
    Allows the manipulation of a single Shopcart
    GET /shopcart{id} - Returns a Shopcart with the id
    PUT /shopcart{id} - Update a Shopcart with the id
    DELETE /shopcart{id} -  Deletes a Shopcart with the id
    """

    @api.doc("get_shopcarts")
    @api.response(404, "Shopcart not found")
    @api.marshal_with(shopcart_model)
    def get(self, shopcart_id):
        """
        Retrieve a single Shopcart
        This endpoint will return an Shopcart based on its id
        """
        app.logger.info("Request for Shopcart with id: %s", shopcart_id)
        shopcart = Shopcart.get_by_id(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' could not be found."
            )
        app.logger.info("Returning shopcart: %s", shopcart.id)
        return shopcart.serialize(), status.HTTP_200_OK

    @api.doc("update_shopcarts")
    @api.response(404, "Shopcart not found")
    @api.response(400, "The posted Shopcart data was not valid")
    @api.response(415, "Invalid header content-type")
    @api.expect(shopcart_base_model)  # Updated the expect decorator
    @api.marshal_with(shopcart_model)
    def put(self, shopcart_id):
        """
        Update a Shopcart

        This endpoint will update a Shopcart based on the body that is posted
        """
        check_content_type(DEFAULT_CONTENT_TYPE)
        app.logger.info("Request to update shopcart with id: %s", shopcart_id)
        shopcart = Shopcart.get_by_id(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found."
            )
        data = api.payload
        shopcart.deserialize(data)
        shopcart.id = shopcart_id
        shopcart.update()
        return shopcart.serialize(), status.HTTP_200_OK

    @api.doc("delete_shopcarts")
    @api.response(204, "Shopcart deleted")
    def delete(self, shopcart_id):
        """
        Delete a Shopcart

        This endpoint will delete a Shopcart based the id specified in the path
        """
        app.logger.info("Start deleting shopcart %s...", shopcart_id)
        shopcart = Shopcart.get_by_id(shopcart_id)
        if shopcart:
            shopcart.delete()
            app.logger.info("Shopcart deleted with id= %s ", shopcart_id)

        return "", status.HTTP_204_NO_CONTENT

######################################################################
#  PATH: /shopcarts/{id}/clear
######################################################################


@api.route("/shopcarts/<shopcart_id>/clear")
@api.param("shopcart_id”, “The Shopcart identifier")
class ClearResource(Resource):
    """Clear actions on a Shopcart"""
    @api.doc("clear_shopcarts")
    @api.response(404, "Shopcart not found")
    @api.marshal_with(shopcart_model)
    def put(self, shopcart_id):
        """Clear a shopcart
        Args:
            user_id (str): the user_id of the shopcart to delete
        """
        app.logger.info("Request for Shopcart with id: %s", shopcart_id)
        shopcart = Shopcart.get_by_id(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' could not be found.",
            )
        app.logger.info("Returning shopcart: %s", shopcart_id)
        app.logger.info("Request to clear shopcart with id: %s", shopcart_id)
        shopcart = Shopcart.get_by_id(shopcart_id)
        for item in shopcart.items:
            item.delete()
            app.logger.info("Deleted item '%s' in shopcart with id='%s'.", item, shopcart_id)
        shopcart.update()
        return shopcart.serialize(), status.HTTP_200_OK

######################################################################
# S H O P C A R T   A P I S
######################################################################


@api.route("/shopcarts", strict_slashes=False)
class ShopcartCollection(Resource):
    """
    ShopcartCollection Class
    Allows interactions with collections of Shopcarts:
    GET /shopcarts - Returns a list of shopcarts
    POST /shopcarts - Create a shopcart
    """

    @api.doc("create_shopcarts")
    @api.response(400, "Invalid shopcart request body")
    @api.response(415, "Invalid header content-type")
    @api.expect(shopcart_base_model)
    @api.marshal_with(shopcart_model, code=201)
    def post(self):
        """ Creates a new shopcart """
        check_content_type(DEFAULT_CONTENT_TYPE)

        app.logger.info("Start creating a shopcart")
        shopcart = Shopcart()
        shopcart.deserialize(api.payload)
        app.logger.info("Request body deserialized to shopcart")

        shopcart.create()  # store in table
        app.logger.info("New shopcart created with id=%s", shopcart.id)
        shopcart_js = shopcart.serialize()
        return shopcart_js, status.HTTP_201_CREATED


@app.route("/shopcarts", methods=["POST"])
def create_shopcarts():
    """ Creates a new shopcart """
    check_content_type(DEFAULT_CONTENT_TYPE)

    app.logger.info("Start creating a shopcart")
    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())
    app.logger.info("Request body deserialized to shopcart")

    shopcart.create()  # store in table
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
            f"Shopcart with id '{shopcart_id}' could not be found."
        )
    app.logger.info("Returning shopcart: %s", shopcart.id)
    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


@app.route("/shopcarts/<int:shopcart_id>", methods=['PUT'])
def update_shopcarts(shopcart_id):
    """ Update shopcart content """
    check_content_type(DEFAULT_CONTENT_TYPE)

    app.logger.info("Request to update shopcart with id: %s", shopcart_id)
    shopcart = Shopcart.get_by_id(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' was not found."
        )

    shopcart.deserialize(request.get_json())
    shopcart.id = shopcart_id
    shopcart.update()

    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


@app.route("/shopcarts/<int:shopcart_id>", methods=["DELETE"])
def delete_shopcarts(shopcart_id):
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


@app.route("/shopcarts/<int:shopcart_id>/clear", methods=["PUT"])
def clear_shopcart(shopcart_id):
    """Clear a shopcart
        Args:
            user_id (str): the user_id of the shopcart to delete
    """
    app.logger.info("Request for Shopcart with id: %s", shopcart_id)

    shopcart = Shopcart.get_by_id(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )
    app.logger.info("Returning shopcart: %s", shopcart_id)
    app.logger.info("Request to clear shopcart with id: %s", shopcart_id)
    shopcart = Shopcart.get_by_id(shopcart_id)

    for item in shopcart.items:
        item.delete()
        app.logger.info("Deleted item '%s' in shopcart with id='%s'.", item, shopcart_id)
    shopcart.update()
    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


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


######################################################################
# I T E M   A P I S
######################################################################

@api.route("/shopcarts/<int:shopcart_id>/items", strict_slashes=False)
@api.param("shopcart_id", "The Shopcart identifier")
class ItemCollection(Resource):
    """
    ItemCollection Class

    Allows interactions with collections of Items:
    POST /shopcarts/<int:shopcart_id>/items - Add an Item to shopcart
    GET /shopcarts/<int:shopcart_id>/items - Returns a list of items in shopcart
    """

    @api.doc("create_items")
    @api.response(400, "Invalid item request body")
    @api.response(404, "Shopcart not found")
    @api.response(415, "Invalid header content-type")
    @api.expect(item_base_model)
    @api.marshal_with(item_model, code=201)
    def post(self, shopcart_id):
        """ Adds a new item to shopcart, and return the newly created item """
        check_content_type(DEFAULT_CONTENT_TYPE)

        shopcart = Shopcart.get_by_id(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id='{shopcart_id}' was not found."
            )
        app.logger.info("Found shopcart with id=%s", shopcart.id)

        app.logger.info("Start creating an item")
        item = Item()
        item.deserialize(api.payload)  # validate request body schema
        app.logger.info("Request body deserialized to item.")

        if item.quantity != 1:
            app.logger.error("Invalid item quantity assignment to %s.", item.quantity)
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Quantity of a new item should always be one."
            )

        shopcart.items.append(item)
        shopcart.update()
        app.logger.info("New item with id=%s added to shopcart with id=%s.", item.id, shopcart.id)

        item_js = item.serialize()
        return item_js, status.HTTP_201_CREATED

    @api.doc("list_items")
    @api.response(404, 'Shopcart not found')
    @api.marshal_list_with(item_model)
    def get(self, shopcart_id):
        """ Returns a list of items in the shopcart """
        app.logger.info("Get items in the shopcart with id=%s", shopcart_id)

        shopcart = Shopcart.get_by_id(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id='{shopcart_id}' was not found."
            )
        app.logger.info("Found shopcart with id=%s", shopcart.id)

        items = [item.serialize() for item in shopcart.items]
        return items, status.HTTP_200_OK


@app.route("/shopcarts/<int:shopcart_id>/items", methods=["POST"])
def create_items(shopcart_id):
    """ Adds a new item to shopcart, and return the newly created item """
    check_content_type(DEFAULT_CONTENT_TYPE)

    shopcart = Shopcart.get_by_id(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id='{shopcart_id}' was not found."
        )
    app.logger.info("Found shopcart with id=%s", shopcart.id)

    app.logger.info("Start creating an item")
    item = Item()
    item.deserialize(request.get_json())  # validate request body schema
    app.logger.info("Request body deserialized to item.")

    if item.quantity != 1:
        app.logger.error("Invalid item quantity assignment to %s.", item.quantity)
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Quantity of a new item should always be one."
        )

    shopcart.items.append(item)
    shopcart.update()
    app.logger.info("New item with id=%s added to shopcart with id=%s.", item.id, shopcart.id)

    item_js = item.serialize()
    return make_response(jsonify(item_js), status.HTTP_201_CREATED)


######################################################################
#  PATH: /shopcarts/<shopcart_id>/items/<item_id>
######################################################################

@api.route("/shopcarts/<shopcart_id>/items/<item_id>")
@api.param("shopcart_id", "The Shopcart identifier")
@api.param("item_id", "The Item identifier")
class ItemResource(Resource):

    """
    ItemResource class
    Allows the manipulation of a single Shopcart
    GET /shopcarts/{shopcart_id}/items/{item_id} - Returns an Item with the shopcart_id and item_id
    PUT /shopcarts/{shopcart_id}/items/{item_id} - Update an Item with the shopcart_id and item_id
    DELETE /shopcarts/{shopcart_id}/items/{item_id} -  Delete an Item with the shopcart_id and item_id
    """

    @api.doc("get_items")
    @api.response(404, "Item not found")
    @api.marshal_with(item_model)
    def get(self, shopcart_id, item_id):
        """
        Retrieve a single Item
        This endpoint will return an Item based on its shopcart_id and item_id
        """
        app.logger.info("Request to retrieve Item %s for Shopcart id: %s", item_id, shopcart_id)

        shopcart = Shopcart.get_by_id(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' could not be found."
            )

        # See if the item exists and abort if it doesn't
        item = Item.get_by_id(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' could not be found."
            )

        app.logger.info("Returning item: %s", item.id)
        item_js = item.serialize()
        return item_js, status.HTTP_200_OK


@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["GET"])
def get_items(shopcart_id, item_id):
    """
    Get a Item

    This endpoint returns just a item
    """
    app.logger.info("Request to retrieve Item %s for Shopcart id: %s", item_id, shopcart_id)

    shopcart = Shopcart.get_by_id(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found."
        )

    # See if the item exists and abort if it doesn't
    item = Item.get_by_id(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found."
        )

    app.logger.info("Returning item: %s", item.id)
    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)


@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["PUT"])
def update_items(shopcart_id, item_id):
    """ Updates an existing item in shopcart, and return the updated item """
    check_content_type(DEFAULT_CONTENT_TYPE)

    req_item = Item()
    req_item.deserialize(request.get_json())  # validate request body schema
    app.logger.info("Request body deserialized to item.")

    if req_item.quantity < 1:
        app.logger.error('Invalid item quantity %s.', req_item.quantity)
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Item quantity should be at least one."
        )

    shopcart = Shopcart.get_by_id(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id='{shopcart_id}' was not found."
        )
    app.logger.info("Found shopcart with id=%s", shopcart_id)

    # search for the corresponding item in shopcart
    item = (list(filter(lambda it: it.id == item_id, shopcart.items)) or [None])[0]
    if item is None:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id='{item_id}' was not found in shopcart with id='{shopcart_id}'."
        )
    app.logger.info("Found item with id='%s' in shopcart with id='%s'.", item_id, shopcart_id)

    app.logger.info("Start updating item with id='%s' in shopcart with id='%s'.", item_id, shopcart_id)
    item.name = req_item.name
    item.quantity = req_item.quantity
    item.price = req_item.price
    item.update()
    app.logger.info("Done updating item with id='%s' in shopcart with id='%s'.", item_id, shopcart_id)

    item_js = item.serialize()
    return make_response(jsonify(item_js), status.HTTP_200_OK)


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


@app.route("/shopcarts/<int:shopcart_id>/items", methods=["GET"])
def list_items(shopcart_id):
    """ Returns a list of items in the shopcart """
    app.logger.info("Get items in the shopcart with id=%s", shopcart_id)

    shopcart = Shopcart.get_by_id(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id='{shopcart_id}' was not found."
        )
    app.logger.info("Found shopcart with id=%s", shopcart.id)

    items = [item.serialize() for item in shopcart.items]
    return make_response(jsonify(items), status.HTTP_200_OK)
