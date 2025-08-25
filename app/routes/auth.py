from flask import request, jsonify, Blueprint
from app.schema.auth import LoginSchema
from app.services.auth import auth_service
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    create_refresh_token
    )

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    payload = LoginSchema().load(request.get_json())
    result = auth_service().login(payload)

    if result.get('error'):
        return jsonify({
            "error": True,
            "detail": result['detail']
        }), result['status']
    return jsonify({
        "error": False,
        "success": True,
        "data": "Login in success",
        "access": result['access'],
        "refresh": result['refresh']
    }), result['status']


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True, locations=['headers'])
def refresh():
    uuid = get_jwt_identity()
    if uuid is None:
        raise LookupError('UserId not found')
    access = create_access_token(identity=uuid)
    refresh = create_refresh_token(identity=uuid)
    return jsonify({
        "error": False,
        "success": True,
        "newAccess": access,
        "newRefresh": refresh
    }), 200
