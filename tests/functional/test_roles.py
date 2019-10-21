from hamcrest import *

from pytest_toolbelt import matchers


def test_get_roles(client, admin, user):
    admin, _ = admin
    user, _ = user

    response = client.get(
        f'/api/v1.0/user/{admin["id"]}/role/', headers={"Authorization": f'Bearer {admin["access_token"]}'}
    )

    assert_that(response, matchers.has_status(200))
    assert_that(response.data.decode(), matchers.is_json(has_items(*admin["roles"])))

    response = client.get(
        f'/api/v1.0/user/{user["id"]}/role/', headers={"Authorization": f'Bearer {admin["access_token"]}'}
    )

    assert_that(response, matchers.has_status(200))
    assert_that(response.data.decode(), matchers.is_json(is_not(has_items(*admin["roles"]))))
