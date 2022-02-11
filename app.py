from flask import Flask, jsonify, request, session
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

client = app.test_client()

engine = create_engine('sqlite:///db.sqlite')

session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager(app)

from models import *

Base.metadata.create_all(bind=engine)

@app.route('/info', methods=['GET'])
@jwt_required()
def get_info():
    user_id = get_jwt_identity()
    wallet = User.query.filter(User.id == user_id)

    if wallet[0].wallet <= 0 :
        return jsonify({'error': 'Your wallet is empty'})
        
    else :
        wallet[0].wallet = wallet[0].wallet - 1
        session.commit()

        return jsonify({'wallet': wallet[0].wallet})

@app.route('/register', methods=['POST'])
def register():
    params = request.json
    user = User(**params)
    session.add(user)
    session.commit()
    token = user.get_token()
    return {'access_token': token}

@app.route('/auth', methods=['POST'])
def auth():
    params = request.json
    user = User.authenticate(**params)
    token = user.get_token()
    return {'access_token': token}
    
@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

if __name__ == '__main__':
    app.run(debug=True)