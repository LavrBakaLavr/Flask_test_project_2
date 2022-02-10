from flask import Flask, jsonify, request, session
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager

app = Flask(__name__)

client = app.test_client()

engine = create_engine('sqlite:///db.sqlite')

session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager(app)

from models import *

Base.metadata.create_all(bind=engine)

tutorials = [
    {
        'id': 1,
        'title': 'Video #1. Intro',
        'description': 'GET, POST routes'
    },
    {
        'id': 2,
        'title': 'Video #2. More features',
        'description': 'PUT, DELETE routes'
    }
]


@app.route('/tutorials', methods=['GET'])
def get_list():
    videos = Video.query.all()
    serialized = []
    for video in videos:
        serialized.append({
            'id': video.id,
            'name': video.name,
            'description': video.description
        })
    return jsonify(serialized)


@app.route('/tutorials', methods=['POST'])
def update_list():
    new_one = Video(**request.json)
    session.add(new_one)
    session.commit()
    serialized = {
            'id': new_one.id,
            'name': new_one.name,
            'description': new_one.description
        }
    return jsonify(serialized)


@app.route('/tutorials/<int:tutorial_id>', methods=['PUT'])
def update_tutorial(tutorial_id):
    item = Video.query.filter(Video.id == tutorial_id).first()
    params = request.json
    if not item:
        return {'message': 'No tutorials with this id'}, 400
    for key, value in params.items():
        setattr(item, key, value)
    session.commit()
    serialized = {
            'id': item.id,
            'name': item.name,
            'description': item.description
        }
    return jsonify(serialized)


@app.route('/tutorials/<int:tutorial_id>', methods=['DELETE'])
def delete_tutorial(tutorial_id):
    item = Video.query.filter(Video.id == tutorial_id).first()
    params = request.json
    if not item:
        return {'message': 'No tutorials with this id'}, 400
    session.delete(item)
    session.commit()
    return '', 204

@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

if __name__ == '__main__':
    app.run(debug=True)