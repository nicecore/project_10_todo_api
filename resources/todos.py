from flask import Blueprint, g, make_response
from flask_restful import (Resource, Api, reqparse,
                           fields, marshal,
                           marshal_with, url_for)
import models
from auth import auth
import json


todo_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'created_at': fields.DateTime,
    'created_by': fields.String
}


class TodoList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='Please provide a name',
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        todos = [marshal(todo, todo_fields)
                 for todo in models.Todo.select()]
        return todos

    @auth.login_required
    @marshal_with(todo_fields)
    def post(self):
        args = self.reqparse.parse_args()
        user = g.user
        todo = models.Todo.create(created_by=user, **args)
        return todo, 201


class Todo(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='Please provide a name',
            location=['form', 'json']
        )
        super().__init__()

    @marshal_with(todo_fields)
    def get(self, id):
        todo = models.Todo.get(models.Todo.id == id)
        return todo

    @marshal_with(todo_fields)
    @auth.login_required
    def put(self, id):
        args = self.reqparse.parse_args()
        try:
            user = g.user
            todo = models.Todo.select().where(
                models.Todo.created_by == user,
                models.Todo.id == id
            ).get()
        except models.Todo.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'That todo does not exist or is not editable.'}
            ), 403)
        query = todo.update(**args)
        query.execute()
        return (models.Todo.get(models.Todo.id == id), 200,
                {'Location': url_for('resources.todos.todo', id=id)})

    @auth.login_required
    def delete(self, id):
        query = models.Todo.delete().where(models.Todo.id == id)
        query.execute()
        return '', 204


todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(
    TodoList,
    '/todos',
    endpoint='todos'
)
api.add_resource(
    Todo,
    '/todos/<int:id>',
    endpoint='todo'
)
