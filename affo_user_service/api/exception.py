import http

import connexion_buzz

import flask


class NoSuchUser(connexion_buzz.ConnexionBuzz):
    status_code = http.HTTPStatus.BAD_REQUEST


class InvalidToken(connexion_buzz.ConnexionBuzz):
    status_code = http.HTTPStatus.BAD_REQUEST


class InvalidPhoneCode(connexion_buzz.ConnexionBuzz):
    status_code = http.HTTPStatus.BAD_REQUEST


class AlreadyExists(connexion_buzz.ConnexionBuzz):
    status_code = http.HTTPStatus.BAD_REQUEST


class InvalidPhone(connexion_buzz.ConnexionBuzz):
    status_code = http.HTTPStatus.BAD_REQUEST


class AuthFailure(connexion_buzz.ConnexionBuzz):
    status_code = http.HTTPStatus.UNAUTHORIZED


class AccessDenied(connexion_buzz.ConnexionBuzz):
    status_code = http.HTTPStatus.FORBIDDEN


class InternalError(connexion_buzz.ConnexionBuzz):
    status_code = http.HTTPStatus.INTERNAL_SERVER_ERROR


class PraetorianErrorBuzz(connexion_buzz.ConnexionBuzz):
    def __init__(self, e, *args, **kwargs):
        self.e = e

        super().__init__(message=e.message, *args, **kwargs)

    def jsonify(self, description=None, headers=None):
        description = description or self.description

        headers = headers or self.headers

        response = flask.jsonify({"code": repr(self.e), "description": description})

        response.status_code = self.e.status_code

        if headers is not None:
            response.headers = headers
        return response


def praetorian_error_handler(e):
    error_handler = PraetorianErrorBuzz.build_error_handler()
    return error_handler(PraetorianErrorBuzz(e))
