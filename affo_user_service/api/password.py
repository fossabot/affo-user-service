import connexion

import itsdangerous

from affo_user_service import settings
from affo_user_service.extensions import db, email, guard
from affo_user_service.models.user import User

from .exception import InvalidToken, NoSuchUser


def reset(password_reset):
    safe = itsdangerous.URLSafeTimedSerializer(settings.SECRET_KEY)

    with db.session.begin(subtransactions=True):
        user_ = db.session.query(User).filter(User.email == password_reset["email"]).one_or_none()

        NoSuchUser.require_condition(user_, "The user with {email} email does not exist", email=password_reset["email"])

        token = safe.dumps(user_.email)

        email.template.send(
            "password_reset",
            body={
                "from_": "noreply@example.com",
                "to": [user_.email],
                "subject": "Password reset required",
                "variables": {
                    "name": user_.get_short_name(),
                    "password_reset_url": password_reset["url_template"].format(token=token),
                },
                "tag": "password_reset",
            },
        )

    return connexion.NoContent, 200


def reset_confirm(password_reset_confirm):
    safe = itsdangerous.URLSafeTimedSerializer(settings.SECRET_KEY)

    with InvalidToken.handle_errors(
        "The specified token is invalid", exception_class=(itsdangerous.BadSignature, itsdangerous.BadTimeSignature)
    ):
        email = safe.loads(password_reset_confirm["token"])

    with db.session.begin(subtransactions=True):
        user_ = db.session.query(User).filter(User.email == email).one_or_none()

        NoSuchUser.require_condition(user_, "The user with {email} email does not exist", email=email)

        user_.password = guard.encrypt_password(password_reset_confirm["new_password"])

        db.session.add(user_)

    return connexion.NoContent, 200
