import json

import pytest
from flask.testing import FlaskClient

from tests.shared_data.shared_seed_data import SHARED_SEED_DATA


def test_user_signup_api(client: FlaskClient):
    response = client.post(
        "user/signup",
        data=json.dumps(
            {
                "user_name": "Hardik",
                "email_id": "hardik.@gmail.com",
                "password": "Hardik_1234",
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 201
    assert response.json["message"] == "User Created Successfully"


@pytest.mark.seed_data(("user_info", SHARED_SEED_DATA["user_info"]))
def test_user_signup_user_name_exists(client: FlaskClient, seed):
    response = client.post(
        "user/signup",
        data=json.dumps(
            {
                "user_name": "Hardik_112",
                "email_id": "hardik.@gmail.com",
                "password": "Hardik_1234",
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json["message"] == "User Name already exists"

    response = client.post(
        "user/signup",
        data=json.dumps(
            {
                "user_name": "Hardik",
                "email_id": "hardik.112@gmail.com",
                "password": "Hardik_1234",
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json["message"] == "Email already exists"

    response = client.post(
        "user/signup",
        data=json.dumps(
            {
                "user_name": "Hardik_1234",
                "email_id": "hardik.112@gmail.com",
                "password": "Hardik_1234",
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json["message"] == "User Name and Password Can not be same"


@pytest.mark.seed_data(("user_info", SHARED_SEED_DATA["user_info"]))
def test_user_login_api(client: FlaskClient, seed):
    response = client.post(
        "user/login",
        data=json.dumps(
            {
                "user_name": "Hardik_112",
                "password": "Hardik_112",
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json["access_token"] is not None
    assert response.json["refresh_token"] is not None
