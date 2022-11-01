from dotenv import load_dotenv
from os import environ

from models.config_models import MySQLSettings

# This loads the .env variables. If they already exist, they won't be overwritten.
# This is useful for defining a single value for development and deployment.
load_dotenv()

preview_url = environ.get("PREVIEW_URL")
site_url = environ.get("SITE_URL")
redis_provider = environ.get("REDIS_URL")
mongodb_provider = environ.get("MONGODB_URL")

jwt_secret = environ.get("JWT_SECRET")
jwt_algorithm = environ.get("JWT_ALGORITHM")

email_url = environ.get("EMAIL")
email_pass = environ.get("EMAIL_PASS")

mysql_settings = MySQLSettings()
