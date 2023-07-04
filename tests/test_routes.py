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
from service.models import db, init_db, Shopcart, Item
from tests.factories import ShopcartFactory, ItemFactory
from . import DATABASE_URI, BASE_URL

from service.models import DataValidationError

NONEXIST_SHOPCART_ID = "0123"


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
            item.shopcart_id = shopcart.id
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

    def test_get_item(self):
        """It should Read an item from a shopcart"""
        test_shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        response = self.client.post(
            f"{BASE_URL}/{test_shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.get_json()
        logging.debug(data)
        item_id = data["id"]

        response = self.client.get(
            f"{BASE_URL}/{test_shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        logging.debug(data)
        self.assertEqual(data["shopcart_id"], test_shopcart.id)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["price"], item.price)
        self.assertEqual(data["name"], item.name)

    def test_get_item_not_found(self):
        """It should not Read an Item that is not found"""
        shopcart = self._create_an_empty_shopcart(1)[0]
        response = self.client.get(f"{BASE_URL}/{shopcart.id}/items/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item_shopcart_not_found(self):
        """It should not Read an Item when the Shopcart is not found"""
        item = ItemFactory()
        response = self.client.get(f"{BASE_URL}/0/items/{item.id}")
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

    def test_add_items_to_shopcart(self):
        """ It should return a list of added items """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data = res.get_json()
        logging.debug(data)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["price"], item.price)
        self.assertEqual(data["shopcart_id"], shopcart.id)

    def test_add_items_to_non_existent_shopcart(self):
        """ It should not read a shopcart that is not found """
        invalid_shopcart = -1
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{invalid_shopcart}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_items_with_invalid_request_body(self):
        """ It should not be added with invalid request body """
        shopcart = self._create_an_empty_shopcart(1)[0]
        res = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json={},  # Empty request body
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_items_with_invalid_data_type(self):
        """ It should not be added with invalid data type """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="text/json",
        )
        self.assertEqual(res.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_add_items_with_invalid_quantity(self):
        """ It should not be added with invalid quantity """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        item.quantity = 0
        res = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch.object(Shopcart, 'get_by_id', MagicMock(side_effect=Exception("DBAPIErr")))
    def test_add_shopcart_items_shopcart_by_id_error(self):
        """ It should get internal server error when add items if there's exception in Shopcart.get_by_id """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('service.models.Shopcart.get_by_id')
    def test_add_shopcart_items_none_items_error(self, mock_shopcart_get_by_id):
        """ It should get internal server error when add items if Shopcart.items is None """
        mock_shopcart = Mock(items=None)
        mock_shopcart_get_by_id.return_value = mock_shopcart
        item = ItemFactory()
        res = self.client.post(
            f"{BASE_URL}/0/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch.object(Shopcart, 'update')
    def test_add_shopcart_items_data_validation_error(self, mock_shopcart_update):
        """It should return a 400 Bad Request response for DataValidationError"""
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()

        # Raise a DataValidationError when calling shopcart.update
        mock_shopcart_update.side_effect = DataValidationError("Invalid data")

        res = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

<<<<<<< HEAD
    def test_update_shopcart_item(self):
        """ It should return the updated item """
=======
    def test_delete_empty_shopcart(self):
        """It should Delete an empty shopcart"""
>>>>>>> 7afb3bd (delete shopcart)
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
<<<<<<< HEAD
        )
        data = res.get_json()
        logging.debug(data)

        # update name
        data["name"] = data["name"] + " II"
        res = self.client.put(
            f'{BASE_URL}/{shopcart.id}/items/{data["id"]}',
            json=data,
            content_type="application/json",
        )
        logging.debug(res.get_json())
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        updated_data = res.get_json()
        self.assertEqual(updated_data["name"], data["name"])
        self.assertEqual(updated_data["quantity"], data["quantity"])
        self.assertEqual(updated_data["price"], data["price"])

        # update quantity
        data["quantity"] = data["quantity"] + 1
        res = self.client.put(
            f'{BASE_URL}/{shopcart.id}/items/{data["id"]}',
            json=data,
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        updated_data = res.get_json()
        self.assertEqual(updated_data["name"], data["name"])
        self.assertEqual(updated_data["quantity"], data["quantity"])
        self.assertEqual(updated_data["price"], data["price"])

        # update price
        data["price"] = data["price"] * 2
        res = self.client.put(
            f'{BASE_URL}/{shopcart.id}/items/{data["id"]}',
            json=data,
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        updated_data = res.get_json()
        self.assertEqual(updated_data["name"], data["name"])
        self.assertEqual(updated_data["quantity"], data["quantity"])
        self.assertEqual(updated_data["price"], data["price"])

    def test_update_shopcart_item_with_invalid_content_type(self):
        """ It should return a 415 Unsupported Media Type response for Content-Type not equal to application/json """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        data = res.get_json()
        logging.debug(data)

        # update name
        data["name"] = data["name"] + " II"
        res = self.client.put(
            f'{BASE_URL}/{shopcart.id}/items/{data["id"]}',
            json=data,
            content_type="application/xml",
        )
        logging.debug(res.get_json())
        self.assertEqual(res.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_shopcart_item_with_invalid_quantity(self):
        """ It should return a 400 Bad Request response for quantity less than 1 """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        data = res.get_json()
        logging.debug(data)

        # update quantity
        data["quantity"] = 0
        res = self.client.put(
            f'{BASE_URL}/{shopcart.id}/items/{data["id"]}',
            json=data,
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_shopcart_item_with_non_existent_shopcart(self):
        """ It should return a 404 Not Found response for non-existent shopcart_id """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        data = res.get_json()
        logging.debug(data)

        # update name
        data["name"] = data["name"] + " II"
        res = self.client.put(
            f'{BASE_URL}/-1/items/{data["id"]}',
            json=data,
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_shopcart_item_with_non_existent_item(self):
        """ It should return a 404 Not Found response for non-existent item """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        data = res.get_json()
        logging.debug(data)

        # update name
        data["name"] = data["name"] + " II"
        res = self.client.put(
            f'{BASE_URL}/{shopcart.id}/items/-1',
            json=data,
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_shopcart_item_with_invalid_request_body(self):
        """ It should return a 404 Not Found response for invalid request body """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        data = res.get_json()
        logging.debug(data)

        # missing name
        no_name_data = data.copy()
        no_name_data.pop("name")
        res = self.client.put(
            f'{BASE_URL}/{shopcart.id}/items/{data["id"]}',
            json=no_name_data,
            content_type="application/json",
        )
        logging.debug(res.get_json())
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # missing quantity
        no_quantity_data = data.copy()
        no_quantity_data.pop("quantity")
        res = self.client.put(
            f'{BASE_URL}/{shopcart.id}/items/{data["id"]}',
            json=no_quantity_data,
            content_type="application/json",
        )
        logging.debug(res.get_json())
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # missing price
        no_price_data = data.copy()
        no_price_data.pop("price")
        res = self.client.put(
            f'{BASE_URL}/{shopcart.id}/items/{data["id"]}',
            json=no_price_data,
            content_type="application/json",
        )
        logging.debug(res.get_json())
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch.object(Item, 'update', MagicMock(side_effect=Exception("DBAPIErr")))
    def test_update_shopcart_item_with_item_update_error(self):
        """ It should return a 500 Internal Server Error response if Item.update() errors """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        data = res.get_json()
        logging.debug(data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # missing name
        data["name"] = data["name"] + " II"
        res = self.client.put(
            f'{BASE_URL}/{shopcart.id}/items/{data["id"]}',
            json=data,
            content_type="application/json",
        )
        logging.debug(res.get_json())
        self.assertEqual(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_update_shopcart_item_with_none_shopcart(self):
        """ It should return a 404 Not Found response when shopcart is None """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        data = res.get_json()
        logging.debug(data)

        with patch('service.models.Shopcart.get_by_id', return_value=None):
            # update name
            data["name"] = data["name"] + " II"
            res = self.client.put(
                f'{BASE_URL}/{shopcart.id}/items/{data["id"]}',
                json=data,
                content_type="application/json",
            )
            self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_item(self):
        """It should Delete an Item"""
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # send delete request
        resp = self.client.delete(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure item is not there
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_not_found(self):
        """It should not Delete an Item that is not found"""
        shopcart = self._create_an_empty_shopcart(1)[0]
        response = self.client.delete(f"{BASE_URL}/{shopcart.id}/items/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_shopcart_item_with_none_shopcart(self):
        """ It should return a 404 Not Found response when shopcart is None """
        shopcart = self._create_an_empty_shopcart(1)[0]
=======
            )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data = res.get_json()
        logging.debug(data)
        shopcart_id = data["id"]
        res = self.client.delete(f"{BASE_URL}/{shopcart_id}")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        res = self.client.get(f"{BASE_URL}/{shopcart_id}")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonempty_shopcart(self):
        """It should Delete a nonempty shopcart"""
        shopcart = self._create_a_shopcart_with_items(1)
>>>>>>> 7afb3bd (delete shopcart)
        item = ItemFactory()
        res = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
<<<<<<< HEAD
        data = res.get_json()
        logging.debug(data)

        with patch('service.models.Shopcart.get_by_id', return_value=None):
            res = self.client.delete(
            f"{BASE_URL}/{shopcart.id}/items/{item.id}",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        
=======
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data = res.get_json()
        logging.debug(data)
        shopcart_id = data["id"]
        res = self.client.delete(f"{BASE_URL}/{shopcart_id}")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # Make sure shopcart is deleted
        res = self.client.get(f"{BASE_URL}/{shopcart_id}")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_invalid_shopcart(self):
        """It Should Delete an non-existing shopcart"""
        res = self.client.delete(f"{BASE_URL}/{NONEXIST_SHOPCART_ID}")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
>>>>>>> 7afb3bd (delete shopcart)
