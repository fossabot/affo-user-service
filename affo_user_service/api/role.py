import flask_praetorian

from affo_user_service.api.utils import get_user_by_id
from affo_user_service.extensions import db


@flask_praetorian.auth_required
def get(user_id):
    return get_user_by_id(user_id).roles


@flask_praetorian.roles_accepted("admin")
def update(user_id, roles):
    with db.session.begin(subtransactions=True):
        user_ = get_user_by_id(user_id)

        user_.roles = roles
        db.session.add(user_)

    return user_.roles
