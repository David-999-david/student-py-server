from app.extensions import db
from sqlalchemy import text
from werkzeug.exceptions import NotFound, BadRequest


class gender_service():
    get_sql = text(
        '''select * from gender'''
    )

    def get(self) -> list[dict]:
        with db.session.begin():
            results = db.session.execute(
                self.get_sql
            ).mappings().fetchall()
            if results is None:
                raise NotFound('There is no genders')
            return results


class StudentService():
    insert_sql = text(
        '''insert into student
            (name,email,phone,address,gender_id,status)
            values
            (:name,:email,:phone,:address,:genderId,:status)
            returning *
        '''
    )

    def insert(self, data: dict) -> dict:
        with db.session.begin():
            insert_gender = {
                "name": data.get('name'),
                "email": data.get('email'),
                "phone": data.get('phone'),
                "address": data.get('address'),
                "genderId": data.get('gender_id'),
                "status": data.get('status')
            }
            result = db.session.execute(
                self.insert_sql,
                insert_gender
            ).mappings().first()
            if result is None:
                raise BadRequest('Failed to insert new student')
            return result
    get_sql = text(
        '''select
        s.id,
        s.name,
        s.email,
        s.phone,
        s.address,
        s.status,
        g.name as "gender",
        s.created_at
        from student s
        left join gender g on g.id = s.gender_id
        order by s.created_at desc
        '''
    )

    get_query_sql = text(
        '''select
            s.id,
        s.name,
        s.email,
        s.phone,
        s.address,
        s.status,
        g.name as "gender",
        s.created_at
        from student s
        left join gender g on g.id = s.gender_id
        where s.name ilike :query
        or s.email ilike :query
        or s.phone ilike :query
        or g.name ilike :query
        order by s.created_at desc
        '''
    )

    def get(self) -> list[dict]:
        with db.session.begin():
            results = db.session.execute(
                self.get_sql
            ).mappings().fetchall()
            return results

    def get_query(self, query: str) -> list[dict]:
        with db.session.begin():
            results = db.session.execute(
                self.get_query_sql,
                {"query": f'%{query}%'}
            ).mappings().fetchall()
            return results

    edit_sql = text(
        '''update student
            set
            name=coalesce(:name, student.name),
            email=coalesce(:email, student.email),
            phone=coalesce(:phone, student.phone),
            address=coalesce(:address, student.address),
            gender_id=coalesce(:gender_id, student.gender_id),
            status=coalesce(:status, student.status),
            updated_at = now()
            where id=:id
            returning *
        '''
    )

    def edit(self, id: int, data: dict) -> dict:
        needed = {
            "name": data.get('name'),
            "email": data.get('email'),
            "phone": data.get('phone'),
            "address": data.get('address'),
            "gender_id": data.get('gender_id'),
            "status": data.get('status'),
            "id": id
        }
        with db.session.begin():
            result = db.session.execute(
                self.edit_sql,
                needed
            ).mappings().first()
            if not result:
                raise NotFound(f'Failed to update student with id={id}')
            return result

    remove_sql = text(
        '''delete from student
            where id=:id
        '''
    )

    def remove(self, id: int):
        with db.session.begin():
            row = db.session.execute(
                self.remove_sql,
                {"id": id}
            )
            if row.rowcount != 1:
                raise LookupError(f'Failed to delete student with id={id}')
