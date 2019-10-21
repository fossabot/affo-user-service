import uuid

from hamcrest import *

from pytest_toolbelt import matchers


def test_set_password(client, user):
    user, old_password = user
    new_password = "qazwsx123"

    response = client.post(
        "/api/v1.0/user/current/set_password/",
        json={"password": new_password},
        headers={"Authorization": f'Bearer {user["access_token"]}'},
    )
    assert_that(response, matchers.has_status(200))

    credentials = {"email": user["email"], "password": old_password}

    response = client.post("/api/v1.0/auth/login/", json=credentials)
    assert_that(response, matchers.has_status(401))

    credentials = {"email": user["email"], "password": new_password}

    response = client.post("/api/v1.0/auth/login/", json=credentials)
    assert_that(response, matchers.has_status(200))


def test_user_utf8mb4(client):
    first_name = "晓鹏"
    last_name = "郑"

    response = client.post(
        "/api/v1.0/user/",
        json={
            "email": f"test-{uuid.uuid4()}@investex.com",
            "phone": "+1234567890",
            "first_name": first_name,
            "last_name": last_name,
            "password": None,
        },
    )
    assert_that(response, matchers.has_status(201))
    assert_that(
        response.data.decode(),
        matchers.is_json(has_entries(first_name=equal_to(first_name), last_name=equal_to(last_name))),
    )
