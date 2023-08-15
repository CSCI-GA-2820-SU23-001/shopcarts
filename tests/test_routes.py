"""
Shopcarts API Service Test Suite

Test cases can be run with the following:
  green
  coverage report -m
"""
import logging
from unittest import TestCase
from unittest.mock import patch

from service import app
from service.common import status  # HTTP Status Codes
from service.models import db, init_db, Shopcart
from tests.factories import ShopcartFactory, ItemFactory
from . import DATABASE_URI, BASE_URL_RESTX, DEFAULT_CONTENT_TYPE


class BaseTestCase(TestCase):
    """ Base setups and teardowns for tests """
    base_url_restx = BASE_URL_RESTX

    @classmethod
    def setUpClass(cls):
        """ Run once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ Run once after the entire test suite """
        db.session.close()

    def setUp(self):
        """Run before each test"""
        self.client = app.test_client()
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ Run after each test """
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
                self.base_url_restx, json=shopcart.serialize(), content_type=DEFAULT_CONTENT_TYPE)
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
                f"{self.base_url_restx}/{shopcart.id}/items", json=item.serialize(), content_type=DEFAULT_CONTENT_TYPE)
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
    """ Shopcarts Service Tests """

    def test_index(self):
        """ GET / should return index.html """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_shopcartsapi(self):
        """ GET /shopcartsapi should return shopcarts.html """
        resp = self.client.get("/shopcartsapi")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_itemsapi(self):
        """ GET /itemsapi should return items.html """
        resp = self.client.get("/itemsapi")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_health(self):
        """ [HTTP_200_OK] GET /health """
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], "OK")

    #################################################
    # S H O P C A R T   A P I   T E S T   C A S E S #
    #################################################

    def test_list_shopcarts(self):
        """ [HTTP_200_OK] GET /shopcarts """
        # list shopcarts when there's none
        resp = self.client.get(f"{self.base_url_restx}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

        # list shopcarts when there's one empty without any item
        self._create_an_empty_shopcart(5)
        resp = self.client.get(f"{self.base_url_restx}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

        # list shopcarts with items
        shopcart_a = self._create_a_shopcart_with_items(1)
        resp = self.client.get(f"{self.base_url_restx}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(type(shopcart_a), Shopcart)
        data = resp.get_json()
        self.assertEqual(len(data), 6)

        # list shopcarts with name filter
        resp = self.client.get(f"{self.base_url_restx}?name={shopcart_a.name}")
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], shopcart_a.name)

    def test_create_shopcarts(self):
        """ [HTTP_201_CREATED] POST /shopcarts """
        shopcart = ShopcartFactory()
        resp = self.client.post(
            self.base_url_restx,
            json=shopcart.serialize(),
            content_type=DEFAULT_CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_shopcarts_415(self):
        """ [HTTP_415_UNSUPPORTED_MEDIA_TYPE] POST /shopcarts """
        shopcart = ShopcartFactory()
        resp = self.client.post(f"{self.base_url_restx}",
                                json=shopcart.serialize(),
                                content_type="")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        resp = self.client.post(f"{self.base_url_restx}",
                                json=shopcart.serialize(),
                                content_type="application/xml")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_shopcarts_400(self):
        """ [HTTP_400_BAD_REQUEST] POST /shopcarts """
        # create a shopcart with invalid request body
        resp = self.client.post(f"{self.base_url_restx}",
                                json={},
                                content_type=DEFAULT_CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # create a shopcart with empty name
        shopcart = ShopcartFactory()
        shopcart.name = ""
        resp = self.client.post(f"{self.base_url_restx}",
                                json=shopcart.serialize(),
                                content_type=DEFAULT_CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        shopcart.name = "  "
        resp = self.client.post(f"{self.base_url_restx}",
                                json=shopcart.serialize(),
                                content_type=DEFAULT_CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # create a shopcart with null name
        shopcart = ShopcartFactory()
        shopcart.name = None
        resp = self.client.post(f"{self.base_url_restx}",
                                json=shopcart.serialize(),
                                content_type=DEFAULT_CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_shopcarts(self):
        """ [HTTP_200_OK] GET /shopcarts/{shopcart_id} """
        # get the id of a shopcart
        test_shopcart = self._create_an_empty_shopcart(1)[0]
        resp = self.client.get(
            f"{self.base_url_restx}/{test_shopcart.id}", content_type=DEFAULT_CONTENT_TYPE
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], test_shopcart.id)

    def test_get_shopcarts_404(self):
        """ [HTTP_404_NOT_FOUND] GET /shopcarts/{shopcart_id} """
        response = self.client.get(f"{self.base_url_restx}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_shopcarts(self):
        """ [HTTP_200_OK] PUT /shopcarts/{shopcart_id} """
        test_shopcart = ShopcartFactory()
        resp = self.client.post(self.base_url_restx, json=test_shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_shopcart = resp.get_json()
        new_shopcart["name"] = "DevOps"
        new_shopcart_id = new_shopcart["id"]
        resp = self.client.put(f"{self.base_url_restx}/{new_shopcart_id}", json=new_shopcart)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_shopcart = resp.get_json()
        self.assertEqual(updated_shopcart["name"], "DevOps")

    def test_update_shopcarts_404(self):
        """ [HTTP_404_NOT_FOUND] PUT /shopcarts/{shopcart_id} """
        shopcart = ShopcartFactory()
        resp = self.client.post(self.base_url_restx, json=shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_shopcart = resp.get_json()
        new_shopcart["name"] = "DevOps"

        resp = self.client.put(
            f"{self.base_url_restx}/-1",
            json=new_shopcart,
            content_type=DEFAULT_CONTENT_TYPE
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_shopcarts_400(self):
        """ [HTTP_400_BAD_REQUEST] PUT /shopcarts/{shopcart_id} """
        shopcart = ShopcartFactory()
        resp = self.client.post(self.base_url_restx, json=shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_shopcart = resp.get_json()
        new_shopcart["name"] = "DevOps"
        resp = self.client.put(
            f"{self.base_url_restx}/{new_shopcart['id']}",
            json=new_shopcart['items'],
            content_type=DEFAULT_CONTENT_TYPE
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_shopcarts_415(self):
        """ [HTTP_415_UNSUPPORTED_MEDIA_TYPE] PUT /shopcarts/{shopcart_id} """
        shopcart = self._create_an_empty_shopcart(1)[0]
        self.assertNotEqual(shopcart.name, "DevOps")
        shopcart.name = "DevOps"
        self.assertEqual(shopcart.name, "DevOps")

        resp = self.client.put(f"{self.base_url_restx}/{shopcart.id}",
                               json=shopcart.serialize(),
                               content_type="")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        resp = self.client.put(f"{self.base_url_restx}/{shopcart.id}",
                               json=shopcart.serialize(),
                               content_type="application/xml")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_delete_shopcarts(self):
        """ [HTTP_204_NO_CONTENT] DELETE /shopcarts/{shopcart_id} """
        shopcart = self._create_an_empty_shopcart(1)[0]

        res = self.client.delete(f"{self.base_url_restx}/{shopcart.id}")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        res = self.client.get(f"{self.base_url_restx}/{shopcart.id}")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_clear_shopcarts(self):
        """ [HTTP_200_OK] PUT /shopcarts/{shopcart_id}/clear """
        # clear an empty shopcart
        shopcart = self._create_an_empty_shopcart(1)[0]
        res = self.client.put(f'{self.base_url_restx}/{shopcart.id}/clear')

        self.assertEqual(res.status_code, status.HTTP_200_OK)  # was the PUT rqst to clear successful
        res = self.client.get(f'{self.base_url_restx}/{shopcart.id}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # was the GET rqst successful

        data = res.get_json()
        self.assertEqual(data['id'], shopcart.id)  # is the id of the shopcart we got the same as the one we created
        self.assertEqual(len(data['items']), 0)  # is the items list empty

        # clear a shopcart with items
        shopcart = self._create_a_shopcart_with_items(3)
        res = self.client.get(f'{self.base_url_restx}/{shopcart.id}')

        res = self.client.put(f'{self.base_url_restx}/{shopcart.id}/clear')
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # was the PUT rqst to clear successful

        res = self.client.get(f'{self.base_url_restx}/{shopcart.id}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # was the GET rqst successful

        data = res.get_json()
        self.assertEqual(data['id'], shopcart.id)  # is the id of the shopcart we got the same as the one we created
        self.assertEqual(len(data['items']), 0)  # is the items list empty

    def test_clear_shopcarts_404(self):
        """ [HTTP_404_NOT_FOUND] PUT /shopcarts/{shopcart_id}/clear """
        shopcart = self._create_an_empty_shopcart(1)[0]
        test_id = shopcart.id + 1
        self.assertNotEqual(test_id, shopcart.id)  # check mock id is diff from created id
        res = self.client.put(f'{self.base_url_restx}/{test_id}/clear')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    #########################################
    # I T E M   A P I   T E S T   C A S E S #
    #########################################

    def test_list_items(self):
        """ [HTTP_200_OK] GET /shopcarts/{shopcart_id}/items """
        # list a shopcart with items
        shopcart = self._create_a_shopcart_with_items(1)
        resp = self.client.get(f"{self.base_url_restx}/{shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)

        # list a shopcart without items
        shopcart = self._create_an_empty_shopcart(1)[0]
        resp = self.client.get(f"{self.base_url_restx}/{shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_list_items_404(self):
        """ [HTTP_404_NOT_FOUND] GET /shopcarts/{shopcart_id}/items """
        shopcart = self._create_an_empty_shopcart(1)[0]
        test_id = shopcart.id + 1
        resp = self.client.get(f"{self.base_url_restx}/{test_id}/items",
                               json=shopcart.serialize(),
                               content_type=DEFAULT_CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # assumed Shopcart.get_by_id() error
        with patch('service.models.Shopcart.get_by_id', return_value=None):
            resp = self.client.get(f"{self.base_url_restx}/0/items")
            self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_items(self):
        """ [HTTP_201_CREATED] POST /shopcarts/{shopcart_id}/items """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{self.base_url_restx}/{shopcart.id}/items",
            json=item.serialize(),
            content_type=DEFAULT_CONTENT_TYPE,
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data = res.get_json()
        logging.debug(data)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["price"], item.price)
        self.assertEqual(data["shopcart_id"], shopcart.id)

    def test_create_items_404(self):
        """ [HTTP_404_NOT_FOUND] POST /shopcarts/{shopcart_id}/items """
        shopcart = self._create_an_empty_shopcart(1)[0]
        test_id = shopcart.id + 1
        item = ItemFactory(shopcart_id=test_id)
        self.assertNotEqual(test_id, shopcart.id)
        resp = self.client.post(
            f"{self.base_url_restx}/{test_id}/items",
            json=item.serialize(),
            content_type=DEFAULT_CONTENT_TYPE,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_items_400(self):
        """ [HTTP_400_BAD_REQUEST] POST /shopcarts/{shopcart_id}/items """
        # add an item with an empty request body
        shopcart = self._create_an_empty_shopcart(1)[0]
        res = self.client.post(
            f"{self.base_url_restx}/{shopcart.id}/items",
            json={},
            content_type=DEFAULT_CONTENT_TYPE,
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # add an item with missing field in request body
        item = ItemFactory(shopcart_id=shopcart.id)
        item.price = None
        res = self.client.post(
            f"{self.base_url_restx}/{shopcart.id}/items",
            json=item.serialize(),
            content_type=DEFAULT_CONTENT_TYPE,
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # add an item with empty name
        item.name = ""
        resp = self.client.post(f"{self.base_url_restx}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type=DEFAULT_CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        item.name = "  "
        resp = self.client.post(f"{self.base_url_restx}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type=DEFAULT_CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # add an item with null name
        item.name = None
        resp = self.client.post(f"{self.base_url_restx}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type=DEFAULT_CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # add an item with invalid quantity
        item = ItemFactory(shopcart_id=shopcart.id)
        item.quantity = "Z"
        resp = self.client.post(f"{self.base_url_restx}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type=DEFAULT_CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        item.quantity = 1.2
        resp = self.client.post(f"{self.base_url_restx}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type=DEFAULT_CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        item.quantity = 2
        resp = self.client.post(f"{self.base_url_restx}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type=DEFAULT_CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # add an item with invalid price
        item = ItemFactory(shopcart_id=shopcart.id)
        item.price = "Z"
        resp = self.client.post(f"{self.base_url_restx}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type=DEFAULT_CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        item.price = -1.11
        resp = self.client.post(f"{self.base_url_restx}/{shopcart.id}/items",
                                json=item.serialize(),
                                content_type=DEFAULT_CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_items_415(self):
        """ [HTTP_415_UNSUPPORTED_MEDIA_TYPE] POST /shopcarts/{shopcart_id}/items """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()

        res = self.client.post(
            f"{self.base_url_restx}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="",
        )
        self.assertEqual(res.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        res = self.client.post(
            f"{self.base_url_restx}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/xml",
        )
        self.assertEqual(res.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_items(self):
        """ [HTTP_200_OK] GET /shopcarts/{shopcart_id}/items/{item_id} """
        test_shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        response = self.client.post(
            f"{self.base_url_restx}/{test_shopcart.id}/items",
            json=item.serialize(),
            content_type=DEFAULT_CONTENT_TYPE,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.get_json()
        logging.debug(data)
        item_id = data["id"]

        response = self.client.get(
            f"{self.base_url_restx}/{test_shopcart.id}/items/{item_id}",
            content_type=DEFAULT_CONTENT_TYPE,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        logging.debug(data)
        self.assertEqual(data["shopcart_id"], test_shopcart.id)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["price"], item.price)
        self.assertEqual(data["name"], item.name)

    def test_get_items_404(self):
        """ [HTTP_404_NOT_FOUND] GET /shopcarts/{shopcart_id}/items/{item_id} """
        shopcart = self._create_an_empty_shopcart(1)[0]

        # shopcart not found
        item = ItemFactory()
        response = self.client.get(f"{self.base_url_restx}/0/items/{item.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # item not found
        response = self.client.get(f"{self.base_url_restx}/{shopcart.id}/items/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_items(self):
        """ [HTTP_200_OK] PUT /shopcarts/{shopcart_id}/items/{item_id} """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{self.base_url_restx}/{shopcart.id}/items",
            json=item.serialize(),
            content_type=DEFAULT_CONTENT_TYPE,
        )
        data = res.get_json()

        # update name
        data["name"] = data["name"] + " II"
        res = self.client.put(
            f'{self.base_url_restx}/{shopcart.id}/items/{data["id"]}',
            json=data,
            content_type=DEFAULT_CONTENT_TYPE,
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
            f'{self.base_url_restx}/{shopcart.id}/items/{data["id"]}',
            json=data,
            content_type=DEFAULT_CONTENT_TYPE,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        updated_data = res.get_json()
        self.assertEqual(updated_data["name"], data["name"])
        self.assertEqual(updated_data["quantity"], data["quantity"])
        self.assertEqual(updated_data["price"], data["price"])

        # update price
        data["price"] = data["price"] * 2
        res = self.client.put(
            f'{self.base_url_restx}/{shopcart.id}/items/{data["id"]}',
            json=data,
            content_type=DEFAULT_CONTENT_TYPE,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        updated_data = res.get_json()
        self.assertEqual(updated_data["name"], data["name"])
        self.assertEqual(updated_data["quantity"], data["quantity"])
        self.assertEqual(updated_data["price"], data["price"])

    def test_update_items_415(self):
        """ [HTTP_415_UNSUPPORTED_MEDIA_TYPE] PUT /shopcarts/{shopcart_id}/items/{item_id} """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{self.base_url_restx}/{shopcart.id}/items",
            json=item.serialize(),
            content_type=DEFAULT_CONTENT_TYPE,
        )
        data = res.get_json()

        # update name
        data["name"] = data["name"] + " II"
        res = self.client.put(
            f'{self.base_url_restx}/{shopcart.id}/items/{data["id"]}',
            json=data,
            content_type="",
        )
        self.assertEqual(res.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        res = self.client.put(
            f'{self.base_url_restx}/{shopcart.id}/items/{data["id"]}',
            json=data,
            content_type="application/xml",
        )
        self.assertEqual(res.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_items_400(self):
        """ [HTTP_400_BAD_REQUEST] PUT /shopcarts/{shopcart_id}/items/{item_id} """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{self.base_url_restx}/{shopcart.id}/items",
            json=item.serialize(),
            content_type=DEFAULT_CONTENT_TYPE,
        )
        data = res.get_json()

        # update item with invalid quantity
        invalid_quantity_data = data.copy()
        invalid_quantity_data["quantity"] = -1
        res = self.client.put(
            f'{self.base_url_restx}/{shopcart.id}/items/{data["id"]}',
            json=invalid_quantity_data,
            content_type=DEFAULT_CONTENT_TYPE,
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # update item with invalid price
        invalid_price_data = data.copy()
        invalid_price_data["price"] = -1
        res = self.client.put(
            f'{self.base_url_restx}/{shopcart.id}/items/{data["id"]}',
            json=invalid_price_data,
            content_type=DEFAULT_CONTENT_TYPE,
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # update item with missing name
        no_name_data = data.copy()
        no_name_data["name"] = None
        res = self.client.put(
            f'{self.base_url_restx}/{shopcart.id}/items/{data["id"]}',
            json=no_name_data,
            content_type=DEFAULT_CONTENT_TYPE,
        )
        logging.debug(res.get_json())
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # update item with missing quantity
        no_quantity_data = data.copy()
        no_quantity_data["quantity"] = None
        res = self.client.put(
            f'{self.base_url_restx}/{shopcart.id}/items/{data["id"]}',
            json=no_quantity_data,
            content_type=DEFAULT_CONTENT_TYPE,
        )
        logging.debug(res.get_json())
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # update item with missing price
        no_price_data = data.copy()
        no_price_data["price"] = None
        res = self.client.put(
            f'{self.base_url_restx}/{shopcart.id}/items/{data["id"]}',
            json=no_price_data,
            content_type=DEFAULT_CONTENT_TYPE,
        )
        logging.debug(res.get_json())
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_items_404(self):
        """ [HTTP_404_NOT_FOUND] PUT /shopcarts/{shopcart_id}/items/{item_id} """
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"{self.base_url_restx}/{shopcart.id}/items",
            json=item.serialize(),
            content_type=DEFAULT_CONTENT_TYPE,
        )
        data = res.get_json()

        data["name"] = data["name"] + " II"

        # update item in non-existent shopcart
        res = self.client.put(
            f'{self.base_url_restx}/-1/items/{data["id"]}',
            json=data,
            content_type=DEFAULT_CONTENT_TYPE,
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        # update non-existent item
        res = self.client.put(
            f'{self.base_url_restx}/{shopcart.id}/items/{item.id + 10000}',
            json=data,
            content_type=DEFAULT_CONTENT_TYPE,
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        with patch('service.models.Shopcart.get_by_id', return_value=None):
            res = self.client.put(
                f'{self.base_url_restx}/{shopcart.id}/items/{data["id"]}',
                json=data,
                content_type=DEFAULT_CONTENT_TYPE,
            )
            self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_items(self):
        """ [HTTP_204_NO_CONTENT] DELETE /shopcarts/{shopcart_id}/items/{item_id} """
        shopcart = self._create_an_empty_shopcart(1)[0]

        # delete an empty shopcart
        res = self.client.delete(f"{self.base_url_restx}/{shopcart.id}")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        res = self.client.get(f"{self.base_url_restx}/{shopcart.id}")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        # delete a shopcart with items
        shopcart = self._create_an_empty_shopcart(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{self.base_url_restx}/{shopcart.id}/items",
            json=item.serialize(),
            content_type=DEFAULT_CONTENT_TYPE
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        item_id = data["id"]
        resp = self.client.delete(
            f"{self.base_url_restx}/{shopcart.id}/items/{item_id}",
            content_type=DEFAULT_CONTENT_TYPE
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        resp = self.client.get(
            f"{self.base_url_restx}/{shopcart.id}/items/{item_id}",
            content_type=DEFAULT_CONTENT_TYPE
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # delete a non-existent shopcart
        res = self.client.delete(f"{self.base_url_restx}/0")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
