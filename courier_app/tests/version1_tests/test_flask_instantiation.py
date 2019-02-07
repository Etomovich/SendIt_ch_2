import unittest
from flask import Flask
from courier_app import create_app

class FlaskRegistrationCase(unittest.TestCase):
    def test_create_app_serves_flask_app(self):
        self.assertTrue(isinstance(create_app(), Flask ), \
                msg="create app does not serve a flask instance")

if __name__ == "__main__":
    unittest.main(verbosity=2)