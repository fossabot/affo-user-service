import random

from werkzeug import import_string

from affo_user_service import settings

DEFAULT_GENERATOR = "affo_user_service.verification.generators.NumberGenerator"


def get_generator(service_name):
    """
    Get the generator that is set for the specific service.
    """
    # Check if service_name in VERIFICATION
    if not settings.VERIFICATION.get(service_name, None):
        raise ValueError("{} not a valid service.".format(service_name))

    service_settings = settings.VERIFICATION.get(service_name)
    generator_path = service_settings.get("GENERATOR", DEFAULT_GENERATOR)

    return import_string(generator_path)()


class Generator:
    pass


class NumberGenerator(Generator):
    """
    Creates a random number.

    :usage example:
        generator = NumberGenerator()
        print(generator())  # 1239
    """

    def __call__(self, key):
        return str(random.randint(1000, 9999))
