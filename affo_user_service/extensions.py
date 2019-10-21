from affo_email_client import Client as EmailClient

from flask_caching import Cache

from flask_marshmallow import Marshmallow

from flask_migrate import Migrate

from flask_sqlalchemy import SQLAlchemy

from flask_praetorian import Praetorian

from . import settings

__all__ = ["cache", "db", "guard", "ma", "migrate"]

cache = Cache()

db = SQLAlchemy(session_options={"autocommit": True})

email = EmailClient(api_root_url=settings.EMAIL_API_ROOT_URL)

guard = Praetorian()

ma = Marshmallow()

migrate = Migrate()
