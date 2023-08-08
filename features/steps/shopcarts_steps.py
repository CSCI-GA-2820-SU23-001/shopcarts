"""
Shopcarts Steps

Steps file for Shopcarts.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


@given("the following shopcarts")
def step_impl(context):
    """ Delete all Shopcarts and load new ones """
    # List all shopcarts and delete them one by one
    rest_endpoint = f"{context.base_url}/shopcarts"
    resp = requests.get(rest_endpoint)
    assert resp.status_code == HTTP_200_OK
    for shopcart in resp.json():
        # logging.info(shopcart)
        resp = requests.delete(f"{rest_endpoint}/{shopcart['id']}")
        assert resp.status_code == HTTP_204_NO_CONTENT

    # load the database with new shopcarts
    for row in context.table:
        payload = {
            "name": row["name"],
            "items": []
        }
        resp = requests.post(rest_endpoint, json=payload)
        assert resp.status_code == HTTP_201_CREATED


@given("the following items")
def step_impl(context):
    rest_endpoint = f"{context.base_url}/shopcarts"
    for row in context.table:
        resp = requests.get(rest_endpoint + "?name=" + row["shopcart_name"])
        assert resp.status_code == HTTP_200_OK
        data = resp.json()
        # logging.info(data)
        shopcart_id = data[0]["id"]
        payload = {
            "shopcart_id": shopcart_id,
            "name": row["name"],
            "quantity": int(row["quantity"]),
            "price": float(row["price"])
        }
        resp = requests.post(rest_endpoint + "/" + str(shopcart_id) + "/items", json=payload)
        # logging.info(resp.json())
        assert resp.status_code == HTTP_201_CREATED
