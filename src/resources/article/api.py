from flask import Blueprint
from flask import current_app as app
from flask import jsonify
from flask_api import status

from src.functionality.article.article_crud import (
    delete_articles,
    get_articles,
    get_articles_for_user,
    post_article_info,
    update_articles,
)
from src.functionality.article.serializer import articles_info_data

articles = Blueprint("articles", __name__, url_prefix="/article")


@articles.route("/publish", methods=["POST"])
def create_article():
    app.logger.info("API: create article")
    articles = post_article_info()
    return (
        jsonify(articles),
        status.HTTP_201_CREATED,
    )


@articles.route("/user", methods=["GET"])
def get_article_user():
    app.logger.info("API: get user article")
    articles_info = get_articles_for_user()
    return (jsonify(articles_info_data(articles_info)), status.HTTP_200_OK)


@articles.route("/", methods=["GET"])
def fetch_articles():
    app.logger.info("API: get article")
    articles_info = get_articles()
    return (jsonify(articles_info_data(articles_info)), status.HTTP_200_OK)


@articles.route("/", methods=["PUT"])
def update_article():
    app.logger.info("API: update article")
    update_article_info = update_articles()
    return (jsonify(message=update_article_info), status.HTTP_204_NO_CONTENT)


@articles.route("/", methods=["DELETE"])
def delete_article():
    app.logger.info("API: delete article")
    articles = delete_articles()
    return (jsonify(message=articles), status.HTTP_204_NO_CONTENT)
