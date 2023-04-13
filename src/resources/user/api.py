from flask import Blueprint
from flask import current_app as app
from flask import jsonify
from flask_api import status

from src.functionality.user.user_crud import (
    login,
    reset_password,
    send_forget_password_link,
    signup,
)

user = Blueprint("user", __name__, url_prefix="/user")


@user.route("/signup", methods=["POST"])
def signup_user():
    app.logger.info("API: sign up user")
    sign_up_user = signup()
    return (jsonify(message=sign_up_user), status.HTTP_201_CREATED)


@user.route("/login", methods=["POST"])
def login_user():
    app.logger.info("API: login user")
    access_token, refresh_token = login()
    return (
        jsonify(access_token=access_token, refresh_token=refresh_token),
        status.HTTP_200_OK,
    )


@user.route("/forget_password", methods=["POST"])
def forget_password_link():
    app.logger.info("API: forget password link send")
    password_link, reset_token = send_forget_password_link()

    return (jsonify(message=password_link, token=reset_token), status.HTTP_200_OK)


@user.route("/reset_password", methods=["POST"])
def reset_password_by_link():
    app.logger.info("API: reset password")
    password_link = reset_password()

    return (jsonify(message=password_link), status.HTTP_200_OK)
