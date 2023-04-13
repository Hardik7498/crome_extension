import pytest
from werkzeug.security import generate_password_hash

SHARED_SEED_DATA = {
    "user_info": [
        {
            "user_name": "Hardik_112",
            "id": pytest.id_for("USER_ID_1"),
            "email_id": "hardik.112@gmail.com",
            "password_hash": generate_password_hash("Hardik_112"),
        }
    ]
}
