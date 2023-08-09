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
from service.models import DataValidationError
from service.models import db, init_db, Shopcart, Item
from tests.factories import ShopcartFactory, ItemFactory
from . import DATABASE_URI, BASE_URL, BASE_URL_RESTX

NONEXIST_SHOPCART_ID = "0123"


class BaseTestCase(TestCase):
    """ Base setups and teardowns for tests """
    base_url = BASE_URL
    base_url_restx = BASE_URL_RESTX

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
        shopcarts = []
        for _ in range(shopcart_count):
            shopcart = ShopcartFactory()
            resp = self.client.post(
                self.base_url, json=shopcart.serialize(), content_type="application/json")
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Shopcart",
            )
            new_shopcart = resp.get_json()
            shopcart.id = new_shopcart["id"]
            shopcart.name = new_shopcart["name"]
            logging.info("%s created for test", repr(shopcart))
            shopcarts.append(shopcart)
        return shopcarts

    def _create_a_shopcart_with_items(self, item_count):
        """ Factory method to create a shopcart with items """
        shopcart = self._create_an_empty_shopcart(1)[0]
        for _ in range(item_count):
            item = ItemFactory()
            resp = self.client.post(
                f"{self.base_url}/{shopcart.id}/items", json=item.serialize(), content_type="application/json")
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Item",
            )
            shopcart.items.append(item)
            item.shopcart_id = shopcart.id
            logging.info("%s created for test", repr(item))
        return shopcart


# pylint: disable=R0904
class TestShopcartsService(BaseTestCase):
    """ REST API Server Tests """

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], "OK")

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_shopcartsapi(self):
        """ It should call the shopcarts.html"""
        resp = self.client.get("/shopcartsapi")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_itemsapi(self):
        """ It should call the items.html"""
        resp = self.client.get("/itemsapi")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_shopcart(self):
        """It should Read a single Shopcart"""
        # get the id of a shopcart
        test_shopcart = self._create_an_empty_shopcart(1)[0]
        resp = self.client.get(
            f"{self.base_url}/{test_shopcart.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], test_shopcart.id)

    def test_get_shopcart_not_found(self):
        """It should not Read a Shopcart that is not found"""
        response = self.client.get(f"{self.base_url}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item(self):
        """It should Read an item from a shopcart"""
        test_shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        response = self.client.post(
            f"{self.base_url}/{test_shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.get_json()
        logging.debug(data)
        item_id = data["id"]

        response = self.client.get(
            f"{self.base_url}/{test_shopcart.id}/items/{item_id}",
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
        response = self.client.get(f"{self.base_url}/{shopcart.id}/items/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item_shopcart_not_found(self):
        """It should not Read an Item when the Shopcart is not found"""
        item = ItemFactory()
        response = self.client.get(f"{self.base_url}/0/items/{item.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_empty_shopcart_items(self):
        """ It should get an empty list of items """
        shopcart = self._create_an_empty_shopcart(1)[0]
        resp = self.client.get(f"{self.base_url}/{shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_list_shopcart_items(self):
        """ It should get a list of only one item """
        shopcart = self._create_a_shopcart_with_items(1)
        resp = self.client.get(f"{self.base_url}/{shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)

    def test_list_items_in_non_existent_shopcart(self):
        """ It should not read a shopcart that is not found """
        shopcart_id = -1
        resp = self.client.get(f"{self.base_url}/{shopcart_id}/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_shopcart_items_shopcart_get_by_id_error(self):
        """ It should get internal server error if shopcart is none """
        with patch('service.models.Shopcart.get_by_id', return_value=None):
            resp = self.client.get(f"{self.base_url}/0/items")
            self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_shopcarts(self):
        """It should return all shopcarts"""
        self._create_an_empty_shopcart(5)
        resp = self.client.get(f"{self.base_url}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_list_empty_shopcarts(self):
        """It should not return any shopcart"""
        resp = self.client.get(f"{self.base_url}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_list_shopcarts_with_items(self):
        """It should return all shopcarts with corresponding items"""
        shopcart_a = self._create_a_shopcart_with_items(1)
        self._create_a_shopcart_with_items(2)
        self._create_a_shopcart_with_items(3)
        self._create_an_empty_shopcart(5)
        resp = self.client.get(f"{self.base_url}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(type(shopcart_a), Shopcart)
        data = resp.get_json()
        self.assertEqual(len(data), Shopcart.find_id())

    def test_list_shopcart_of_a_customer(self):
        """It should return a shopcart within a specific customer"""
        shopcart_a = self._create_a_shopcart_with_items(1)
        self.assertEqual(type(shopcart_a.name), str)
        name = Shopcart.find_by_name(shopcart_a.name)
        test_shopcart = name.scalar()
        url = self.base_url + "?name=" + shopcart_a.name
        resp = self.client.get(f"{url}")
        data = resp.get_json()
        self.assertEqual(type(data[0]['name']), str)
        self.assertEqual(data[0]['name'], test_shopcart.name)

    def test_add_items(self):
        """ It should return a list of added items """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{self.base_url}/{shopcart.id}/items",
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
        shopcart = self._create_an_empty_shopcart(1)[0]
        test_id = shopcart.id + 1
        item = ItemFactory(shopcart_id=test_id)
        self.assertNotEqual(test_id, shopcart.id)
        resp = self.client.post(
            f"{self.base_url}/{test_id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_items_with_invalid_request_body(self):
        """ It should not be added with invalid request body """
        shopcart = self._create_an_empty_shopcart(1)[0]
        res = self.client.post(
            f"{self.base_url}/{shopcart.id}/items",
            json={},  # Empty request body
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_items_with_invalid_content_type(self):
        """ It should not be added with invalid content type """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()

        res = self.client.post(
            f"{self.base_url}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="",
        )
        self.assertEqual(res.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        res = self.client.post(
            f"{self.base_url}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/xml",
        )
        self.assertEqual(res.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    @patch.object(Shopcart, 'update')
    def test_add_items_with_data_validation_error(self, mock_shopcart_update):
        """It should return a 400 Bad Request response for DataValidationError"""
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()

        # Raise a DataValidationError when calling shopcart.update
        mock_shopcart_update.side_effect = DataValidationError("Invalid data")

        res = self.client.post(
            f"{self.base_url}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_items_with_empty_name(self):
        """It should return Shopcart with id='{shopcart_id}' was not found"""
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory(shopcart_id=shopcart.id)
        item.name = ""
        resp = self.client.post(f"{self.base_url}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        item.name = "  "
        resp = self.client.post(f"{self.base_url}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_items_with_null_name(self):
        """It should return Shopcart with id='{shopcart_id}' was not found"""
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory(shopcart_id=shopcart.id)
        item.name = None
        resp = self.client.post(f"{self.base_url}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_items_with_invalid_quantity(self):
        """It should return Shopcart with id='{shopcart_id}' was not found"""
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory(shopcart_id=shopcart.id)
        item.quantity = "Z"
        resp = self.client.post(f"{self.base_url}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        item.quantity = 1.2
        resp = self.client.post(f"{self.base_url}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        item.quantity = 2
        resp = self.client.post(f"{self.base_url}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_items_with_invalid_price(self):
        """It should return Shopcart with id='{shopcart_id}' was not found"""
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory(shopcart_id=shopcart.id)
        item.price = "Z"
        resp = self.client.post(f"{self.base_url}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        item.price = 100.0
        resp = self.client.post(f"{self.base_url}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_update_name_of_shopcart(self):
        """It should return the shopcart within updated name"""
        test_shopcart = ShopcartFactory()
        resp = self.client.post(self.base_url, json=test_shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_shopcart = resp.get_json()
        new_shopcart["name"] = "DevOps"
        new_shopcart_id = new_shopcart["id"]
        resp = self.client.put(f"{self.base_url}/{new_shopcart_id}", json=new_shopcart)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_shopcart = resp.get_json()
        self.assertEqual(updated_shopcart["name"], "DevOps")

    def test_update_non_existent_shopcart(self):
        """It should return a 404 not Found response for non-existent shopcart"""
        shopcart = ShopcartFactory()
        resp = self.client.post(self.base_url, json=shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_shopcart = resp.get_json()
        new_shopcart["name"] = "DevOps"

        resp = self.client.put(
            f"{self.base_url}/-1",
            json=new_shopcart,
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_shopcart_with_invalid_request_body(self):
        """It should return a 404 Not Found response for invalid request body"""
        shopcart = ShopcartFactory()
        resp = self.client.post(self.base_url, json=shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_shopcart = resp.get_json()
        new_shopcart["name"] = "DevOps"
        resp = self.client.put(
            f"{self.base_url}/{new_shopcart['id']}",
            json=new_shopcart['items'],
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_shopcart_item(self):
        """ It should return the updated item """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{self.base_url}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        data = res.get_json()
        logging.debug(data)

        # update name
        data["name"] = data["name"] + " II"
        res = self.client.put(
            f'{self.base_url}/{shopcart.id}/items/{data["id"]}',
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
            f'{self.base_url}/{shopcart.id}/items/{data["id"]}',
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
            f'{self.base_url}/{shopcart.id}/items/{data["id"]}',
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
            f"{self.base_url}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        data = res.get_json()
        logging.debug(data)

        # update name
        data["name"] = data["name"] + " II"
        res = self.client.put(
            f'{self.base_url}/{shopcart.id}/items/{data["id"]}',
            json=data,
            content_type="",
        )
        self.assertEqual(res.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        res = self.client.put(
            f'{self.base_url}/{shopcart.id}/items/{data["id"]}',
            json=data,
            content_type="application/xml",
        )
        self.assertEqual(res.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_shopcart_item_with_invalid_quantity(self):
        """ It should return a 400 Bad Request response for quantity less than 1 """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{self.base_url}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        data = res.get_json()
        logging.debug(data)

        # update quantity
        data["quantity"] = 0
        res = self.client.put(
            f'{self.base_url}/{shopcart.id}/items/{data["id"]}',
            json=data,
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_shopcart_item_with_non_existent_shopcart(self):
        """ It should return a 404 Not Found response for non-existent shopcart_id """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{self.base_url}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        data = res.get_json()
        logging.debug(data)

        # update name
        data["name"] = data["name"] + " II"
        res = self.client.put(
            f'{self.base_url}/-1/items/{data["id"]}',
            json=data,
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_shopcart_item_with_non_existent_item(self):
        """ It should return a 404 Not Found response for non-existent item """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{self.base_url}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        data = res.get_json()
        logging.debug(data)

        # update name
        data["name"] = data["name"] + " II"
        res = self.client.put(
            f'{self.base_url}/{shopcart.id}/items/{item.id + 10000}',
            json=data,
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_shopcart_item_with_invalid_request_body(self):
        """ It should return a 404 Not Found response for invalid request body """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{self.base_url}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        data = res.get_json()
        logging.debug(data)

        # missing name
        no_name_data = data.copy()
        no_name_data.pop("name")
        res = self.client.put(
            f'{self.base_url}/{shopcart.id}/items/{data["id"]}',
            json=no_name_data,
            content_type="application/json",
        )
        logging.debug(res.get_json())
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # missing quantity
        no_quantity_data = data.copy()
        no_quantity_data.pop("quantity")
        res = self.client.put(
            f'{self.base_url}/{shopcart.id}/items/{data["id"]}',
            json=no_quantity_data,
            content_type="application/json",
        )
        logging.debug(res.get_json())
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # missing price
        no_price_data = data.copy()
        no_price_data.pop("price")
        res = self.client.put(
            f'{self.base_url}/{shopcart.id}/items/{data["id"]}',
            json=no_price_data,
            content_type="application/json",
        )
        logging.debug(res.get_json())
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch.object(Item, 'update', MagicMock(side_effect=DataValidationError))
    def test_update_shopcart_item_with_item_update_error(self):
        """ It should return a 500 Internal Server Error response if Item.update() errors """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{self.base_url}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        data = res.get_json()
        logging.debug(data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # missing name
        data["name"] = data["name"] + " II"
        res = self.client.put(
            f'{self.base_url}/{shopcart.id}/items/{data["id"]}',
            json=data,
            content_type="application/json",
        )
        logging.debug(res.get_json())
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_shopcart_item_with_none_shopcart(self):
        """ It should return a 404 Not Found response when shopcart is None """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{self.base_url}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        data = res.get_json()
        logging.debug(data)

        with patch('service.models.Shopcart.get_by_id', return_value=None):
            # update name
            data["name"] = data["name"] + " II"
            res = self.client.put(
                f'{self.base_url}/{shopcart.id}/items/{data["id"]}',
                json=data,
                content_type="application/json",
            )
            self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_clear_empty_shopcart(self):
        """ It should clear the items but not delete the shopcart """
        shopcart = self._create_an_empty_shopcart(1)[0]
        res = self.client.put(
            f'{self.base_url}/{shopcart.id}/clear'
            )
        logging.debug(res)
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # was the PUT rqst to clear successful
        res = self.client.get(f'{self.base_url}/{shopcart.id}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # was the GET rqst successful
        data = res.get_json()
        logging.debug(data)
        self.assertEqual(data['id'], shopcart.id)  # is the id of the shopcart we got the same as the one we created
        self.assertEqual(data['items'], [])  # is the items list empty

    def test_clear_shopcart_with_items(self):
        """ It should clear the items but not delete the shopcart """
        shopcart = self._create_a_shopcart_with_items(3)
        res = self.client.get(
            f'{self.base_url}/{shopcart.id}'
        )
        data = res.get_json()
        logging.debug(data)
        print(data)  # should have 3 items
        res = self.client.put(
            f'{self.base_url}/{shopcart.id}/clear'
        )
        logging.debug(res)
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # was the PUT rqst to clear successful
        res = self.client.get(f'{self.base_url}/{shopcart.id}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # was the GET rqst successful
        data = res.get_json()
        logging.debug(data)
        print("after: ", data)  # should be empty list
        self.assertEqual(data['id'], shopcart.id)  # is the id of the shopcart we got the same as the one we created
        self.assertEqual(data['items'], [])  # is the items list empty

    def test_clear_shopcart_not_found(self):
        """It should return a 404 not Found response for non-existent shopcart"""
        shopcart = self._create_an_empty_shopcart(1)[0]
        test_id = shopcart.id + 1
        self.assertNotEqual(test_id, shopcart.id)  # check mock id is diff from created id
        res = self.client.put(
            f'{self.base_url}/{test_id}/clear'
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item(self):
        """It should Delete an Item"""
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{self.base_url}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # send delete request
        resp = self.client.delete(
            f"{self.base_url}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure item is not there
        resp = self.client.get(
            f"{self.base_url}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_empty_shopcart(self):
        """It should Delete an empty shopcart"""
        shopcart = self._create_an_empty_shopcart(1)[0]
        res = self.client.delete(f"{self.base_url}/{shopcart.id}")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        res = self.client.get(f"{self.base_url}/{shopcart.id}")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonempty_shopcart(self):
        """It should Delete a nonempty shopcart"""
        shopcart = self._create_a_shopcart_with_items(1)
        res = self.client.delete(f"{self.base_url}/{shopcart.id}")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # Make sure shopcart is deleted
        res = self.client.get(f"{self.base_url}/{shopcart.id}")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_invalid_shopcart(self):
        """It Should Delete an non-existing shopcart"""
        res = self.client.delete(f"{self.base_url}/{NONEXIST_SHOPCART_ID}")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_unsupported_method_on_shopcart(self):
        """It should return a 405 Method Not Supported response"""
        self._create_an_empty_shopcart(5)
        resp = self.client.put(f"{self.base_url}")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_shopcarts(self):
        """ It should return a 415 Unsupported media type """
        shopcart = ShopcartFactory()
        resp = self.client.post(
            self.base_url,
            json=shopcart.serialize(),
            content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_shopcarts_with_invalid_content_type(self):
        """ It should return a 415 Unsupported media type """
        shopcart = ShopcartFactory()
        resp = self.client.post(f"{self.base_url}",
                                json=shopcart.serialize(),
                                content_type="")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        resp = self.client.post(f"{self.base_url}",
                                json=shopcart.serialize(),
                                content_type="application/xml")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_a_shopcart_with_empty_name(self):
        """ It should return a 400 Bad request response when shopcart name is empty """
        shopcart = ShopcartFactory()
        shopcart.name = ""
        resp = self.client.post(f"{self.base_url}",
                                json=shopcart.serialize(),
                                content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        shopcart.name = "  "
        resp = self.client.post(f"{self.base_url}",
                                json=shopcart.serialize(),
                                content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_a_shopcart_with_null_name(self):
        """ It should return a 400 Bad request response when shopcart name is null """
        shopcart = ShopcartFactory()
        shopcart.name = None
        resp = self.client.post(f"{self.base_url}",
                                json=shopcart.serialize(),
                                content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_a_shopcart_with_bad_request(self):
        """It should return a 400 Bad request response"""
        shopcart = ShopcartFactory()
        resp = self.client.post(f"{self.base_url}",
                                json=shopcart.serialize()['name'],
                                content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_a_nonexistent_shopcart(self):
        """It should return a 404 Not found response"""
        shopcart = self._create_an_empty_shopcart(1)[0]
        test_id = shopcart.id + 1
        self.assertNotEqual(test_id, shopcart.id)
        resp = self.client.put(f"{self.base_url}/{test_id}",
                               json=shopcart.serialize(),
                               content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_a_shopcart_with_invalid_content_type(self):
        """It should return a 415 Unsupported Media Type response when the given Content-Type is no application/json"""
        shopcart = self._create_an_empty_shopcart(1)[0]
        self.assertNotEqual(shopcart.name, "DevOps")
        shopcart.name = "DevOps"
        self.assertEqual(shopcart.name, "DevOps")

        resp = self.client.put(f"{self.base_url}/{shopcart.id}",
                               json=shopcart.serialize(),
                               content_type="")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        resp = self.client.put(f"{self.base_url}/{shopcart.id}",
                               json=shopcart.serialize(),
                               content_type="application/xml")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_list_items_of_nonexistent_shopcart(self):
        """It should return a 404 Not found response"""
        shopcart = self._create_an_empty_shopcart(1)[0]
        # item = ItemFactory(shopcart_id = shopcart.id)
        test_id = shopcart.id + 1
        resp = self.client.get(f"{self.base_url}/{test_id}/items",
                               json=shopcart.serialize(),
                               content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
