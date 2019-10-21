from hamcrest import *

import pytest

from pytest_toolbelt import matchers


@pytest.mark.parametrize("verification_type,recipient", [("phone", "+1234567890")])
def test_verification(client, verification_type, recipient):
    response = client.post(f"/api/v1.0/verification/{verification_type}/", json={"phone": recipient})

    assert_that(response, matchers.has_status(200))


@pytest.mark.parametrize("verification_type,recipient", [("phone", "+1234567890")])
def test_verification_complete_invalid(client, verification_type, recipient):
    response = client.post(
        f"/api/v1.0/verification/{verification_type}/confirm/", json={"phone": recipient, "code": "1234"}
    )
    assert_that(response, matchers.has_status(400))

    response = client.post(
        f"/api/v1.0/verification/{verification_type}/confirm/", json={"phone": recipient, "code": "1111"}
    )
    assert_that(response, matchers.has_status(200))
