from app import db, session, Base
from flask_jwt_extended import create_access_token
from datetime import timedelta
from passlib.hash import bcrypt


class User(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    wallet = db.Column(db.Integer, default=100)

    def __init__(self, **kwargs):
        self.login = kwargs.get('login')
        self.password = bcrypt.hash(kwargs.get('password'))

    def get_token(self, expire_time=24):
        expire_delta = timedelta(expire_time)
        token = create_access_token(
            identity=self.id, expires_delta=expire_delta)
        return token

    @classmethod
    def authenticate(cls, login, password):
        user = cls.query.filter(cls.login == login).one()
        if not bcrypt.verify(password, user.password):
            raise Exception('No user with this password')
        return user