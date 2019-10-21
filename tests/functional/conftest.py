import uuid

from hamcrest import *

import pytest

from pytest_toolbelt import matchers

from affo_user_service import settings


@pytest.fixture()
def user(client):
    password = "1234567890"

    response = client.post(
        "/api/v1.0/user/",
        json={
            "email": f"test-{uuid.uuid4()}@example.com",
            "phone": "+1234567890",
            "first_name": "晓鹏",
            "last_name": "郑",
            "password": password,
        },
    )
    assert_that(response, matchers.has_status(201))

    return (response.json, password)


@pytest.fixture()
def admin(client):
    response = client.post(
        "/api/v1.0/auth/login/",
        json={"email": settings.PROVISIONING_ADMIN_EMAIL, "password": settings.PROVISIONING_ADMIN_PASSWORD},
    )
    assert_that(response, matchers.has_status(200))

    access_token = response.json["access_token"]

    response = client.get("/api/v1.0/user/current/", headers={"Authorization": f"Bearer {access_token}"})
    assert_that(response, matchers.has_status(200))

    user = response.json
    user["access_token"] = access_token

    return (user, settings.PROVISIONING_ADMIN_PASSWORD)
