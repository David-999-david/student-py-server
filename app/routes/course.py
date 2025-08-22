from flask import request, Blueprint, jsonify
from app.schema.course import CourseSchema
from app.services.course import CourseService
from app.seralizer import seralize_dict
from app.schema.student import bulkSchema


course_bp = Blueprint('course', __name__, url_prefix='/course')


# @course_bp.route('', methods=['POST'])
# def insert():
#     payload = CourseSchema().load(
#         request.get_json() or {}
#     )
#     result = CourseService().insert(payload)
#     course = seralize_dict(dict(result))
#     return jsonify({
#         "error": False,
#         "success": True,
#         "data": course
#     }), 201


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
    })


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
    })


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
    })


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
    CourseService().join(courseId=courseId, studentIds=studentIds)
    message = f"Join course with id{courseId} and students success"
    return jsonify({
        "error": False,
        "success": True,
        "message": message
    }), 201


@course_bp.route('/join', methods=['DELETE'])
def cancel_join():
    data = request.get_json()
    courseId = data.get('courseId')
    studentId = data.get('studentId')
    CourseService().cancel_join(courseId=courseId, studentId=studentId)
    message = f'Cancel join course id={courseId} with student id={studentId}' \
              'success'
    return jsonify({
        "error": False,
        "success": True,
        "data": message
    }), 203
