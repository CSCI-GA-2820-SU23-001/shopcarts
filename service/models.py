"""
Models for Shopcart

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """ Initializes the SQLAlchemy app """
    Shopcart.init_db(app)
    Item.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class Shopcart(db.Model):
    """
    Class that represents a Shopcart
    """

    app = None

    # Table Schema
    # customer_id (primary key), customer_name, shopcart_quantity, shopcart_price
    customer_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(63), nullable=False)

    def __repr__(self):
        return f"<Shopcart for customer {self.customer_name} id=[{self.customer_id}]>"

    def create(cls, self):
        """
        Creates a Shopcart to the database
        """
        logger.info("Creating %s %s", cls.__name__, self.__repr__)
        self.customer_id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(cls, self):
        """
        Updates a Shopcart to the database
        """
        logger.info("Saving %s %s", cls.__name__, self.__repr__)
        db.session.commit()

    def delete(cls, self):
        """ Removes a Shopcart from the data store """
        logger.info("Deleting %s %s", cls.__name__, self.__repr__)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Shopcart into a dictionary """
        return {
            "customer_id": self.customer_id, 
            "customer_name": self.customer_name,
        }

    def deserialize(self, data):
        """
        Deserializes a Shopcart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id = data["customer_id"]
            self.customer_name = data["customer_name"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid Shopcart: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Shopcart: body of request contained bad or no data - "
                "Error message: " + error
            ) from error
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Shopcarts in the database """
        logger.info("Processing all Shopcarts")
        return cls.query.all()

    @classmethod
    def find(cls, id):
        """ Finds a Shopcart by it's ID """
        logger.info("Processing lookup for id %s ...", id)
        return cls.query.get(id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Shopcarts with the given name

        Args:
            name (string): the name of the Shopcarts you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.customer_name == name) 
    
class Item(db.Model):
    """
    Class that represents a Item
    """

    app = None

    # Table Schema
    # customer_id (primary key), item_id (primary key), item_name, item_quantity, item_price
    customer_id = db.Column(db.Integer, primary_key=True) 
    item_id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(128), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self):
        return f"<Item {self.name} id=[{self.item_id}]>"

    def create(cls, self):
        """
        Creates a Item to the database
        """
        logger.info("Creating %s %s", cls.__name, self.__repr__)
        self.item_id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(cls, self):
        """
        Updates a Item to the database
        """
        logger.info("Saving %s %s", cls.__name, self.__repr__)
        db.session.commit()

    def delete(self):
        """ Removes a Item from the data store """
        logger.info("Deleting %s %s", cls.__name, self.__repr__)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Item into a dictionary """
        return {
            "customer_id": self.customer_id,
            "item_id": self.item_id, 
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price
        }

    def deserialize(self, data):
        """
        Deserializes a Item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id = data["customer_id"]
            self.item_id = data["item_id"]
            self.name = data["name"]
            self.quantity = data["quantity"]
            self.price = data["price"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid Item: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained bad or no data - "
                "Error message: " + error
            ) from error
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Items in the database """
        logger.info("Processing all Item")
        return cls.query.all()

    @classmethod
    def find(cls, id):
        """ Finds a Item by it's ID """
        logger.info("Processing lookup for id %s ...", id)
        return cls.query.get(id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Items with the given name

        Args:
            name (string): the name of the Item you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)