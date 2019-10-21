import datetime

from hamcrest import *

import pytest

from pytest_toolbelt import matchers

from affo_user_service import settings


def test_auth_login(client, user):
    user, password = user

    credentials = {"email": user["email"], "password": password}

    response = client.post("/api/v1.0/auth/login/", json=credentials)
    assert_that(response, matchers.has_status(200))


def test_auth_login_failed(client):
    credentials = {"email": "test@example.com", "password": "1234567890"}

    response = client.post("/api/v1.0/auth/login/", json=credentials)
    assert_that(response, matchers.has_status(401))


def test_auth_logout(client, user):
    user, _ = user

    response = client.get(f'/api/v1.0/user/{user["id"]}/', headers={"Authorization": f'Bearer {user["access_token"]}'})
    assert_that(response, matchers.has_status(200))

    response = client.post("/api/v1.0/auth/logout/", headers={"Authorization": f'Bearer {user["access_token"]}'})
    assert_that(response, matchers.has_status(204))

    response = client.get(f'/api/v1.0/user/{user["id"]}/', headers={"Authorization": f'Bearer {user["access_token"]}'})
    assert_that(response, matchers.has_status(403))


def test_auth_verify_token(client, user):
    user, _ = user

    response = client.get("/api/v1.0/auth/verify_token/", headers={"Authorization": f'Bearer {user["access_token"]}'})
    assert_that(response, matchers.has_status(200))


@pytest.mark.freeze_time
def test_auth_refresh(freezer, client, user):
    user, _ = user

    response = client.post("/api/v1.0/auth/refresh/", headers={"Authorization": f'Bearer {user["access_token"]}'})

    assert_that(response, matchers.has_status(401))
    assert_that(response.data.decode(), matchers.is_json(has_entries(code="EarlyRefreshError")))

    freezer.tick(datetime.timedelta(**settings.JWT_ACCESS_LIFESPAN) + datetime.timedelta(seconds=1))

    response = client.post("/api/v1.0/auth/refresh/", headers={"Authorization": f'Bearer {user["access_token"]}'})
    assert_that(response, matchers.has_status(200))

    token_data = response.json

    response = client.get(
        f'/api/v1.0/user/{user["id"]}/', headers={"Authorization": f'Bearer {token_data["access_token"]}'}
    )
    assert_that(response, matchers.has_status(200))


@pytest.mark.freeze_time
def test_auth_refresh_multiple(freezer, client, user):
    user, _ = user

    freezer.tick(datetime.timedelta(**settings.JWT_ACCESS_LIFESPAN) + datetime.timedelta(seconds=1))

    response = client.post("/api/v1.0/auth/refresh/", headers={"Authorization": f'Bearer {user["access_token"]}'})
    assert_that(response, matchers.has_status(200))

    token_data = response.json

    response = client.get(
        f'/api/v1.0/user/{user["id"]}/', headers={"Authorization": f'Bearer {token_data["access_token"]}'}
    )
    assert_that(response, matchers.has_status(200))

    freezer.tick(datetime.timedelta(**settings.JWT_ACCESS_LIFESPAN) + datetime.timedelta(seconds=1))

    response = client.post("/api/v1.0/auth/refresh/", headers={"Authorization": f'Bearer {token_data["access_token"]}'})
    assert_that(response, matchers.has_status(200))

    token_data = response.json

    response = client.get(
        f'/api/v1.0/user/{user["id"]}/', headers={"Authorization": f'Bearer {token_data["access_token"]}'}
    )
    assert_that(response, matchers.has_status(200))
