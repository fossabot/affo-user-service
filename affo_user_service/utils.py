from .extensions import guard


def jwt_decode_token(token, required_scopes=None):
    return guard.extract_jwt_token(token)
