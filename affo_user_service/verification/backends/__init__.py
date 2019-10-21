from werkzeug import import_string

from affo_user_service import settings

DEFAULT_SERVICE = 'affo_user_service.verification.backends.base.BaseBackend'


def get_backend(service_name):
    """
    Gets the backend with the given service settings.
    It checks for a BACKEND key and later passes in these OPTIONS in the
    backend.

    :param service_settings: dict like object
    :returns: base.BaseBackend inherited object
    """
    backend_import = DEFAULT_SERVICE
    service_settings = settings.VERIFICATION.get(service_name, None)

    if service_settings is None:
        raise ValueError('service with {} key not found'.format(service_name))

    if service_settings.get('BACKEND', None):
        backend_import = service_settings.get('BACKEND', None)

    backend_cls = import_string(backend_import)
    return backend_cls(identifier=service_name, **service_settings.get('OPTIONS', {}))
