"""
Shopcarts API Service Test Suite

Test cases can be run with the following:
  green
  coverage report -m
"""
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch

from service import app
from service.common import status  # HTTP Status Codes
from service.models import db, init_db, Shopcart
from tests.factories import ShopcartFactory, ItemFactory
from . import DATABASE_URI, BASE_URL


class TestShopcartsService(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_an_empty_shopcart(self, shopcart_count):
        """ Factory method to create empty shopcarts """
        shopcarts = list()
        for _ in range(shopcart_count):
            shopcart = ShopcartFactory()
            resp = self.client.post(
                BASE_URL, json=shopcart.serialize(), content_type="application/json")
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Shopcart",
            )
            new_shopcart = resp.get_json()
            shopcart.id = new_shopcart["id"]
            shopcart.name = new_shopcart["name"]
            logging.info(f"{shopcart.__repr__()} created for test")
            shopcarts.append(shopcart)
        return shopcarts

    # TODO: add different types of item to shopcart
    def _create_a_shopcart_with_items(self, item_count):
        """ Factory method to create a shopcart with items """
        shopcart = self._create_an_empty_shopcart(1)[0]
        for _ in range(item_count):
            item = ItemFactory()
            resp = self.client.post(
                f"{BASE_URL}/{shopcart.id}/items", json=item.serialize(), content_type="application/json")
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Item",
            )
            shopcart.items.append(item)
            logging.info(f"{item.__repr__()} created for test")
        return shopcart

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_shopcart(self):
        """It should Read a single Shopcart"""
        # get the id of a shopcart
        test_shopcart = self._create_an_empty_shopcart(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{test_shopcart.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], test_shopcart.id)

    def test_get_shopcart_not_found(self):
        """It should not Read an Shopcart that is not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # @patch.object(Shopcart, 'get_by_id', MagicMock(side_effect=Exception("DBAPIErr")))
    # def test_list_shopcart_items_shopcart_get_by_id_error(self):
    #     """ It should get internal server error if there's exception in Shopcart.get_by_id """
    #     resp = self.client.get(f"{BASE_URL}/0/items")
    #     self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


    # def test_create_shopcart(self):
    #     """It should Create a new Shopcart"""
    #     shopcart = ShopcartFactory()
    #     resp = self.client.post(
    #         BASE_URL, json=shopcart.serialize(), content_type="application/json"
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    #     # Make sure location header is set
    #     location = resp.headers.get("Location", None)
    #     self.assertIsNotNone(location)

    #     # Check the data is correct
    #     new_shopcart = resp.get_json()
    #     self.assertEqual(new_shopcart["name"], shopcart.name, "Names does not match")
        

    #     # Check that the location header was correct by getting it
    #     resp = self.client.get(location, content_type="application/json")
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     new_shopcart = resp.get_json()
    #     self.assertEqual(new_shopcart["name"], shopcart.name, "Names does not match")
    

    # def test_create_shopcarts(self):
    #     """ It should create an shopcart """
    #     shopcart = ShopcartFactory()
    #     resp = self.client.post(
    #         f"{BASE_URL}",json = shopcart.serialize(), content_type = "application/json"
    #     )
        
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        

    #     location = resp.headers.get("location", None)
    #     self.assertIsNotNone(location)

    #     new_shopcart = resp.get_json()
    #     # self.assertEqual(data["date"], shopcart.date,"date does not match")
    #     self.assertEqual(new_shopcart["name"],shopcart.name, "name does not match")
        

    def test_create_shopcart_missing_info(self):
        """
        It should fail if the call has some missing information.
        """
        resp = self.client.post(
            f"{BASE_URL}",
            json={
                "items": []
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

       

    # def test_get_item(self):
    #     """It should Read an item from a shopcart"""

    #     test_shopcart = self._create_shopcarts(1)
    #     item = ItemFactory()
    #     response = self.client.post(
    #         f"{BASE_URL}/{test_shopcart.customer_id}/items",
    #         json=item.serialize(),
    #         content_type="application/json",
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     data = response.get_json()
    #     logging.debug(data)
    #     item_id = data["id"]

    #     resp = self.client.get(
    #         f"{BASE_URL}/{test_shopcart.customer_id}/items/{item_id}",
    #         content_type="application/json",
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)

    #     data = resp.get_json()
    #     logging.debug(data)
    #     self.assertEqual(data["shopcart_id"], test_shopcart.customer_id)
    #     self.assertEqual(data["id"], item.item_id)

    #      # retrieve it back and make sure address is not there
    #     resp = self.client.get(
    #         f"{BASE_URL}/{test_shopcart.customer_id}/items/{item_id}",
    #         content_type="application/json",
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
