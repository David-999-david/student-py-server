from flask import request, Blueprint, jsonify
from app.schema.course import CourseSchema
from app.services.course import CourseService
from app.seralizer import seralize_dict
from app.schema.student import bulkSchema
from app.extensions import limiter


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


@course_bp.route('', methods=['POST'])
def insert_more():
    payload = bulkSchema(CourseSchema).load(
        request.get_json() or {}
    )
    results = CourseService().insert_many(payload['items'])
    courses = [
        seralize_dict(dict(s)) for s in results
    ]
    return jsonify({
        "error": False,
        "success": True,
        "data": courses
    }), 201


@course_bp.route('', methods=['GET'])
def get():
    query = request.args.get('q', '').strip()
    if query:
        results = CourseService().get_query(query=query)
        courses = [
            seralize_dict(dict(c)) for c in results
        ]
    else:
        results = CourseService().get_all()
        courses = [
            seralize_dict(dict(c)) for c in results
        ]
    return jsonify({
        "error": False,
        "success": True,
        "data": courses,
        "count": len(courses)
    }), 200


@course_bp.route('/<int:id>', methods=['PUT'])
def update(id):
    payload = CourseSchema(partial=True).load(
        request.get_json() or {}
    )
    result = CourseService().update(id, payload)
    updated = seralize_dict(dict(result))
    return jsonify({
        "error": False,
        "success": True,
        "data": updated
    }), 200


@course_bp.route('/<int:id>', methods=['DELETE'])
def delete(id):
    CourseService().delete(id)
    return jsonify({
        "error": False,
        "success": True,
        "message": f"Delete course with id={id} success"
    }), 200


@course_bp.route('/<int:id>', methods=['GET'])
def get_id(id):
    result = CourseService().get_id(id)
    course = seralize_dict(dict(result))
    return jsonify({
        "error": False,
        "success": True,
        "data": course
    }), 200


@course_bp.route('/join', methods=['POST'])
def join():
    data = request.get_json()
    courseId = data.get('courseId')
    studentIds = data.get('studentIds')
    response = CourseService().join(courseId=courseId, studentIds=studentIds)
    if response.get('error'):
        return jsonify({
            "error": True,
            "success": False,
            "detail": response["detail"]
        }), response['status']
    return jsonify({
        "error": False,
        "success": True,
        "data": response['data']
    }), 201


@course_bp.route('/join', methods=['DELETE'])
def cancel_join():
    data = request.get_json()
    courseId = data.get('courseId')
    studentId = data.get('studentId')
    result = CourseService().cancel_join(courseId=courseId, studentId=studentId)
    if result.get('error'):
        return jsonify({
            "error": True,
            "detail": result['detail']
        }), result['status']
    return jsonify({
        "error": False,
        "success": True,
        "data": result['detail']
    }), result['status']


@course_bp.route('/join', defaults={"id": None}, methods=['GET'])
@course_bp.route('/join/<int:id>', methods=['GET'])
@limiter.limit('10 per minute')
def get_join(id):
    query = request.args.get('q', '').strip()
    if id:
        result = CourseService().get_id(id=id)
        return jsonify({
            "error": False,
            "success": True,
            "data": seralize_dict(dict(result))
        })
    elif query:
        results = CourseService().join_query(query=query)
        courses = [
            seralize_dict(dict(c)) for c in results
        ]
    else:
        results = CourseService().get_join()
        courses = [
            seralize_dict(dict(c)) for c in results
        ]
    return jsonify({
        "error": False,
        "success": True,
        "data": courses,
        "count": len(courses)
    })
