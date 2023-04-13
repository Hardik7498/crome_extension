import traceback

import jwt
from flask import Flask, jsonify

from database import db
from src.config import Config
from src.utils.exception import MuzliException
from src.utils.log_utils import config_log


def create_app():
    """
    Create flask app, configure the app, configure
    database session :returns: instance of flask
    """

    app = Flask(__name__)

    # load the configs
    app.config.from_object(Config)

    # init db
    db.init_app(app)

    # configure logger
    config_log(app)

    @app.route("/", methods=["GET", "POST"])
    def check():
        return "Up and Running..."

    # register the blueprints
    from src.resources.article.api import articles
    from src.resources.user.api import user

    app.register_blueprint(user)
    app.register_blueprint(articles)

    @app.errorhandler(Exception)
    def handle_known_exceptions(exception: Exception):
        app.logger.error(traceback.format_exc())

        # FIXME remove error showing thing
        if isinstance(exception, MuzliException):
            return (jsonify(message=exception.message), exception.status_code)
        if isinstance(exception, jwt.InvalidTokenError):
            return (jsonify(message=exception.args[1]), exception.args[0])

        return (
            jsonify(message="Something went wrong!!", error=str(exception)),
            500,
        )

    return app
