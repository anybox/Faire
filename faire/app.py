import os
from typing import Optional, Union

from flask import Flask

from clocky.models import DB
from clocky.views import bp, csrf, login_manager, page_not_found

ConfigObject = Optional[Union[str, object]]


def create_app() -> Flask:
    """App fatory."""
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.register_error_handler(404, page_not_found)
    login_manager.init_app(app)
    login_manager.login_view = "clocky.login"
    config(app)

    csrf.init_app(app)

    app.logger.setLevel(app.config["LOGGING_LEVEL"].upper())
    app.debug = app.config["DEBUG"]

    app.app_context().push()
    DB.init_app(app)

    return app


def config(app: Flask, config_object: ConfigObject = None):
    if config_object is None:
        config_object = os.getenv("APP_CONFIG", "clocky.config.DevConfig")
    app.config.from_object(config_object)
