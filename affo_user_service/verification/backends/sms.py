import requests

from .base import BaseBackend
from .. import exception


class SMSBackend(BaseBackend):
    def __init__(self, **settings):
        self._endpoint_url = settings["SMS_API_ROOT_URL"]
        self._from = settings["FROM"]
        self._service_id = settings["SERVICE_ID"]
        self._message = settings["MESSAGE"]

        self._session = requests.Session()

    def send(self, recipient, token, resend=False):
        # FIXME: find the way to provide a user identifier
        response = self._session.request(
            method="POST",
            url="{}{}".format(self._endpoint_url, "sms/"),
            json={
                "from": self._from,
                "message": self._message.format(token=token),
                "phone": recipient,
                "retry": resend,
                "service_id": self._service_id,
                "user_id": "",
            },
        )

        if response.status_code == 400:
            error = response.json()
            raise exception.InvalidPhone(error["description"])
        else:
            response.raise_for_status()
