"""
Test cases for Shopcart Model

"""
import logging
import unittest


from service import app
from service.models import Shopcart, Item, DataValidationError, db
from tests.factories import ShopcartFactory,ItemFactory

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

     ######################################################################
    #  TEST CREATE / ADD SHOPCART
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
