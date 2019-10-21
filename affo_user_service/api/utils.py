import flask_praetorian

from affo_user_service.extensions import db
from affo_user_service.models.user import User

from .exception import AccessDenied, NoSuchUser


def get_user_by_id(user_id):
    requester = flask_praetorian.current_user()

    AccessDenied.require_condition(
        str(user_id) in (str(requester.id), 'current') or requester.has_role('admin', 'service'),
        'Access denied'
    )

    if user_id == 'current':
        user = requester
    else:
        user = db.session.query(User).filter(User.id == user_id).one_or_none()

    NoSuchUser.require_condition(
        user,
        'The user with {user_id} identifier does not exist',
        user_id=user_id
    )

    return user
