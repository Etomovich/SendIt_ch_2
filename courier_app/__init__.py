from flask import Flask
from instance.config import Config
from courier_app.send_it_apis.v1 import bp as api_v1_bp
from courier_app.send_it_apis.v1 import v1_bp
    
def create_app(config_class = Config):
    '''This method creates the flask instance and returns it.'''
    app = Flask(__name__)
    app.config.from_object(config_class)

    v1_bp.init_app(app) 

    app.register_blueprint(api_v1_bp, url_prefix="/api/v1")

    return app