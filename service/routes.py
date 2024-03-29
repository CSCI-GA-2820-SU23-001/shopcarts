"""
Shopcarts Service Routes

GET  /

GET  /health

GET  /shopcarts
POST /shopcarts
GET  /shopcarts/{shopcart_id}
PUT  /shopcarts/{shopcart_id}
DELETE /shopcarts/{shopcart_id}

GET  /shopcarts/{shopcart_id}/items
POST /shopcarts{shopcart_id}/items
GET  /shopcarts/{shopcart_id}/items/{item_id}
PUT  /shopcarts/{shopcart_id}/items/{item_id}
DELETE /shopcarts/{shopcart_id}/items/{item_id}
"""

from flask import request, abort
from flask_restx import Resource, fields, reqparse

from service.common import status  # HTTP Status Codes
from service.models import Shopcart, Item, DataValidationError
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

shopcart_args = reqparse.RequestParser()
shopcart_args.add_argument(
    "name", type=str, location="args", required=False, help="List Shopcarts by name"
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


def check_shopcart_id(shopcart_id):
    """ Check shopcart_id value type """
    if not str(shopcart_id).isdigit():
        app.logger.error("Invalid shopcart_id: %s", shopcart_id)
        abort(
            status.HTTP_404_NOT_FOUND,
            "shopcart_id must be a positive integer."
        )


def check_item_id(item_id):
    """ Check item_id value type """
    if not str(item_id).isdigit():
        app.logger.error("Invalid item_id: %s", item_id)
        abort(
            status.HTTP_404_NOT_FOUND,
            "item_id must be a positive integer."
        )


######################################################################
# S H O P C A R T   A P I S
######################################################################

@api.route("/shopcarts/<shopcart_id>")
@api.param("shopcart_id", "The Shopcart identifier")
class ShopcartResource(Resource):
    """
    ShopcartResource Class

    Allows the manipulation of a single Shopcart:
    GET /shopcarts/<int:shopcart_id> - Get a Shopcart according to shopcart_id
    PUT /shopcarts/<int:shopcart_id> - Update a Shopcart according to shopcart_id
    DELETE /shopcarts/<int:shopcart_id> - Delete a Shopcart according to shopcart_id
    """

    @api.doc("get_shopcarts")
    @api.response(404, "Shopcart not found")
    @api.marshal_with(shopcart_model)
    def get(self, shopcart_id):
        """
        Get a Shopcart

        This endpoint will return the Shopcart according to the shopcart_id specified in the path.
        """
        check_shopcart_id(shopcart_id)

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
    @api.expect(shopcart_base_model)
    @api.marshal_with(shopcart_model)
    def put(self, shopcart_id):
        """
        Update a Shopcart

        This endpoint will update the Shopcart based on the posted body according to the shopcart_id specified in the
        path.
        """
        check_shopcart_id(shopcart_id)
        check_content_type(DEFAULT_CONTENT_TYPE)

        app.logger.info("Request to update shopcart with id: %s", shopcart_id)
        shopcart = Shopcart.get_by_id(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found."
            )
        data = api.payload
        try:
            shopcart.deserialize(data)
        except DataValidationError as error:
            abort(status.HTTP_400_BAD_REQUEST, error.message)
        shopcart.id = shopcart_id
        shopcart.update()
        return shopcart.serialize(), status.HTTP_200_OK

    @api.doc("delete_shopcarts")
    @api.response(204, "Shopcart deleted")
    def delete(self, shopcart_id):
        """
        Delete a Shopcart

        This endpoint will delete the Shopcart according to the shopcart_id specified in the path.
        """
        app.logger.info("Start deleting shopcart %s...", shopcart_id)
        shopcart = Shopcart.get_by_id(shopcart_id)
        if shopcart:
            shopcart.delete()
            app.logger.info("Shopcart deleted with id= %s ", shopcart_id)

        return "", status.HTTP_204_NO_CONTENT


@api.route("/shopcarts/<shopcart_id>/clear")
@api.param("shopcart_id”, “The Shopcart identifier")
class ClearShopcartResource(Resource):
    """
    ClearShopcartResource Class

    Allows the manipulation of a single Shopcart:
    PUT /shopcarts/<int:shopcart_id>/clear - Clear a Shopcart according to id
    """

    @api.doc("clear_shopcarts")
    @api.response(404, "Shopcart not found")
    @api.marshal_with(shopcart_model)
    def put(self, shopcart_id):
        """
        Clear a Shopcart

        This endpoint will clear all items in the Shopcart according to the shopcart_id specified in the path.
        """
        check_shopcart_id(shopcart_id)

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


@api.route("/shopcarts", strict_slashes=False)
class ShopcartCollection(Resource):
    """
    ShopcartCollection Class

    Allows interactions with collections of Shopcarts:
    POST /shopcarts - Create a Shopcart
    GET /shopcarts - List all Shopcarts
    """

    @api.doc("create_shopcarts")
    @api.response(400, "Invalid shopcart request body")
    @api.response(415, "Invalid header content-type")
    @api.expect(shopcart_base_model)
    @api.marshal_with(shopcart_model, code=201)
    def post(self):
        """
        Create a Shopcart

        This endpoint will create a Shopcart based on the posted body.
        """
        check_content_type(DEFAULT_CONTENT_TYPE)

        app.logger.info("Start creating a shopcart")
        shopcart = Shopcart()
        try:
            shopcart.deserialize(api.payload)
        except DataValidationError as error:
            abort(status.HTTP_400_BAD_REQUEST, error.message)
        app.logger.info("Request body deserialized to shopcart")

        shopcart.create()  # store in table
        app.logger.info("New shopcart created with id=%s", shopcart.id)
        shopcart_js = shopcart.serialize()
        return shopcart_js, status.HTTP_201_CREATED

    @api.doc("list_shopcarts")
    @api.expect(shopcart_args, validate=True)
    @api.marshal_with(shopcart_model)
    def get(self):
        """
        List all Shopcarts

        This endpoint will list all Shopcarts in the system.
        """
        app.logger.info("Request to list all Shopcarts")
        shopcarts = []
        args = shopcart_args.parse_args()
        if args["name"]:
            app.logger.info("Filtering by name: %s", args["name"])
            shopcarts = list(Shopcart.find_by_name(args["name"]))
        else:
            app.logger.info("Returning unfiltered list")
            shopcarts = Shopcart.get_all()

        app.logger.info("[%s] Shopcarts returned", len(shopcarts))
        results = [shopcart.serialize() for shopcart in shopcarts]
        return results, status.HTTP_200_OK


######################################################################
# I T E M   A P I S
######################################################################

@api.route("/shopcarts/<int:shopcart_id>/items", strict_slashes=False)
@api.param("shopcart_id", "The Shopcart identifier")
class ItemCollection(Resource):
    """
    ItemCollection Class

    Allows interactions with collections of Items:
    POST /shopcarts/<int:shopcart_id>/items - Add an Item to the Shopcart according to shopcart_id
    GET /shopcarts/<int:shopcart_id>/items - List all items in the Shopcart according to shopcart_id
    """

    @api.doc("create_items")
    @api.response(400, "Invalid item request body")
    @api.response(404, "Shopcart not found")
    @api.response(415, "Invalid header content-type")
    @api.expect(item_base_model)
    @api.marshal_with(item_model, code=201)
    def post(self, shopcart_id):
        """
        Create an Item

        This endpoint will add an Item to the Shopcart based on the posted body according to the shopcart_id specified
        in the path.
        """
        check_shopcart_id(shopcart_id)
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
        try:
            item.deserialize(api.payload)  # validate request body schema
        except DataValidationError as error:
            abort(status.HTTP_400_BAD_REQUEST, error.message)
        app.logger.info("Request body deserialized to item.")

        if item.quantity != 1:
            app.logger.error("Invalid item quantity assignment to %s.", item.quantity)
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Quantity of a new item should always be one."
            )

        if item.price < 0:
            app.logger.error("Invalid item price assignment to %s.", item.price)
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Price of a new item must be positive."
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
        """
        List Items in a Shopcart

        This endpoint will list all Items in the Shopcart according to the shopcart_id specified in the path.
        """
        check_shopcart_id(shopcart_id)

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


@api.route("/shopcarts/<shopcart_id>/items/<item_id>")
@api.param("shopcart_id", "The Shopcart identifier")
@api.param("item_id", "The Item identifier")
class ItemResource(Resource):
    """
    ItemResource Class

    Allows the manipulation of a single Item:
    GET /shopcarts/{shopcart_id}/items/{item_id} - Get an Item according to shopcart_id and item_id
    PUT /shopcarts/{shopcart_id}/items/{item_id} - Update an Item according to shopcart_id and item_id
    DELETE /shopcarts/{shopcart_id}/items/{item_id} - Delete an Item according to shopcart_id and item_id
    """

    @api.doc("get_items")
    @api.response(404, "Item not found")
    @api.marshal_with(item_model)
    def get(self, shopcart_id, item_id):
        """
        Get an Item

        This endpoint will return the Item according to the shopcart_id and item_id specified in the path.
        """
        check_shopcart_id(shopcart_id)
        check_item_id(item_id)

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

    @api.doc("update_items")
    @api.response(404, "Shopcart or Item not found")
    @api.response(400, "The posted Item data was not valid")
    @api.response(415, "Invalid header content-type")
    @api.expect(item_base_model)
    @api.marshal_with(item_model)
    def put(self, shopcart_id, item_id):
        """
        Update an Item

        This endpoint will update the Item based on the posted body according to the shopcart_id and item_id specified
        in the path.
        """
        check_shopcart_id(shopcart_id)
        check_item_id(item_id)
        check_content_type(DEFAULT_CONTENT_TYPE)

        app.logger.info("Request update item with shopcart_id: %s and item_id: %s", shopcart_id, item_id)
        shopcart = Shopcart.get_by_id(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' could not be found."
            )

        item = Item.get_by_id(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' could not be found."
            )

        try:
            item.deserialize(api.payload)
        except DataValidationError as error:
            abort(status.HTTP_400_BAD_REQUEST, error.message)

        if item.quantity <= 0:
            app.logger.error("Invalid item quantity assignment to %s.", item.quantity)
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Quantity of the item must be positive."
            )

        if item.price < 0:
            app.logger.error("Invalid item price assignment to %s.", item.price)
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Price of the item must be positive."
            )

        item.update()
        app.logger.info("Item with shopcart_id: %s and item_id: %s is updated successfully", shopcart_id, item_id)
        return item.serialize(), status.HTTP_200_OK

    @api.doc("delete_items")
    @api.response(204, 'Item deleted')
    def delete(self, shopcart_id, item_id):
        """
        Delete an item

        This endpoint will delete the Item according to the shopcart_id and item_id specified in the path.
        """
        app.logger.info("Request to delete item with id='%s' in shopcart with id='%s'.", item_id, shopcart_id)

        item = Item.get_by_id(item_id)
        # See if the item exists and delete it if it does
        if item:
            item.delete()

        return "", status.HTTP_204_NO_CONTENT
