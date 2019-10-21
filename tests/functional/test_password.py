from hamcrest import *

from pytest_toolbelt import matchers

from affo_user_service import settings


def test_password_reset(client, user, requests_mock):
    requests_mock.post(f"{settings.EMAIL_API_ROOT_URL}template/password_reset/send/", status_code=200)

    user, old_password = user

    response = client.post("/api/v1.0/password/reset/", json={"email": user["email"], "url_template": "{token}"})
    assert_that(response, matchers.has_status(200))

    password_reset_email_data = requests_mock.last_request.json()
    assert_that(password_reset_email_data, has_entries({"variables": has_key("password_reset_url")}))

    token = password_reset_email_data["variables"]["password_reset_url"]
    new_password = "new_password"

    response = client.post("/api/v1.0/password/reset/confirm/", json={"token": token, "new_password": new_password})

    credentials = {"email": user["email"], "password": old_password}
    response = client.post("/api/v1.0/auth/login/", json=credentials)
    assert_that(response, matchers.has_status(401))

    credentials = {"email": user["email"], "password": new_password}

    response = client.post("/api/v1.0/auth/login/", json=credentials)
    assert_that(response, matchers.has_status(200))
