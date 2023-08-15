# Shopcarts Service
The shopcarts service allows customers to make a collection of products that they want to purchase. It contains a
reference to a product and the quantity the customer wants to buy. It also contains the price of the product at the time
they placed it in the cart. A customer will only have one shopcart.

[![Build Status](https://github.com/CSCI-GA-2820-SU23-001/shopcarts/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SU23-001/shopcarts/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SU23-001/shopcarts/branch/master/graph/badge.svg?token=OUCWT94U59)](https://codecov.io/gh/CSCI-GA-2820-SU23-001/shopcarts)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

## Contents
* [Sites](#sites)
  * [Production](http://159.122.175.64:31002)
    * [/shopcartsapi](http://159.122.175.64:31002/shopcartsapi)
    * [/itemsapi](http://159.122.175.64:31002/itemsapi)
  * [Development](http://159.122.175.64:31001)
* [CI/CD Workflow](#cicd-workflow)
* [Documentation](#documentation)
  * [List of RESTful Routes](#list-of-restful-routes)
  * [Swagger Doc](http://159.122.175.64:31002/apidocs)


## Sites
* [Production](http://159.122.175.64:31002)
* [Development](http://159.122.175.64:31001)


## CI/CD Workflow
![CI/CD Workflow](.github/cicd-workflow.png)


## Documentation

This project leverages [Flask-RESTX](https://flask-restx.readthedocs.io/en/latest/) to generate [Swagger/OpenAPI](https://www.openapis.org/) documentation available at [/apidocs](http://159.122.175.64:31002/apidocs).

### List of RESTful Routes

These are the RESTful routes for `shopcarts` and `items`:

```markdown
Endpoint            Methods  Rule
------------------  -------  -----------------------------------------------------
index_page          GET      /
shopcartsapi_page   GET      /shopcartsapi
itemsapi_page       GET      /itemsapi

health              GET      /health

apidocs             GET      /apidocs
list_shopcarts      GET      /api/shopcarts
create_shopcarts    POST     /api/shopcarts
get_shopcarts       GET      /api/shopcarts/<shopcart_id>
update_shopcarts    PUT      /api/shopcarts/<shopcart_id>
delete_shopcarts    DELETE   /api/shopcarts/<shopcart_id>
clear_shopcarts     PUT      /api/shopcarts/<shopcart_id>/clear

list_items          GET      /api/shopcarts/<shopcart_id>/items
create_items        POST     /api/shopcarts/<shopcart_id>/items
get_items           GET      /api/shopcarts/<shopcart_id>/items/<item_id>
update_items        PUT      /api/shopcarts/<shopcart_id>/items/<item_id>
delete_items        DELETE   /api/shopcarts/<shopcart_id>/items/<item_id>
```

The test cases can be run with `green`.


## Database Connection

### Steps

1. Leveraging the Docker command to launch the PostgreSQL CLI in the shopcarts.db container using the following command:

    ```bash
    docker exec -it shopcarts.db psql -U postgres -d postgres -h localhost -p 5432
    ```

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
