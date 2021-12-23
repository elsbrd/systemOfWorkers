import os
import tempfile
import unittest

import pytest
import requests
from flask import Flask, request, session
from base64 import b64encode

app = Flask(__name__)

with app.test_request_context('/?name=Peter'):
    assert request.path == '/'
    assert request.args['name'] == 'Peter'
from controller import app, login, logout




class TestConfig(unittest.TestCase):
    def test_config_loading(self):
        assert app.config['DEBUG'] is False
        assert app.config['MYSQL_DB'] == 'course'

    URL = "http://127.0.0.1:5000/todolist"

    def test_1_get_all_todos(self):
        resp = requests.get(self.URL)
        self.assertEqual(resp.status_code, 404)
        print("Test 1 completed")

    def test_2_get_all_todos(self):
        resp = requests.post(self.URL)
        self.assertEqual(resp.status_code, 404)
        print("Test 2 completed")

    def test_empty_db(client):
        """Start with a blank database."""

        rv = session.get('/')
        assert b'No entries here so far' in rv.data
        print("Test 3completed")


    def test_login_logout(client):
        """Make sure login and logout works."""

        rv = login(client, app.config['email'], app.config['password'])
        assert b'You were logged in' in rv.data

        rv = logout(client)
        assert b'You were logged out' in rv.data

        rv = login(client, app.config['email'] + 'x', app.config['password'])
        assert b'Invalid username' in rv.data

        rv = login(client, app.config['email'], app.config['password'] + 'x')
        assert b'Invalid password' in rv.data


    @pytest.fixture
    def client(self):
        db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        os.close(db_fd)
        os.unlink(app.config['DATABASE'])


class BasicTest(unittest.TestCase):
    def setUp(self):
         app.config['TESTING'] = True
         app.config['DEBUG'] = False
         self.app = app.test_client()

    def tearDown(self):
         pass
    def test_root(self):
        response = self.app.get('/', follow_redirects = True)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()