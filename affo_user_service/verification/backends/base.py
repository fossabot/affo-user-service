class BaseBackend:
    def __init__(self, **settings):
        raise NotImplementedError()

    def send(self, recipient, token, resend=False):
        raise NotImplementedError()
