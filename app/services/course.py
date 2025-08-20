from sqlalchemy import text
from app.extensions import db
from werkzeug.exceptions import NotFound


class CourseService():
    insert_sql = text(
        '''insert into course
            (name,description,student_limit,
            current_students,start_date,end_date
            )
            values
            (:name,:description,:student_limit,
            :current_students,:start_date,:end_date
            )
            returning *
        '''
    )

    def insert(self, data: dict) -> dict:
        need = {
            "name": data.get('name'),
            "description": data.get('description'),
            "student_limit": data.get('student_limit'),
            "current_students": data.get('current_students'),
            "start_date": data.get("start_date"),
            "end_date": data.get('end_date')
        }
        with db.session.begin():
            result = db.session.execute(
                self.insert_sql,
                need
            ).mappings().first()
            if result is None:
                raise NotFound("Insert course failed")
            return result
