from werkzeug.exceptions import HTTPException
from marshmallow.exceptions import ValidationError
from flask import jsonify, current_app
from sqlalchemy.exc import IntegrityError, DatabaseError


def register_app_error(app):

    @app.errorhandler(ValidationError)
    def on_validate(e):
        current_app.logger.info(e.messages)
        return jsonify(
            error="Validation Error",
            detail=e.messages
        ), 422

    @app.errorhandler(HTTPException)
    def on_http(e):
        return jsonify({
            "error": str(e),
            "detail": e.description
        }), e.code

    @app.errorhandler(DatabaseError)
    def on_database(e):
        current_app.logger.exception(e)
        return jsonify(
            error=f"DataBase Error , {str(e.description)}",
            detail=str(e)
        ), 500

    @app.errorhandler(IntegrityError)
    def on_integirty(e):
        current_app.logger.exception(e)
        return jsonify(
            error="on Conflict",
            detail=str(e)
        ), 409

    @app.errorhandler(LookupError)
    def on_lookup(e):
        current_app.logger.error(e)
        return jsonify(
            error="Not Found",
            detail=str(e)
        ), 404

    @app.errorhandler(Exception)
    def on_any(e):
        current_app.logger.error(e)
        return jsonify(
            error="Internal Server Error"
        ), 500
