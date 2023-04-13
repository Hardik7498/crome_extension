from functools import wraps

import jwt
from flask import g, request
from flask_api import status

from src.config import Config
from src.utils.exception import MuzliException


def authenticated(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            access_token = request.headers.get("Authorization")
            jwt.decode(access_token, Config.JWT_SECRET_KEY, algorithms=["HS256"])

        except jwt.ExpiredSignatureError:
            raise jwt.InvalidTokenError(status.HTTP_401_UNAUTHORIZED, "Token expired")

        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError(status.HTTP_401_UNAUTHORIZED, "Invalid token")

        return fn(*args, **kwargs)

    return wrapper


def authenticated_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            access_token = request.headers.get("Authorization")
            if access_token:
                payload = jwt.decode(
                    access_token, Config.JWT_SECRET_KEY, algorithms=["HS256"]
                )
                user_id = payload["user_id"]
                if not user_id:
                    raise jwt.InvalidTokenError(
                        status.HTTP_401_UNAUTHORIZED, "Invalid token"
                    )
                user_metadata = payload
                user = type("MyObject", (object,), user_metadata)
                g.user = user
            else:
                raise MuzliException(
                    status.HTTP_401_UNAUTHORIZED, "Authorization not found"
                )

            return fn(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            raise jwt.InvalidTokenError(status.HTTP_401_UNAUTHORIZED, "Token expired")

        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    return wrapper
