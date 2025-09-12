from flask import Flask, abort
from .handlers import error

def create_app():
    app = Flask(__name__)

    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.generic)

    @app.route('/')
    def home():
        return "¡Hola mundo!"
    
    @app.route('/private')
    def private():
        abort(401)

    @app.route('/error')
    def trigger_error():
        abort(500)

    return app
