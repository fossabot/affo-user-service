import datetime

import connexion

import flask_praetorian

import jwt

from sqlalchemy import or_

from affo_user_service import settings
from affo_user_service.models.user import User, user_schema
from affo_user_service.extensions import db, guard, cache

from .exception import AlreadyExists, NoSuchUser
from .utils import get_user_by_id


def create(user):
    with db.session.begin(subtransactions=True):
        user_already_exists_condition = User.email == user["email"]

        if "phone" in user:
            if user["phone"] not in settings.VERIFICATION_RECIPIENT_EXCEPTIONS:
                user_already_exists_condition = or_(User.email == user["email"], User.phone == user["phone"])

        user_already_exists = db.session.query(User.query.filter(user_already_exists_condition).exists()).scalar()

        AlreadyExists.require_condition(
            not user_already_exists, "A user already exists with the specified email address or phone number"
        )

        if user["password"]:
            user["password"] = guard.encrypt_password(user["password"])

        user_ = User(**user)
        db.session.add(user_)

    access_token = guard.encode_jwt_token(user_)

    # FIXME: Flask-Praetorian does not provide JTI without a token
    # validation
    data = jwt.decode(
        access_token, guard.encode_key, algorithms=guard.allowed_algorithms, options={"verify_exp": False}
    )

    cache.set(data["jti"], "false", int(datetime.timedelta(**settings.JWT_REFRESH_LIFESPAN).total_seconds()))

    user_dump = user_schema.dump(user_)
    user_dump["access_token"] = access_token

    return user_dump, 201


@flask_praetorian.auth_required
def get(user_id):
    user_ = get_user_by_id(user_id)

    return user_schema.dump(user_)


@flask_praetorian.auth_required
def update(user_id, user1):
    with db.session.begin(subtransactions=True):
        user_ = get_user_by_id(user_id)

        for k, v in user1.items():
            setattr(user_, k, v)

        db.session.add(user_)

    return user_schema.dump(user_)


@flask_praetorian.roles_accepted("admin")
def delete(user_id):
    with db.session.begin(subtransactions=True):
        user_ = db.session.query(User).filter(User.id == user_id).one_or_none()

        NoSuchUser.require_condition(user_, "The user with {user_id} identifier does not exist", user_id=user_id)

        user_.is_active = False

        db.session.add(user_)

    return connexion.NoContent, 204


@flask_praetorian.auth_required
def set_password(user_id, password):
    with db.session.begin(subtransactions=True):
        user_ = get_user_by_id(user_id)
        user_.password = guard.encrypt_password(password["password"])

        db.session.add(user_)

    return connexion.NoContent, 200
