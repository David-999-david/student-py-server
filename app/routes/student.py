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


@student_bp.route('', methods=['GET'])
def get_stu():
    query = request.args.get('q', '').strip()
    page = request.args.get('p', default=1, type=int)
    limit = request.args.get('l', default=10, type=int)
    if page is None or page < 1:
        page = 1
    if limit is None or limit < 1:
        limit = 10
    offset = (page - 1) * limit
    if query:
        results = StudentService().get_query(query=query, limit=limit, offset=offset)
        students = [
            seralize_dict(dict(s)) for s in results
        ]
    else:
        results = StudentService().get(limit=limit, offset=offset)
        students = [
            seralize_dict(dict(s)) for s in results
        ]
    return jsonify({
        "error": False,
        "success": True,
        "data": students,
        "count": len(students)
    }), 200


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


@student_bp.route('/join', defaults={"id": None}, methods=['GET'])
@student_bp.route('/join/<int:id>', methods=['GET'])
def get_id(id):
    query = request.args.get('q', '').strip()
    page = request.args.get('p', default=1, type=int)
    limit = request.args.get('l', default=10, type=int)
    if page is None or page < 1:
        page = 1
    if limit is None or limit < 1:
        limit = 10
    offset = (page - 1) * limit
    if id:
        results = StudentService().get_id(id)
        students = seralize_dict(dict(results))
        return jsonify({
            "error": False,
            "success": True,
            "data": students,
        }), 200
    elif query:
        results = StudentService().get_join_query(query=query, limit=limit, offset=offset)
        students = [
            seralize_dict(dict(s)) for s in results
        ]
    else:
        results = StudentService().get_join(limit=limit, offset=offset)
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
    result = StudentService().make_join(studentId=studentId, courseIds=courseIds)
    if result.get('error'):
        return jsonify({
            "error": True,
            "detail": result['detail']
        }), result['status']
    return jsonify({
        "error": False,
        "success": True,
        "message": result['message'],
        "data": result['data']
    }), result['status']


@student_bp.route('/join', methods=['DELETE'])
def cancel_join():
    data = request.get_json()
    studentId = data.get('studentId')
    courseId = data.get('courseId')
    result = StudentService().cancel_join(studentId, courseId)
    if result.get('error'):
        return jsonify({
            "error": True,
            "detail": result['detail']
        }), result['status']
    return jsonify({
        "error": False,
        "success": True,
        "message": result['detail']
    }), result['status']


@student_bp.route('/detail', methods=['GET'])
def detail():
    result = StudentService().detail()
    return jsonify({
        "error": False,
        "success": True,
        "data": {
            "s_s_t": result['s_s_t'],
            "s_s_f": result['s_s_f'],
            "s_g_m": result['s_g_m'],
            's_g_f': result['s_g_f'],
            's_g_o': result['s_g_o'],
            "c_s_t": result['c_s_t'],
            "c_s_f": result['c_s_f']
        }
    })
