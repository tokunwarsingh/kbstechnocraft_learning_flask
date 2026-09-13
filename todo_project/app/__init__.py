import os

from flask import Flask

from .extensions import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-secret"),
        SQLALCHEMY_DATABASE_URI=(
            "sqlite:///" + os.path.join(app.instance_path, "todo.sqlite3")
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from .api import api
    from .web import web

    app.register_blueprint(web)
    app.register_blueprint(api)

    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def not_found(error):
        if app.request_class:
            from flask import request

            if request.path.startswith("/api/"):
                return {"error": "Resource not found"}, 404
        from flask import render_template

        return render_template("404.html"), 404

    return app
