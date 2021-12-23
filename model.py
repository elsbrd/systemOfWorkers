from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '12345'
    app.config['MYSQL_DB'] = 'course'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    return app
