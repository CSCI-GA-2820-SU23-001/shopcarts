"""
Global Configuration for Application
"""
import os

APP_VERSION = "1.0.0"
PREFIX_API = "/api"
PREFIX_API_DOCS = "/apidocs"

# Get configuration from environment
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

# Configure SQLAlchemy
SQLALCHEMY_DATABASE_URI = DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret for session management
SECRET_KEY = os.getenv("SECRET_KEY", "s3cr3t-key-shhhh")
