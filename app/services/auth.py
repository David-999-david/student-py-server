from sqlalchemy import text
from app.extensions import db
from flask_jwt_extended import (
    create_access_token, create_refresh_token
)


class auth_service():
    login_sql = text(
        '''select * from users
            where email=:email and
            password=:password
        '''
    )

    def login(self, data: dict) -> tuple[str, str]:
        with db.session.begin():
            user = db.session.execute(
                self.login_sql,
                {"email": data.get('email'),
                 "password": data.get('password')
                 }
            ).mappings().first()
            userId = user['id']
            access = create_access_token(identity=userId)
            refresh = create_refresh_token(identity=userId)
            return access, refresh
