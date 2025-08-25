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

    def insert_many(self, items: list[dict]) -> list[dict]:
        results = []
        with db.session.begin():
            for s in items:
                need = {
                    "name": s.get('name'),
                    "email": s.get('email'),
                    "phone": s.get('phone'),
                    "address": s.get('address'),
                    "genderId": s.get('gender_id'),
                    "status": s.get('status')
                    }
                result = db.session.execute(
                         self.insert_sql,
                         need
                         ).mappings().first()
                results.append(result)
            return results

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
            returning 1
        '''
    )
    update_count = text(
        '''update course
            set current_students = current_students - 1,
            updated_at = now()
            where id=any(:ids)
            and current_students > 0
        '''
    )

    def remove(self, id: int, courseIds: list[int]):
        with db.session.begin():
            row = db.session.execute(
                self.remove_sql,
                {"id": id}
            )
            if row.rowcount != 1:
                raise LookupError(f'Failed to delete student with id={id}')
            if courseIds:
                db.session.execute(
                    self.update_count,
                    {"ids": courseIds}
                )
    get_id_sql = text(
        '''select
            s.id,
            s.name,
            s.email,
            s.phone,
            s.address,
            s.status,
            s.created_at,
            g.name as "gender",
            coalesce(
            jsonb_agg(
            jsonb_build_object(
            'courseId',c.id,
            'courseName',c.name,
            'description',c.description,
            'studentLimit',c.student_limit,
            'currentStudents',c.current_students,
            'courseStatus',c.status,
            'startDate',c.start_date,
            'endDate',c.end_date,
            'createdAt',c.created_at
            )
            order by c.created_at desc
            ) filter (where c.id is not null),
            '[]'::jsonb
            ) as courses
            from student s
            left join gender g on g.id = s.gender_id
            left join student_course sc on sc.student_id = s.id
            left join course c on c.id = sc.course_id
            where s.id=:id
            group by s.id,s.name,s.email,s.phone,s.address,s.status,
            g.name
        '''
    )

    join_query_sql = text(
        '''select
            s.id,
            s.name,
            s.email,
            s.phone,
            s.address,
            s.status,
            s.created_at,
            g.name as "gender",
            coalesce(
            jsonb_agg(
            jsonb_build_object(
            'courseId',c.id,
            'courseName',c.name,
            'description',c.description,
            'studentLimit',c.student_limit,
            'currentStudents',c.current_students,
            'courseStatus',c.status,
            'startDate',c.start_date,
            'endDate',c.end_date,
            'createdAt',c.created_at
            )
            order by c.created_at desc
            ) filter (where c.id is not null),
            '[]'::jsonb
            ) as courses
            from student s
            left join gender g on g.id = s.gender_id
            left join student_course sc on sc.student_id = s.id
            left join course c on c.id = sc.course_id
            where s.name ilike :query
            group by s.id,s.name,s.email,s.phone,s.address,s.status,
            g.name
            order by s.created_at desc
        '''
    )
    get_join_sql = text(
        '''select
            s.id,
            s.name,
            s.email,
            s.phone,
            s.address,
            s.status,
            s.created_at,
            g.name as "gender",
            coalesce(
            jsonb_agg(
            jsonb_build_object(
            'courseId',c.id,
            'courseName',c.name,
            'description',c.description,
            'studentLimit',c.student_limit,
            'currentStudents',c.current_students,
            'courseStatus',c.status,
            'startDate',c.start_date,
            'endDate',c.end_date,
            'createdAt',c.created_at
            )
            order by c.created_at desc
            ) filter (where c.id is not null),
            '[]'::jsonb
            ) as courses
            from student s
            left join gender g on g.id = s.gender_id
            left join student_course sc on sc.student_id = s.id
            left join course c on c.id = sc.course_id
            group by s.id,s.name,s.email,s.phone,s.address,s.status,
            g.name
            order by s.created_at desc
        '''
    )

    def get_id(self, id: int) -> dict:
        with db.session.begin():
            result = db.session.execute(
                self.get_id_sql,
                {"id": id}
            ).mappings().first()
            if result is None:
                raise NotFound(f'Student with id={id} Not found')
            return result

    def get_join_query(self, query: str) -> dict:
        with db.session.begin():
            result = db.session.execute(
                self.join_query_sql,
                {"query": f'%{query}%'}
            ).mappings().fetchall()
            if result is None:
                raise NotFound(f'Student with query={query} Not found')
            return result

    def get_join(self) -> dict:
        with db.session.begin():
            result = db.session.execute(
                self.get_join_sql,
            ).mappings().all()
            if result is None:
                raise NotFound('Students Not found')
            return result
    status_sql = text(
        '''select status from student
            where id=:id
        '''
    )
    join_check = text(
        '''select 1 from student_course
            where student_id=:studentId
            and course_id=:courseId
        '''
    )
    check_limit = text(
        '''select 1 from course
            where id = :courseId
            and status = true
            and current_students < student_limit
        '''
    )
    join_sql = text(
        '''insert into student_course
            (student_id,course_id)
            select :studentId, unnest(:courseIds)
            on conflict do nothing
            returning course_id
        '''
    )
    count_sql = text(
        '''update course
            set current_students = current_students + 1,
            updated_at = now()
            where id=any(:courseIds)
            returning id
        '''
    )

    def make_join(self, studentId: int, courseIds: list[int]):
        valid_courseIds: list[int] = []
        result = {
            "join": [],
            "skip": [],
            "valid_course": [],
            "course_full": False
        }
        with db.session.begin():
            status = db.session.execute(
                self.status_sql,
                {"id": studentId}
            ).scalar()
            if not status:
                return {
                    "error": True,
                    "status": 403,
                    "detail": f"Sid {studentId} is Inactive"
                }
            for id in courseIds:
                check = db.session.execute(
                    self.join_check,
                    {
                        "studentId": studentId,
                        "courseId": id
                    }
                ).scalar()
                if check:
                    result["skip"].append(
                        {
                            "sid": studentId,
                            "cid": id,
                            "reason": f"Sid {studentId} already join with cid {id}"
                        }
                    )
                    continue
                check_limit = db.session.execute(
                    self.check_limit,
                    {
                        "courseId": id
                    }
                ).scalar()
                if check_limit:
                    valid_courseIds.append(id)
                    result["join"].append(
                        {
                            "cid": id,
                            "reason": f'Course {id} status active'
                        }
                    )
                    result['valid_course'].append(
                        {
                            "cid": id
                        }
                    )
                else:
                    result['skip'].append(
                        {
                            "cid": id,
                            "reason": f'Cid {id} is inactive or reach limit'
                        }
                    )
            if not valid_courseIds:
                return {
                    "error": False,
                    "status": 200,
                    "message": "There is no valid course for join with student",
                    "data": result
                }
            join = db.session.execute(
                self.join_sql,
                {
                 "studentId": studentId,
                 "courseIds": valid_courseIds
                 }
            ).scalars().all()
            if join:
                db.session.execute(
                    self.count_sql,
                    {
                        "courseIds": valid_courseIds
                    }
                    ).scalars().all()
            return {
                "error": False,
                "status": 201,
                "message": f"Courses success join with sid {studentId}",
                "data": result
            }
    dec_count = text(
        '''update course set
            current_students = GREATEST(current_students - 1,0),
            updated_at = now()
            where id = :courseId
            returning 1
        '''
    )
    cancel_sql = text(
        '''delete from student_course
            where student_id=:studentId
            and course_id=:courseId
            returning 1
        '''
    )

    def cancel_join(self, studId: int, couId: int):
        with db.session.begin():
            need = {
                "studentId": studId,
                "courseId": couId
            }
            check = db.session.execute(
                self.join_check,
                need
            ).scalar()
            if check is None:
                return {
                    "error": True,
                    "status": 404,
                    "detail": f'Not found the course id={couId}'
                    f'With join of student id={studId}'
                }
            cancel = db.session.execute(
                self.cancel_sql,
                need
            ).scalar()
            if cancel is None:
                raise LookupError(
                    f'Failed to delete the course id={couId}'
                    f'With join of student id={studId}'
                )
            dec = db.session.execute(
                self.dec_count,
                {"courseId": couId}
            ).scalar()
            if dec is None:
                raise LookupError(
                    f'Failed to decrease the current students of'
                    f'course with id={couId}'
                )
            return {
                "error": False,
                "status": 200,
                "detail": 'Cancel join student with course success'
            }
    s_s_sql = text(
        '''select count(*) from student
            where status = :status
        '''
    )
    c_c_sql = text(
        '''select count(*) from course
            where status = :status
        '''
    )
    s_g_sql = text(
        '''select count(*) from student
            where gender_id = :n
        '''
    )

    def detail(self):
        with db.session.begin():
            s_s_t = db.session.execute(
                self.s_s_sql,
                {"status": True}
            ).scalar()
            s_s_f = db.session.execute(
                self.s_s_sql,
                {"status": False}
            ).scalar()
            s_g_m = db.session.execute(
                self.s_g_sql,
                {"n": 1}
            ).scalar()
            s_g_f = db.session.execute(
                self.s_g_sql,
                {"n": 2}
            ).scalar()
            s_g_o = db.session.execute(
                self.s_g_sql,
                {"n": 3}
            ).scalar()
            c_s_t = db.session.execute(
                self.c_c_sql,
                {"status": True}
            ).scalar()
            c_s_f = db.session.execute(
                self.c_c_sql,
                {"status": False}
            ).scalar()
            return {
                "s_s_t": s_s_t,
                "s_s_f": s_s_f,
                "s_g_m": s_g_m,
                "s_g_f": s_g_f,
                "s_g_o": s_g_o,
                "c_s_t": c_s_t,
                "c_s_f": c_s_f
            }
