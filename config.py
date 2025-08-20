import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta

basedir = Path(__file__).parent
load_dotenv(basedir / '.env')


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Development(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_ECHO = True

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_LOCATION = ["headers"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=10)
