import sys  # noqa

from dynaconf import LazySettings, Validator

settings = LazySettings(ENVVAR_PREFIX_FOR_DYNACONF="AFFO_US", ENVVAR_FOR_DYNACONF="AFFO_US_SETTINGS")

# Register validators
settings.validators.register(
    Validator(
        "DATABASE_URI",
        "CACHE_TYPE",
        "ADMIN_EMAIL",
        "ADMIN_PASSWORD",
        "SERVICE_EMAIL",
        "SERVICE_PASSWORD",
        "SMS_API_ROOT_URL",
        "EMAIL_API_ROOT_URL",
        must_exist=True,
    )
)

# Fire the validator
settings.validators.validate()

# SECRET CONFIGURATION
SECRET_KEY = getattr(settings, "SECRET_KEY", "")

# SQLALCHEMY CONFIGURATION
SQLALCHEMY_DATABASE_URI = settings.DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_MODEL_IMPORTS = ("affo_user_service.models.user",)

# FLASK PRAETORIAN CONFIGURATION
PRAETORIAN_HASH_SCHEME = "argon2"
DISABLE_PRAETORIAN_ERROR_HANDLER = True

# JWT CONFIGURATION
JWT_ACCESS_LIFESPAN = {"minutes": 15}

# Should be greater then JWT access lifespan
JWT_REFRESH_LIFESPAN = {"days": 30}

# PROVISIONING CONFIGURATION
PROVISIONING_ADMIN_EMAIL = settings.ADMIN_EMAIL
PROVISIONING_ADMIN_PASSWORD = settings.ADMIN_PASSWORD

PROVISIONING_SERVICE_EMAIL = settings.SERVICE_EMAIL
PROVISIONING_SERVICE_PASSWORD = settings.SERVICE_PASSWORD

PROVISIONING = {
    PROVISIONING_ADMIN_EMAIL: {"password": PROVISIONING_ADMIN_PASSWORD, "roles": ("admin",)},
    PROVISIONING_SERVICE_EMAIL: {"password": PROVISIONING_SERVICE_PASSWORD, "roles": ("service",)},
}

# VERIFICATION CONFIGURATION
VERIFICATION = {
    "phone": {
        "BACKEND": "affo_user_service.verification.backends.sms.SMSBackend",
        "OPTIONS": {
            "SMS_API_ROOT_URL": settings.SMS_API_ROOT_URL,
            "FROM": "AFFO",
            "SERVICE_ID": "user-service",
            "MESSAGE": "Your security code is: {token}",
        },
    }
}

VERIFICATION_RECIPIENT_EXCEPTIONS = ["+1234567890"]
VERIFICATION_RECIPIENT_EXCEPTIONS_TOKEN = "1111"

settings.populate_obj(sys.modules[__name__])
