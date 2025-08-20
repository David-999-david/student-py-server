from flask import request, Blueprint, jsonify
from app.schema.course import CourseSchema
from app.services.course import CourseService
from app.seralizer import seralize_dict


course_bp = Blueprint('course', __name__, url_prefix='/course')


@course_bp.route('', methods=['POST'])
def insert():
    payload = CourseSchema().load(
        request.get_json() or {}
    )
    result = CourseService().insert(payload)
    course = seralize_dict(dict(result))
    return jsonify({
        "error": False,
        "success": True,
        "data": course
    }), 201
