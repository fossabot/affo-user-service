from affo_user_service import settings
from affo_user_service.extensions import cache

from .backends import get_backend
from .generators import get_generator

DEFAULT_EXPIRY = getattr(settings, "VERIFICATION_TOKEN_EXPIRY", 60 * 10)
services = {}


class VerificationService:
    """
    The VerificationService is the main access point in this module. This
    service makes sure that there is a token generated as well as it has been
    send with the appropriate backend.

    :ivar backend: the backend to be used (e.g. email, phone backend)
    :ivar verification_type: The type of verification that is done (e.g. email, phone)
    :ivar generator: Generator which returns a token to be passed
    """

    def __init__(self, backend, verification_type):
        self.backend = backend
        self.verification_type = verification_type
        self.generator = get_generator(verification_type)

    def send_verification(self, recipient, resend=False):
        """
        Send a verification email/ text to the given recipient to verify.

        :param recipient: the phone recipient/ email of recipient.
        """
        token = self.create_temporary_token(recipient=recipient)

        if recipient not in getattr(settings, "VERIFICATION_RECIPIENT_EXCEPTIONS", []):
            return self.backend.send(recipient=recipient, token=token, resend=resend)

    def create_temporary_token(self, recipient, expiry=DEFAULT_EXPIRY):
        """
        Creates a temporary token inside the cache, this holds the phone recipient
        as value, so that we can later check if everything is correct.

        :param recipient: recipient of recipient
        :param expiry: Expiry of the token, defaults to 3 hours.

        :return token: string of sha token
        """
        token = self.generator(recipient)

        if recipient in getattr(settings, "VERIFICATION_RECIPIENT_EXCEPTIONS", []):
            token = getattr(settings, "VERIFICATION_RECIPIENT_EXCEPTIONS_TOKEN", token)

        cache.set(self._cache_key(recipient), token, expiry)

        return token

    def _cache_key(self, recipient):
        return "verification:{}".format(recipient)

    def validate_token(self, recipient, token):
        """
        Check if given token is valid, compares it with the ones present in the
        cache.

        :param token: Token to be checked
        :param value: The key it should be in

        :returns boolean: Valid or not.
        """
        cached = cache.get(self._cache_key(recipient))
        return str(token) == str(cached)


def get_service(service_name):
    """
    Gets the service VerificationService, checks if there is already one in the
    memory, if so return that one.

    :param service_name: e.g. phone, email
    """
    # Check if service_name in VERIFICATION
    if not settings.VERIFICATION.get(service_name, None):
        raise ValueError("{} not a valid service.".format(service_name))

    if not services.get(service_name, None):
        service = VerificationService(get_backend(service_name), service_name)
        services[service_name] = service
    return services[service_name]
