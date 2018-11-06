from flask import Flask
from instance.config import Config

def create_app(config_class = Config):
    '''This method creates the flask instance and returns it.'''
    app = Flask(__name__)
    app.config.from_object(config_class)

    return app