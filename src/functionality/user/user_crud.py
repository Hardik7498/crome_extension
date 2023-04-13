import datetime
import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import jwt
from flask import current_app as app
from flask import request
from flask_api import status
from sqlalchemy import false, true

from database import db
from src.config import Config
from src.resources.user.model import UserInfo
from src.utils.exception import MuzliException


def signup():
    app.logger.info("Functionality: sign up user")
    req_data: dict = request.json
    user_name = req_data.get("user_name")
    email_id = req_data.get("email_id")
    password = req_data.get("password")

    if user_name == password:
        raise MuzliException(
            status.HTTP_400_BAD_REQUEST, "User Name and Password Can not be same"
        )

    users = UserInfo.query.filter(
        UserInfo.user_name == user_name,
        UserInfo.is_deleted == false(),
        UserInfo.is_active == true(),
    ).first()
    users_emails = UserInfo.query.filter(
        UserInfo.email_id == email_id,
        UserInfo.is_deleted == false(),
        UserInfo.is_active == true(),
    ).first()

    if users:
        raise MuzliException(status.HTTP_400_BAD_REQUEST, "User Name already exists")

    if users_emails:
        raise MuzliException(status.HTTP_400_BAD_REQUEST, "Email already exists")

    user_info = UserInfo(user_name=user_name, email_id=email_id)

    user_info.set_password(password)
    db.session.add(user_info)
    db.session.commit()
    db.session.close()
    return "User Created Successfully"


def login():
    app.logger.info("Functionality: login user")
    req_data = request.json
    user_name = req_data.get("user_name")
    password = req_data.get("password")
    email = req_data.get("email_id")

    if user_name:
        user = UserInfo.query.filter(
            UserInfo.user_name == user_name, UserInfo.is_deleted == false()
        ).first()
    elif email:
        user = UserInfo.query.filter(
            UserInfo.email_id == email, UserInfo.is_deleted == false()
        ).first()

    if not user:
        raise MuzliException(
            status.HTTP_401_UNAUTHORIZED, "Invalid User Name or Password"
        )

    if not user.check_password(password):
        raise MuzliException(status.HTTP_401_UNAUTHORIZED, "Invalid Password")

    user_id = user.id
    access_payload = {
        "user_name": user_name,
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
    }
    access_token = jwt.encode(access_payload, Config.JWT_SECRET_KEY, algorithm="HS256")

    refresh_token_id = str(uuid.uuid4())
    refresh_payload = {
        "refresh_token_id": refresh_token_id,
        "user_id": user_id,
        "username": user_name,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
    }
    refresh_token = jwt.encode(
        refresh_payload, Config.JWT_SECRET_KEY, algorithm="HS256"
    )

    return access_token, refresh_token


def send_forget_password_link():
    app.logger.info("Functionality: forget password")
    user_name = request.args.get("user_name")
    email = request.args.get("email")

    if user_name:
        user = UserInfo.query.filter(
            UserInfo.user_name == user_name, UserInfo.is_deleted == false()
        ).first()
    elif email:
        user = UserInfo.query.filter(
            UserInfo.email_id == email, UserInfo.is_deleted == false()
        ).first()

    if not user:
        raise MuzliException(status.HTTP_404_NOT_FOUND, "User not found")

    # generate reset password token
    reset_token = user.generate_reset_token()

    # send email to user with reset password link
    reset_link = f"https://clone.com/reset-password/{reset_token}"
    sender_email = Config.SENDER_EMAIL
    sender_password = Config.EMAIL_PASSWORD
    recipient_email = user.email_id
    subject = "Reset Password"
    body = f"Reset your password here: {reset_link}"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(sender_email, sender_password)
        smtp.send_message(message)

    return (
        "An email with password reset sent to your registered email address",
        reset_token,
    )


def reset_password():
    token = request.json.get("token")
    password = request.json.get("password")

    if not token or not password:
        raise MuzliException(
            status.HTTP_400_BAD_REQUEST, "Token and password are required."
        )

    user = UserInfo.verify_reset_token(token)

    if not user:
        raise MuzliException(status.HTTP_400_BAD_REQUEST, "Invalid or expired token.")

    user.set_password(password)
    db.session.commit()

    return "Password reset successfully."
