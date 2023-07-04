# The Shopcarts Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This is a skeleton you can use to start your projects

## Overview

This project template contains starter code for your class project. The `/service` folder contains your `models.py` file for your model and a `routes.py` file for your service. The `/tests` folder has test case starter code for testing the model and the service separately. All you need to do is add your functionality. You can use the [lab-flask-tdd](https://github.com/nyu-devops/lab-flask-tdd) for code examples to copy from.

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

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

list_shopcarts    GET      /shopcarts
create_shopcarts  POST     /shopcarts
get_shopcarts     GET      /shopcarts/<shopcart_id>
update_shopcarts  PUT      /shopcarts/<shopcart_id>
delete_shopcarts  DELETE   /shopcarts/<shopcart_id>

list_items        GET      /shopcarts/<shopcart_id>/items
create_items      POST     /shopcarts/<shopcart_id>/items
get_items         GET      /shopcarts/<shopcart_id>/items/<item_id>
update_items      PUT      /shopcarts/<shopcart_id>/items/<item_id>
delete_items      DELETE   /shopcarts/<shopcart_id>/items/<item_id>
```

The test cases can be run with `green`.


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
TBA
```

##### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "${error_message}",
  "status": 500
}
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

##### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "${error_message}",
  "status": 500
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

##### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "${error_message}",
  "status": 500
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
   "id": 34,
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

##### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "${error_message}",
  "status": 500
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
##### 200 OK
```json
TBA
```

##### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Shopcart with id='0' was not found.",
  "status": 404
}
```

##### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "${error_message}",
  "status": 500
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

##### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "${error_message}",
  "status": 500
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
  "quantity": 1
}
```

#### Response
##### 200 OK
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

##### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "${error_message}",
  "status": 500
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

##### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "${error_message}",
  "status": 500
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
  "quantity": 2
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
TBA
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

##### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "${error_message}",
  "status": 500
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
##### 200 OK
```json
TBA
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

##### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "${error_message}",
  "status": 500
}
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
