""" Models for Article """

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import relationship

from database import db


def uuid_default():
    return str(uuid.uuid4())


class Article(db.Model):
    __tablename__ = "article"

    id = Column(String(36), primary_key=True, default=uuid_default)
    user_id = Column(String(36), ForeignKey("user_info.id"))
    article_link = Column(String(1028), nullable=False)
    image_link = Column(String(1028), nullable=False)
    name = Column(String(1028))
    category = Column(String(128), default="General")
    website_name = Column(String(1028), nullable=False)
    website_url = Column(String(1028), nullable=False)
    is_deleted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_on = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    share = Column(Integer, default=0, autoincrement=True)
    watch = Column(Integer, default=0, autoincrement=True)

    user = relationship("UserInfo")


class SavedArticle(db.Model):
    __tablename__ = "saved_article"
    __table_args__ = (PrimaryKeyConstraint("id", "user_id"),)
    id = Column(String(36), primary_key=True, default=uuid_default)
    article_id = Column(String(36), ForeignKey("article.id"))
    user_id = Column(String(36), ForeignKey("user_info.id"))
    created_on = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    article = relationship("Article")

    user = relationship("UserInfo")
