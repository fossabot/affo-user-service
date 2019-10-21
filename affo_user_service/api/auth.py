import datetime

import connexion

import flask_praetorian
import flask_praetorian.exceptions

import jwt

from affo_user_service import settings
from affo_user_service.extensions import db, guard, cache
from affo_user_service.models.user import user_schema

from .exception import AuthFailure


def login(login):
    with db.session.begin(subtransactions=True):
        try:
            user = guard.authenticate(username=login["email"], password=login["password"])
        except (flask_praetorian.exceptions.MissingUserError, flask_praetorian.exceptions.AuthenticationError):
            raise AuthFailure("The email or password is incorrect")

        user.last_login = datetime.datetime.utcnow()
        db.session.add(user)

    access_token = guard.encode_jwt_token(user)

    # FIXME: Flask-Praetorian does not provide JTI without a token
    # validation
    data = jwt.decode(
        access_token, guard.encode_key, algorithms=guard.allowed_algorithms, options={"verify_exp": False}
    )

    cache.set(data["jti"], "false", int(datetime.timedelta(**settings.JWT_REFRESH_LIFESPAN).total_seconds()))

    user_dump = user_schema.dump(user)
    user_dump["access_token"] = access_token

    return user_dump, 200


def refresh():
    old_token = guard.read_token_from_header()
    new_token = guard.refresh_jwt_token(old_token)

    # FIXME: Flask-Praetorian does not provide JTI without a token
    # validation
    data = jwt.decode(new_token, guard.encode_key, algorithms=guard.allowed_algorithms, options={"verify_exp": False})

    cache.set(data["jti"], "false", int(datetime.timedelta(**settings.JWT_REFRESH_LIFESPAN).total_seconds()))

    return {"access_token": new_token}, 200


@flask_praetorian.auth_required
def logout():
    data = guard.extract_jwt_token(guard.read_token_from_header())

    cache.set(data["jti"], "true", int(datetime.timedelta(**settings.JWT_REFRESH_LIFESPAN).total_seconds()))

    return connexion.NoContent, 204


@flask_praetorian.auth_required
def verify_token():
    data = guard.extract_jwt_token(guard.read_token_from_header())
    return data, 200
