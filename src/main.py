"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from models import db, Todos

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/todos', methods=['GET'])
def get_todos():
    todos = Todos.query.all()
    todos = list(map(lambda todo: todo.serialize(), todos ))
    return jsonify(todos), 200

@app.route('/todos', methods=['POST'])
def post_todos():
    body = request.get_json()    
    if 'done' not in body:
        return 'Invalid todo', 400 
    if 'label' not in body:
        return 'Invalid todo', 400 
    todo = Todos(done=body['done'], label=body['label'])
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.serialize()), 200

@app.route('/todos/<id>', methods=['DELETE'])
def delete_todos(id):
    todo = Todos.query.filter_by(id=id).first_or_404()
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.serialize()), 200

@app.route('/todos', methods=['PUT'])
def put_todos():
    body = request.get_json()
    todo = Todos.query.filter_by(id=body['id']).first_or_404()
    todo.done = body['done']
    todo.label = body['label']
    db.session.commit()
    return jsonify(todo.serialize()), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)