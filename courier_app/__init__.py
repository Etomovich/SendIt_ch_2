from flask import Flask
import psycopg2
from instance.config import Config, TestConfiguration
from courier_app.send_it_apis.v1 import bp as api_v1_bp
from courier_app.send_it_apis.v1 import v1_bp
from courier_app.database import connection,create_relations,create_test_relations
from courier_app.send_it_apis.v2 import bp as api_v2_bp
from courier_app.send_it_apis.v2 import v2_bp
    
def create_app(config_class =Config):
    '''This method creates the flask instance and returns it.'''
    app = Flask(__name__)
    app.config.from_object(config_class)    
    
    my_tables = create_relations()

    my_test_relations = create_test_relations()
        
    v1_bp.init_app(app)

    v2_bp.init_app(app) 

    app.register_blueprint(api_v1_bp, url_prefix="/api/v1")
    app.register_blueprint(api_v2_bp, url_prefix="/api/v2")

    return app