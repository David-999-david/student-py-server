from flask import Flask
from app.extensions import (
    init_extensions,
    db
    )
from app.error.error import register_app_error
from app.routes.auth import auth_bp
from app.routes.student import (
    gender_bp,
    student_bp
)
from app.routes.course import course_bp


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object("config.Development")

    init_extensions(app=app)

    register_app_error(app=app)

    with app.app_context():
        db.create_all()
        app.logger.info("Successfully connect to Postgres Database")

    app.register_blueprint(auth_bp)
    app.register_blueprint(gender_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(course_bp)

    return app
