""" Models for user"""

import uuid
from datetime import datetime, timedelta

from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import URLSafeTimedSerializer as Serializer
from sqlalchemy import Boolean, Column, DateTime, String
from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from src.config import Config


def uuid_default():
    return str(uuid.uuid4())


class UserInfo(db.Model):
    __tablename__ = "user_info"

    id = Column(String(36), primary_key=True, default=uuid_default)
    password_hash = Column(String(128), nullable=False)
    user_name = Column(String(128), nullable=False, unique=True)
    email_id = Column(String(128), nullable=False)
    is_deleted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_on = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self, expiration_hours=1):
        s = Serializer(Config.SECRET_PASSWORD_KEY)
        expires_in = datetime.utcnow() + timedelta(hours=expiration_hours)
        expires_in_str = expires_in.strftime("%Y-%m-%dT%H:%M:%SZ")
        return s.dumps(
            {"user_id": self.id, "expires_in": expires_in_str}, salt="reset-password"
        )

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(Config.SECRET_PASSWORD_KEY)
        try:
            data = s.loads(token, salt="reset-password", max_age=3600)
        except SignatureExpired:
            return None  # token has expired
        except BadSignature:
            return None  # token is invalid
        return UserInfo.query.get(data["user_id"])
