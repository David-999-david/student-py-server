from flask import request, jsonify, Blueprint
from app.schema.auth import LoginSchema
from app.services.auth import auth_service

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    payload = LoginSchema().load(request.get_json())
    token = auth_service().login(payload)

    if not token:
        return jsonify({
            "error": True,
            "message": "Email or password is incorrect"
        }), 400

    access, refresh = token
    return jsonify({
        "error": False,
        "success": True,
        "data": "Login in success",
        "access": access,
        "refresh": refresh
    }), 200
