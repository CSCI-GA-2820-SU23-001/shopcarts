# Shopcarts Service

[![Build Status](https://github.com/CSCI-GA-2820-SU23-001/shopcarts/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SU23-001/shopcarts/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SU23-001/shopcarts/branch/master/graph/badge.svg?token=OUCWT94U59)](https://codecov.io/gh/CSCI-GA-2820-SU23-001/shopcarts)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes
```

## RESTful Routes

These are the RESTful routes for `shopcarts` and `items`
```markdown
Endpoint          Methods  Rule
----------------  -------  -----------------------------------------------------
index             GET      /

health            GET      /health

list_shopcarts    GET      /shopcarts
create_shopcarts  POST     /shopcarts
get_shopcarts     GET      /shopcarts/<shopcart_id>
update_shopcarts  PUT      /shopcarts/<shopcart_id>
delete_shopcarts  DELETE   /shopcarts/<shopcart_id>
clear_shopcarts   PUT      /shopcarts/<shopcart_id>/clear

list_items        GET      /shopcarts/<shopcart_id>/items
create_items      POST     /shopcarts/<shopcart_id>/items
get_items         GET      /shopcarts/<shopcart_id>/items/<item_id>
update_items      PUT      /shopcarts/<shopcart_id>/items/<item_id>
delete_items      DELETE   /shopcarts/<shopcart_id>/items/<item_id>
```

The test cases can be run with `green`.


### Health Check
Get service health status.

#### API Endpoint
GET /health

#### Request Headers
| Header       | Value            |
|--------------|------------------|
| Content-Type | application/json |

#### Response
##### 200 OK
```json
{
  "status": "OK"
}
```

### List Shopcarts
List all shopcarts in the system.

#### API Endpoint
GET /shopcarts

#### Request Headers
| Header       | Value            |
|--------------|------------------|
| Content-Type | application/json |

#### Response
##### 200 OK
```json
[
  {
    "id": 27,
    "items": [],
    "name": "Yuzhao"
  },
  {
    "id": 1,
    "items": [
      {
        "id": 2,
        "name": "iPad",
        "price": 500.0,
        "quantity": 2,
        "shopcart_id": 1
      },
      {
        "id": 5,
        "name": "Switch",
        "price": 399.0,
        "quantity": 1,
        "shopcart_id": 1
      }
    ],
    "name": "Wan-Yu"
  }
]
```

### Create Shopcart
Create a new shopcart.

#### API Endpoint
POST /shopcarts

#### Request Headers
| Header       | Value            |
|--------------|------------------|
| Content-Type | application/json |

#### Request Body
```json
{
   "name": "Darcy"
}
```

#### Response
##### 201 Created
```json
{
  "id": 34,
  "items": [],
  "name": "Darcy"
}
```

##### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Invalid Shopcart: missing name",
  "status": 400
}
```

##### 415 Unsupported Media Type
```json
{
  "error": "Unsupported media type",
  "message": "Content-Type must be application/json",
  "status": 415
}
```

### Get Shopcart
Get a shopcart by id.

#### API Endpoint
GET /shopcarts/{shopcarts_id}

#### Request Headers
| Header       | Value            |
|--------------|------------------|
| Content-Type | application/json |

#### Response
##### 200 OK
```json
{
  "id": 5,
  "items": [
    {
      "id": 2,
      "name": "Macbook Air",
      "price": 600.0,
      "quantity": 1,
      "shopcart_id": 5
    }
  ],
  "name": "Elizabeth"
}
```

##### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Shopcart with id='0' was not found.",
  "status": 404
}
```

### Update Shopcart
Update an existing shopcart.

#### API Endpoint
PUT /shopcarts/{shopcarts_id}

#### Request Headers
| Header       | Value            |
|--------------|------------------|
| Content-Type | application/json |

#### Request Body
```json
{
   "name": "Fitzwilliam Darcy"
}
```

#### Response
##### 200 OK
```json
{
  "id": 34,
  "items": [],
  "name": "Fitzwilliam Darcy"
}
```

##### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Invalid Shopcart: missing name",
  "status": 400
}
```

##### 415 Unsupported Media Type
```json
{
  "error": "Unsupported media type",
  "message": "Content-Type must be application/json",
  "status": 415
}
```

### Delete Shopcart
Delete an existing shopcart.

#### API Endpoint
DELETE /shopcarts/{shopcarts_id}

#### Request Headers
| Header       | Value            |
|--------------|------------------|
| Content-Type | application/json |

#### Response
##### 204 No Content
```json

```

### Clear Shopcart
Clear a shopcart by id.

#### API Endpoint
PUT /shopcarts/{shopcarts_id}/clear

#### Request Headers
| Header       | Value            |
|--------------|------------------|
| Content-Type | application/json |

#### Response
##### 200 OK
```json
{
  "id": 47,
  "items": [],
  "name": "John"
}
```

##### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "404 Not Found: Shopcart with id '44' could not be found.",
  "status": 404
}
```

### List Shopcart Items
Get a list of items in the shopcart.

#### API Endpoint
GET /shopcarts/{shopcart_id}/items

#### Request Headers
| Header       | Value            |
|--------------|------------------|
| Content-Type | application/json |

#### Response
##### 200 OK
```json
[
  {
    "id": 2,
    "name": "iPhone SE",
    "price": 500.0,
    "quantity": 1,
    "shopcart_id": 3
  }
]
```

##### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Shopcart with id='0' was not found.",
  "status": 404
}
```

### Create Shopcart Item
Add a new item to shopcart.

#### API Endpoint
POST /shopcarts/<shopcart_id>/items

#### Request Headers
| Header       | Value            |
|--------------|------------------|
| Content-Type | application/json |

#### Request Body
```json
{
  "name": "iPhone SE",
  "price": 500.0,
  "quantity": 1,
  "shopcart_id": 1
}
```

#### Response
##### 201 Created
```json
{
  "id": 1,
  "name": "iPhone SE",
  "price": 500.0,
  "quantity": 1,
  "shopcart_id": 1
}
```

##### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Quantity of a new item should always be one.",
  "status": 400
}
```

##### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Shopcart with id='3' was not found.",
  "status": 404
}
```

##### 415 Unsupported Media Type
```json
{
  "error": "Unsupported media type",
  "message": "Content-Type must be application/json",
  "status": 415
}
```

### Get Shopcart Item
Get the contents of a shopcart item.

#### API Endpoint
GET /shopcarts/{shopcart_id}/items/{item_id}

#### Request Headers
| Header       | Value            |
|--------------|------------------|
| Content-Type | application/json |

#### Response
##### 200 OK
```json
{
 "id": 2,
 "name": "iPhone SE",
 "price": 500.0,
 "quantity": 1,
 "shopcart_id": 3
}
```

##### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Shopcart with id='0' was not found.",
  "status": 404
}
```

```json
{
  "error": "Not Found",
  "message": "Item with id='123' was not found.",
  "status": 404
}
```

### Update Shopcart Item
Update an existing item in shopcart.

#### API Endpoint
PUT /shopcarts/<shopcart_id>/items/{item_id}

#### Request Headers
| Header       | Value            |
|--------------|------------------|
| Content-Type | application/json |

#### Request Body
> e.g. Increase item quantity from 1 to 2

```json
{
  "name": "iPhone SE",
  "price": 500.0,
  "quantity": 2,
  "shopcart_id": 1
}
```

#### Response
##### 200 OK
```json
{
  "id": 1,
  "name": "iPhone SE",
  "price": 500.0,
  "quantity": 2,
  "shopcart_id": 1
}
```

##### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Missing key \"name\" in request body.",
  "status": 400
}
```

##### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Shopcart with id='0' was not found.",
  "status": 404
}
```

```json
{
  "error": "Not Found",
  "message": "Item with id='123' was not found.",
  "status": 404
}
```

##### 415 Unsupported Media Type
```json
{
  "error": "Unsupported media type",
  "message": "Content-Type must be application/json",
  "status": 415
}
```

### Delete Shopcart Item
Delete an existing item in shopcart.

#### API Endpoint
DELETE /shopcarts/<shopcart_id>/items/{item_id}

#### Request Headers
| Header       | Value            |
|--------------|------------------|
| Content-Type | application/json |

#### Response
##### 204 No Content
```json

```

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
