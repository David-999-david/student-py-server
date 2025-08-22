from sqlalchemy import text
from app.extensions import db
from werkzeug.exceptions import NotFound, BadRequest


class CourseService():
    insert_sql = text(
        '''insert into course
            (name,description,status,student_limit
            ,start_date,end_date
            )
            values
            (:name,:description,:status,:student_limit
            ,:start_date,:end_date
            )
            returning *
        '''
    )

    def insert(self, data: dict) -> dict:
        need = {
            "name": data.get('name'),
            "description": data.get('description'),
            "status": data.get('status'),
            "student_limit": data.get('student_limit'),
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

    def insert_many(self, items: list[dict]) -> list[dict]:
        results = []
        with db.session.begin():
            for s in items:
                need = {
                    "name": s.get('name'),
                    "description": s.get('description'),
                    "status": s.get('status'),
                    "student_limit": s.get('student_limit'),
                    "start_date": s.get("start_date"),
                    "end_date": s.get('end_date')
                            }
                result = db.session.execute(
                            self.insert_sql,
                            need
                            ).mappings().first()
                results.append(result)
            return results
    get_all_sql = text(
        '''select * from course
            order by created_at desc
        '''
    )
    get_query_sql = text(
        '''select * from course
            where name ilike :query
            or description ilike :query
            order by created_at desc
        '''
    )

    def get_all(self) -> list[dict]:
        with db.session.begin():
            results = db.session.execute(
                self.get_all_sql
            ).mappings().fetchall()
            return results

    def get_query(self, query: str) -> list[dict]:
        with db.session.begin():
            results = db.session.execute(
                self.get_query_sql,
                {
                    "query": f'%{query}%'
                }
            ).mappings().fetchall()
            return results
    updated_sql = text(
        '''update course set
            name = coalesce(:name, course.name),
            description = coalesce(:description, course.description),
            status = coalesce(:status, course.status),
            student_limit = coalesce(:student_limit, course.student_limit),
            start_date = coalesce(:start_date, course.start_date),
            end_date = coalesce(:end_date, course.end_date),
            updated_at = now()
            where id = :id
            returning *
        '''
    )

    def update(self, id: int, data: dict) -> dict:
        need = {
            "name": data.get('name'),
            "description": data.get('description'),
            "status": data.get('status'),
            "student_limit": data.get('student_limit'),
            "start_date": data.get('start_date'),
            "end_date": data.get('end_date'),
            "id": id
        }
        with db.session.begin():
            result = db.session.execute(
                self.updated_sql,
                need
            ).mappings().first()
            if result is None:
                raise BadRequest(f'Error when update course with id={id}')
            return result
    delete_sql = text(
        '''delete from course
            where id=:id
        '''
    )

    def delete(self, id: int):
        with db.session.begin():
            row = db.session.execute(
                self.delete_sql,
                {"id": id}
            )
            if row.rowcount != 1:
                raise BadRequest(f'Delete course with id={id} Failed')
    get_id_sql = text(
        '''select
            c.id as "courseId",
            c.name as "course_name",
            c.description as "description",
            c.status as "courseStatus",
            c.student_limit as "student_limit",
            c.current_students as "current_students",
            c.start_date as "start_date",
            c.end_date as "end_date",
            c.created_at as "course_created_at",
            coalesce(
            jsonb_agg(
            jsonb_build_object(
            'studentId',s.id,
            'studentName',s.name,
            'studentStatus',s.status
            )
            ) filter (where s.id is not null),
            '[]'::jsonb
            ) as students
            from course c
            left join student_course sc on sc.course_id = c.id
            left join student s on s.id = sc.student_id
            where c.id = :id
            group by c.id,c.name,c.status,c.student_limit,c.current_students,
            c.start_date,c.end_date,c.created_at
            order by c.created_at desc
        '''
    )

    def get_id(self, id: int) -> dict:
        with db.session.begin():
            result = db.session.execute(
                self.get_id_sql,
                {"id": id}
            ).mappings().first()
            if result is None:
                raise NotFound(f'Course with id={id} not found')
            return result
    check_limit = text(
        '''select student_limit,current_students,status
            from course where id=:courseId
        '''
    )
    check_join = text(
        '''select 1 from student_course
            where student_id = :studentId
            and course_id= :courseId
        '''
    )
    join_sql = text(
        '''insert into student_course
            (student_id,course_id)
            values
            (:studentId, :courseId)
            on conflict(student_id,course_id)
            do nothing
            returning 1
        '''
    )
    plus_student = text(
        '''update course
            set current_students =current_students + :n
            where id=:courseId
            returning current_students
        '''
    )
    stud_status_sql = text(
        '''select status
            from student
            where id=:id
        '''
    )

    def join(self, courseId: int, studentIds: list[int]):
        count = 0
        with db.session.begin():
            limit_check = db.session.execute(
                    self.check_limit,
                    {"courseId": courseId}
                    ).mappings().fetchone()
            if limit_check is None:
                raise LookupError(f'Course with id{courseId} not found')
            limit = limit_check['student_limit']
            current = limit_check['current_students']
            status = limit_check['status']
            if current >= limit:
                raise LookupError(f'The course with id={courseId}'
                                  'limit had reach')
            for id in studentIds:
                status_check = db.session.execute(
                    self.stud_status_sql,
                    {"id": id}
                ).mappings().fetchone()
                stud_status = status_check['status']
                if not stud_status:
                    continue
                if not status:
                    break
                if current >= limit:
                    break
                need = {
                    "studentId": id,
                    "courseId": courseId
                }
                check = db.session.execute(
                    self.check_join,
                    need
                ).fetchone()
                if check is not None:
                    continue
                join_row = db.session.execute(
                    self.join_sql,
                    need
                ).fetchone()
                if join_row is not None:
                    count += 1
            after = db.session.execute(
                self.plus_student,
                {
                    "courseId": courseId,
                    "n": count
                }
            ).fetchone()
            if after is None:
                raise RuntimeError('Failed to refresh '
                                   'the newest student count')
    check_sql = text(
        '''select 1 from
            student_course
            where student_id=:studentId
            and course_id=:courseId
        '''
    )
    current_sql = text(
        '''update course
            set
            current_students = current_students - 1,
            updated_at = now()
            where id = :id
            returning 1
        '''
    )
    cancel_join_sql = text(
        '''delete from student_course
            where student_id=:studentId
            and course_id=:courseId
            returning 1
        '''
    )

    def cancel_join(self, courseId: int, studentId: int):
        with db.session.begin():
            need = {
                "studentId": studentId,
                "courseId": courseId
            }
            check = db.session.execute(
                self.check_sql,
                need
            ).scalar()
            if check is None:
                raise NotFound(
                    f'Not found the course id={courseId}'
                    f'With join of student id={studentId}'
                )
            cancel = db.session.execute(
                self.cancel_join_sql,
                need
            ).rowcount
            if cancel == 0:
                raise LookupError(
                    f'Failed to delete the course id={courseId}'
                    f'With join of student id={studentId}'
                )
            decrease = db.session.execute(
                self.current_sql,
                {
                    "id": courseId
                }
            ).scalar()
            if decrease is None:
                raise LookupError(
                    f'Failed to decrease the current students of'
                    f'course with id={courseId}'
                )
