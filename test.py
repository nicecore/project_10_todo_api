import base64
import unittest
from peewee import SqliteDatabase
from playhouse.test_utils import test_database
from app import app
from models import Todo, User
from base64 import b64encode

TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([User, Todo], safe=True)


class UserModelAndAuthTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_create_user(self):
        with test_database(TEST_DB, (User,)):
            # Test PUT request to /users with incorrect password
            resp = self.app.post(
                '/api/v1/users',
                data={
                    'username': 'adamdc',
                    'email': 'adamdc@adam.com',
                    'password': 'adam',
                    'verify_password': 'madam'
                }
            )
            self.assertEqual(resp.status_code, 400)
            # Test PUT request to /users with correct password
            resp = self.app.post(
                '/api/v1/users',
                data={
                    'username': 'adamdc',
                    'email': 'adamdc@adam.com',
                    'password': 'adam',
                    'verify_password': 'adam'
                }
            )
            self.assertEqual(resp.status_code, 201)

            # Test GET request to token endpoint
            headers = {'Authorization': 'Basic ' + base64.b64encode(
                bytes('adamdc' + ':' + 'adam', 'ascii')
            ).decode('ascii')}
            resp = self.app.get('/api/v1/users/token', headers=headers)
            self.assertEqual(resp.status_code, 200)

    def test_basic_auth(self):
        with test_database(TEST_DB, (User,)):
            # Test unauthenticated attempt to get key
            adam = User.create_user('adamc', 'adamc@adam.com', 'password')
            resp = self.app.get('/api/v1/users/token')
            self.assertEqual(resp.status_code, 401)

            # Test attempt to get key with basic auth
            resp = self.app.get(
                '/api/v1/users/token',
                headers={'Authorization': 'Basic {}'.format(b64encode(
                    b"adamc:password").decode("ascii"))}
            )
            self.assertEqual(resp.status_code, 200)

            # Test attempt to get key with incorrect password
            resp = self.app.get(
                '/api/v1/users/token',
                headers={'Authorization': 'Basic {}'.format(b64encode(
                    b"adamc:wrong_password").decode("ascii"))}
            )
            self.assertEqual(resp.status_code, 500)


class TodoTests(unittest.TestCase):

    def setUp(self):
        # Create a test client
        self.app = app.test_client()
        self.app.testing = True

    def test_home(self):
        """Test home page"""
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn("todoListApp", str(resp.data))

    def test_item(self):
        """Tests for GET, POST, PUT, and DELETE methods"""
        resp = self.app.post('/api/v1/todos', data={'name': 'Test the app.'})
        self.assertEqual(resp.status_code, 401)
        headers = {'Authorization': 'Basic ' + base64.b64encode(
            bytes('adam' + ':' + 'password', 'ascii')
        ).decode('ascii')}

        with test_database(TEST_DB, (User, Todo)):
            User.create_user('adam', 'adam@adam.com', 'password')
            response = self.app.post(
                '/api/v1/todos',
                headers=headers,
                data={'name': 'Test the app again.'}
            )
            self.assertEqual(response.status_code, 201)

            resp = self.app.get('/api/v1/todos')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Test the app', str(resp.data))
            todo = Todo.get(name='Test the app again.')

            # Test GET method on one Todo
            resp = self.app.get('/api/v1/todos/{}'.format(todo.id))
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Test the app again', str(resp.data))

            # Test PUT method on one Todo
            resp = self.app.put(
                '/api/v1/todos/{}'.format(todo.id),
                data={'name': 'Mow the lawn'},
                headers=headers
            )

            self.assertIn('/api/v1/todos/{}'.format(todo.id),
                          resp.headers['Location'])
            query = Todo.get(name='Mow the lawn')

            # Test DELETE method on one Todo
            resp = self.app.delete(
                '/api/v1/todos/{}'.format(todo.id),
                headers=headers
            )
            self.assertEqual(resp.status_code, 204)


if __name__ == '__main__':
    unittest.main()
