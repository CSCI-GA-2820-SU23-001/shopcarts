"""
Shopcarts API Service Test Suite

Test cases can be run with the following:
  green
  coverage report -m
"""
import logging
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

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
        """It should not Read a Shopcart that is not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

   
    def test_list_empty_shopcart_items(self):
        """ It should get an empty list of items """
        shopcart = self._create_an_empty_shopcart(1)[0]
        resp = self.client.get(f"{BASE_URL}/{shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_list_shopcart_items(self):
        """ It should get a list of only one item """
        shopcart = self._create_a_shopcart_with_items(1)
        resp = self.client.get(f"{BASE_URL}/{shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)

    def test_list_items_in_non_existent_shopcart(self):
        """ It should not read a shopcart that is not found """
        shopcart_id = -1
        resp = self.client.get(f"{BASE_URL}/{shopcart_id}/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch.object(Shopcart, 'get_by_id', MagicMock(side_effect=Exception("DBAPIErr")))
    def test_list_shopcart_items_shopcart_get_by_id_error(self):
        """ It should get internal server error if there's exception in Shopcart.get_by_id """
        resp = self.client.get(f"{BASE_URL}/0/items")
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('service.models.Shopcart.get_by_id')
    def test_list_shopcart_items_none_items_error(self, mock_shopcart_get_by_id):
        """ It should get internal server error if Shopcart.items is None """
        mock_shopcart = Mock(items=None)
        mock_shopcart_get_by_id.return_value = mock_shopcart
        resp = self.client.get(f"{BASE_URL}/0/items")
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
