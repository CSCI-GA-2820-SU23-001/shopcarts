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
