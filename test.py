import base64
import unittest

from app import app
from models import Todo


class TodoTests(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        self.app.testing = True


    def test_home(self):
        """Test home page"""
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<body ng-app="todoListApp">', str(resp.data))


    def test_item(self):
        """Tests for GET, POST, PUT, and DELETE methods"""
        resp = self.app.post('/api/v1/todos', data={'name': 'Mow the yard'})
        self.assertEqual(resp.status_code, 201)

        # Test GET request on all Todos
        resp = self.app.get('/api/v1/todos')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Mow the yard', str(resp.data))
        todo = Todo.get(name='Mow the yard')

        # Test GET method on one Todo
        resp = self.app.get('/api/v1/todos/{}'.format(todo.id))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Mow the yard', str(resp.data))

        # Test PUT method on one Todo
        resp = self.app.put('/api/v1/todos/{}'.format(todo.id),
                              data={'name': 'Mow the lawn'})
        self.assertIn('/api/v1/todos/{}'.format(todo.id),
                      resp.headers['Location'])
        query = Todo.get(name='Mow the lawn')

        # Test DELETE method on one Todo
        resp = self.app.delete('/api/v1/todos/{}'.format(todo.id))
        self.assertEqual(resp.status_code, 204)


if __name__ == '__main__':
    unittest.main()