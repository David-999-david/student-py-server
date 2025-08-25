from sqlalchemy import text
from app.extensions import db
from flask_jwt_extended import (
    create_access_token, create_refresh_token
)


class auth_service():
    exist_sql = text(
        '''select * from users
            where email=:email
        '''
    )
    psw_sql = text(
        '''select password from users
            where id = :id
        '''
    )

    def login(self, data: dict) -> tuple[str, str]:
        with db.session.begin():
            user = db.session.execute(
                self.exist_sql,
                {"email": data.get('email'),
                 }
            ).mappings().first()
            if user is None:
                return {
                    "error": True,
                    "status": 404,
                    "detail": "User not found"
                }
            userId = user['id']
            psw = db.session.execute(
                self.psw_sql,
                {
                 "id": userId
                 }
            ).mappings().first()
            inputpsw = data.get('password')
            correct = inputpsw == psw['password']
            if not correct:
                return {
                    "error": True,
                    "status": 401,
                    "detail": "Incorrect password"
                }
            access = create_access_token(identity=userId)
            refresh = create_refresh_token(identity=userId)
            return {
                "error": False,
                "status": 200,
                "access": access,
                "refresh": refresh
            }
