from flask import request, jsonify, Blueprint
from app.services.student import (
    gender_service,
    StudentService
)
from app.seralizer import seralize_dict
from app.schema.student import StudentSchema

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
    })


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


@student_bp.route('', methods=['GET'])
def get_stu():
    query = request.args.get('q', '').strip()
    if query:
        results = StudentService().get_query(query=query)
        students = [
            seralize_dict(dict(s)) for s in results
        ]
    else:
        results = StudentService().get()
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
    StudentService().remove(id)
    message = f'Delete student with id={id} success'
    return jsonify({
        "error": False,
        "success": True,
        "data": message
    }), 204
