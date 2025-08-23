from flask import request, jsonify, Blueprint
from app.services.student import (
    gender_service,
    StudentService
)
from app.seralizer import seralize_dict
from app.schema.student import StudentSchema, bulkSchema

gender_bp = Blueprint('gender', __name__, url_prefix='/gender')


@gender_bp.route('', methods=['GET'])
def get():
    results = gender_service().get()
    genders = [
        seralize_dict(dict(g)) for g in results
    ]
    return jsonify({
        "error": False,
        "success": True,
        "data": genders
    }), 200


student_bp = Blueprint('student', __name__, url_prefix='/student')


@student_bp.route('', methods=['POST'])
def insert():
    payload = StudentSchema().load(
        request.get_json() or {}
    )
    result = StudentService().insert(payload)
    new_stud = seralize_dict(dict(result))
    return jsonify({
        "error": False,
        "success": True,
        "data": new_stud
    }), 201


@student_bp.route('', methods=['POST'])
def insert_more():
    payload = bulkSchema(StudentSchema).load(
        request.get_json() or {}
    )
    results = StudentService().insert_many(payload['items'])
    students = [
        seralize_dict(dict(s)) for s in results
    ]
    return jsonify({
        "error": False,
        "success": True,
        "data": students
    }), 201


# @student_bp.route('', methods=['GET'])
# def get_stu():
#     query = request.args.get('q', '').strip()
#     if query:
#         results = StudentService().get_query(query=query)
#         students = [
#             seralize_dict(dict(s)) for s in results
#         ]
#     else:
#         results = StudentService().get()
#         students = [
#             seralize_dict(dict(s)) for s in results
#         ]
#     return jsonify({
#         "error": False,
#         "success": True,
#         "data": students,
#         "count": len(students)
#     }), 200


@student_bp.route('/<int:id>', methods=['PUT'])
def edit_stu(id):
    payload = StudentSchema(partial=True).load(
        request.get_json() or {}
    )
    result = StudentService().edit(id, payload)
    edited = seralize_dict(dict(result))
    return jsonify({
        "error": False,
        "success": True,
        "data": edited
    }), 200


@student_bp.route('/<int:id>', methods=['DELETE'])
def remove(id):
    data = request.get_json()
    courseIds = data.get('courseIds') or []
    if not isinstance(courseIds, list):
        raise LookupError('For delete student, courseIds is not list')
    StudentService().remove(id, courseIds=courseIds)
    message = f'Delete student with id={id} success'
    return jsonify({
        "error": False,
        "success": True,
        "data": message
    }), 200


@student_bp.route('', defaults={"id": None}, methods=['GET'])
@student_bp.route('/<int:id>', methods=['GET'])
def get_id(id):
    query = request.args.get('q', '').strip()
    if id:
        results = StudentService().get_id(id)
        students = seralize_dict(dict(results))
        return jsonify({
            "error": False,
            "success": True,
            "data": students,
        }), 200
    elif query:
        results = StudentService().get_join_query(query=query)
        students = [
            seralize_dict(dict(s)) for s in results
        ]
    else:
        results = StudentService().get_join()
        students = [
            seralize_dict(dict(s)) for s in results
        ]
    return jsonify({
        "error": False,
        "success": True,
        "data": students,
        "count": len(students)
    }), 200


@student_bp.route('/join', methods=['POST'])
def join():
    data = request.get_json()
    studentId = data.get('studentId')
    courseIds = data.get('courseIds')
    res = StudentService().make_join(studentId=studentId, courseIds=courseIds)
    message = 'Join student with courses success'
    return jsonify({
        "error": False,
        "success": True,
        "message": message,
        "detail": res
    }), 200


@student_bp.route('/join', methods=['DELETE'])
def cancel_join():
    data = request.get_json()
    studentId = data.get('studentId')
    courseId = data.get('courseId')
    StudentService().cancel_join(studentId, courseId)
    message = 'Cancel join student with course success'
    return jsonify({
        "error": False,
        "success": True,
        "message": message
    }), 200
