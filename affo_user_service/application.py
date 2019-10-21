import importlib
import logging
import sys

import connexion

import connexion_buzz

import flask_praetorian

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from sqlalchemy.exc import ProgrammingError

from . import settings
from .api import exception
from .extensions import cache, db, guard, ma, migrate
from .models.user import User

__all__ = ["create_app"]

logging.basicConfig(level=logging.INFO)


def create_guard(app):
    def is_blacklisted(jti):
        entry = cache.get(jti)

        if entry is None:
            return True

        return entry == "true"

    guard.init_app(app, User, is_blacklisted=is_blacklisted)

    return guard


def provisioning(app):
    with app.app_context():
        # FIXME: A correct migration handing is needed
        try:
            with db.session.begin(subtransactions=True):
                for user_email, user_data in app.config["PROVISIONING"].items():
                    user_already_exists = db.session.query(
                        User.query.filter(User.email == user_email).exists()
                    ).scalar()

                    if user_already_exists:
                        continue

                    user_data["email"] = user_email
                    user_data["password"] = guard.encrypt_password(user_data["password"])

                    user_ = User(**user_data)
                    db.session.add(user_)
        except ProgrammingError:
            pass


def create_app(settings_override=None):
    app = connexion.App(__name__, specification_dir="./spec/", options={"swagger_ui": False}, debug=settings.DEBUG)
    app.add_api("openapi.yaml", arguments={"title": "AFFO User Service API"}, validate_responses=True)

    application = app.app
    application.config.from_object(settings)

    if settings_override:
        application.config.update(settings_override)

    app.add_error_handler(connexion_buzz.ConnexionBuzz, connexion_buzz.ConnexionBuzz.build_error_handler())
    app.add_error_handler(flask_praetorian.PraetorianError, exception.praetorian_error_handler)

    # Import DB models. Flask-SQLAlchemy doesn't do this automatically.
    with application.app_context():
        for module in application.config.get("SQLALCHEMY_MODEL_IMPORTS", list()):
            importlib.import_module(module)

    # Initialize extensions/add-ons/plugins.
    create_guard(application)

    # Flask-SQLAlchemy must be initialized before Flask-Marshmallow.
    db.init_app(application)
    ma.init_app(application)
    migrate.init_app(application, db)

    sentry_sdk.init(integrations=[FlaskIntegration()], **application.config.get("SENTRY_CONFIG", {}))

    # Initialize the cache
    cache.init_app(application, config=application.config)

    # Provisioning
    if not application.config.get("TESTING", False) and "sphinx" not in sys.modules:
        provisioning(application)

    return application
