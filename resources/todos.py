from flask import Blueprint
from flask_restful import (Resource, Api, reqparse, 
                            fields, marshal,
                            marshal_with, url_for)
from auth import auth
import models



todo_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'created_at': fields.DateTime
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


    @marshal_with(todo_fields)
    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        todo = models.Todo.create(**args)
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
    @auth.login_required
    def put(self, id):
        args = self.reqparse.parse_args()
        query = models.Todo.update(**args).where(models.Todo.id == id)
        query.execute()
        return models.Todo.get(models.Todo.id == id), 200

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






