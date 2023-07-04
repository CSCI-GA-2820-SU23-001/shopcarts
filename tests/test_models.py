"""
Test cases for Shopcart Model

"""
import logging
import unittest

from service import app
from service.models import Shopcart, Item, db
from tests.factories import ShopcartFactory, ItemFactory

from . import DATABASE_URI


######################################################################
#  S H O P C A R T   M O D E L   T E S T   C A S E S
######################################################################

class TestShopcart(unittest.TestCase):
    """ Test Cases for Shopcart Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Shopcart.init_db(app)

    # @classmethod
    # def tearDownClass(cls):
    #     """ This runs once after the entire test suite """

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_shopcart(self):
        """ It should Create an Shopcart and assert that it exists """
        fake_shopcart = ShopcartFactory()
        # pylint: disable=unexpected-keyword-arg
        shopcart = Shopcart(
            name=fake_shopcart.name,
        )
        self.assertIsNotNone(shopcart)
        self.assertEqual(shopcart.id, None)
        self.assertEqual(shopcart.name, fake_shopcart.name)

    def test_read_an_shopcart(self):
        """It should Read a Shopcart"""
        shopcart = ShopcartFactory()
        shopcart.create()
        found_shopcart = Shopcart.get_by_id(shopcart.id)

        self.assertIsNotNone(shopcart)
        self.assertEqual(found_shopcart.id, shopcart.id)
        self.assertEqual(found_shopcart.name, shopcart.name)
        self.assertEqual(found_shopcart.items, [])

    def test_update_name_of_a_shopcart(self):
        """It should update the name of a Shopcart"""
        shopcarts = Shopcart.get_all()
        self.assertEqual(len(shopcarts), 0)

        shopcart = ShopcartFactory()
        shopcart.create()
        shopcarts = Shopcart.get_all()
        self.assertEqual(len(shopcarts), 1)
        self.assertIsNotNone(shopcart.id)
        self.assertIsNotNone(shopcart.name)

        shopcart = Shopcart.get_by_id(shopcart.id)
        shopcart.name = "Dev Ops"
        shopcart.update()

        shopcart = Shopcart.get_by_id(shopcart.id)
        self.assertEqual(shopcart.name, "Dev Ops")

    def test_update_an_item_of_a_shopcart(self):
        """It should update an item of a Shopcart"""
        shopcarts = Shopcart.get_all()
        self.assertEqual(len(shopcarts), 0)
        
        shopcart = ShopcartFactory()
        shopcart.create()
        shopcarts = Shopcart.get_all()
        self.assertEqual(len(shopcarts), 1)
        self.assertIsNotNone(shopcart.id)
        self.assertIsNotNone(shopcart.name)

        items = Item.get_all()
        self.assertEqual(len(items), 0)
        item = ItemFactory(shopcart_id = shopcart.id)
        item.create()
        items = Item.get_all()
        self.assertEqual(len(items), 1)
        self.assertIsNotNone(item.id)
        self.assertEqual(item.shopcart_id, shopcart.id)
        
        shopcart = Shopcart.get_by_id(shopcart.id)
        self.assertEqual(len(shopcart.items), 1)
        # self.assertEqual(type(shopcart.items[0].id), "int")
        item_id = shopcart.items[0].id
        self.assertEqual(item.id, item_id)
        
        item.name = "Switch"
        item.price = 399.0
        item.quantity = 2
        item.update()

        shopcart = Shopcart.get_by_id(shopcart.id)
        self.assertEqual(len(shopcart.items), 1)
        item_name =  shopcart.items[0].name
        item_price =  shopcart.items[0].price
        item_quantity =  shopcart.items[0].quantity
        self.assertEqual(item.name, item_name)
        self.assertEqual(item.price, item_price)
        self.assertEqual(item.quantity, item_quantity)

######################################################################
#  I T E M   M O D E L   T E S T   C A S E S
######################################################################

class TestItem(unittest.TestCase):
    """ Test Cases for Item Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Item.init_db(app)

    # @classmethod
    # def tearDownClass(cls):
    #     """ This runs once after the entire test suite """

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_add_shopcart_item(self):
        """It should create an shopcart with an item and add it to the database"""
        shopcart = ShopcartFactory()
        shopcart.create()
        item = ItemFactory(shopcart_id=shopcart.id)
        shopcart.items.append(item)
        shopcart.update()
        self.assertIsNotNone(shopcart.id)
        new_shopcart = Shopcart.get_by_id(shopcart.id)
        self.assertEqual(len(new_shopcart.items), 1)
        self.assertEqual(new_shopcart.items[0].id, item.id)
        self.assertEqual(new_shopcart.items[0].quantity, item.quantity)
        self.assertEqual(new_shopcart.items[0].name, item.name)
        self.assertEqual(new_shopcart.items[0].price, item.price)

    def test_update_shopcart_item(self):
        """ It should update an item in shopcart """
        shopcarts = Shopcart.get_all()
        self.assertEqual(len(shopcarts), 0)

        shopcart = ShopcartFactory()
        new_item = ItemFactory(shopcart_id=shopcart.id)
        shopcart.items.append(new_item)
        shopcart.create()
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.get_all()
        self.assertEqual(len(shopcarts), 1)

        shopcart = Shopcart.get_by_id(shopcart.id)
        self.assertEqual(len(shopcart.items), 1)
        item = shopcart.items[0]
        item.name = item.name + " II"
        item.update()

        shopcart = Shopcart.get_by_id(shopcart.id)
        updated_item = shopcart.items[0]
        self.assertEqual(updated_item.name, item.name)

    ######################################################################
    #  TEST SERIALIZE ITEM
    ######################################################################

    def test_serialize_a_shopcart(self):
        """It should Serialize items into shopcart"""
        shopcart = ShopcartFactory()
        item = ItemFactory()
        shopcart.items.append(item)
        serial_shopcart = shopcart.serialize()
        self.assertEqual(serial_shopcart["id"], shopcart.id)
        self.assertEqual(serial_shopcart["name"], shopcart.name)
        self.assertEqual(len(serial_shopcart["items"]), 1)
        items = serial_shopcart["items"]
        self.assertEqual(items[0]["id"], item.id)
        self.assertEqual(items[0]["price"], item.price)
        self.assertEqual(items[0]["quantity"], item.quantity)
        self.assertEqual(items[0]["name"], item.name)
    
    def test_delete_shopcart_item(self):
        """It should Delete a shopcart item"""
        shopcarts = Shopcart.get_all()
        self.assertEqual(shopcarts, [])

        shopcart = ShopcartFactory()
        item = ItemFactory(shopcart=shopcart)
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.get_all()
        self.assertEqual(len(shopcarts), 1)

        # Fetch it back
        shopcart = Shopcart.get_by_id(shopcart.id)
        item = shopcart.items[0]
        item.delete()
        shopcart.update()

        # Fetch it back again
        shopcart = Shopcart.get_by_id(shopcart.id)
        self.assertEqual(len(shopcart.items), 0)