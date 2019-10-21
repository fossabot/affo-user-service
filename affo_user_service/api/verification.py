import connexion

from affo_user_service.verification import services
from affo_user_service.verification.exception import InvalidPhone

from . import exception


def phone(phone):
    service = services.get_service("phone")

    try:
        service.send_verification(recipient=phone["phone"], resend=phone.get("resend", False))
    except InvalidPhone as exc:
        raise exception.InvalidPhone(str(exc))

    return connexion.NoContent, 200


def phone_confirm(phone_confirm):
    service = services.get_service("phone")

    exception.InvalidPhoneCode.require_condition(
        service.validate_token(recipient=phone_confirm["phone"], token=phone_confirm["code"]),
        "Invalid phone verification code",
    )

    return connexion.NoContent, 200
