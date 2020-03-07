from flask import Flask
from shorty.api import api
from shorty.logger import set_logger_level


def create_app(settings_overrides=None):
    app = Flask(__name__)
    configure_settings(app, settings_overrides)
    configure_blueprints(app)
    print(app.name)
    return app


def configure_settings(app, settings_override):
    app.config.update({"DEBUG": True, "TESTING": False})
    set_logger_level("INFO")
    if settings_override:
        app.config.update(settings_override)


def configure_blueprints(app):
    app.register_blueprint(api)
