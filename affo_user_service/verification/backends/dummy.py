from .base import BaseBackend


class DummyBackend(BaseBackend):
    def __init__(self, **settings):
        pass

    def send(self, recipient, token, resend=False):
        pass
