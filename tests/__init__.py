"""
Variables shared among tests
"""

import os

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/shopcarts"
BASE_URL_RESTX = "/api/shopcarts"

DEFAULT_CONTENT_TYPE = "application/json"
