import unittest
from marshmallow import (Schema, fields, ValidationError,
        post_dump,post_load,validates, validates_schema)

from courier_app.send_it_apis.v1.models import (SystemUsers,
    SendItParcels, SendItUserOrders)

from courier_app.send_it_apis.v1.validators.user_model_validators 
    import (CreateUserSchema,EditUserSchema, UserIdSchema)

class UserValidatorsCase(unittest.TestCase):

    def setUp(self):
        self.user_1= {
            "username": "etomovich",
            "email": "etolejames@gmail.com",
            "phoneNo":"0717823158",
            "role": "Admin",
            "password": "etomovich"
        }
        self.user_2= {
                "username":"pogie",
                "email":"paulpogba@gmail.com",
                "role":"User",
                "phoneNo":"07157674544548",
                "password":"pogie"
            }
        
        users_DB = SystemUsers(0000)
        answ = users_DB.add_user(self.user_1['username'],self.user_1['email'],\
            self.user_1['phoneNo'],self.user_1['password'],\
            self.user_1['role'])

        answ = users_DB.add_user(self.user_2['username'],self.user_2['email'],\
            self.user_2['phoneNo'],self.user_2['password'],\
            self.user_2['role'])
        
        self.etomovich_id = ""
        self.pogie_id = ""
        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['username'] \
            == "etomovich":
                self.etomovich_id = item
            if SystemUsers.send_it_users[item]['username'] \
            == "pogie":
                self.pogie_id = item

    def tearDown(self):
        SystemUsers.send_it_users = {}
        SendItParcels.sendit_parcels ={}
        SendItUserOrders.sendit_user_orders ={}
        
    def test_create_user_schema(self):
        my_data = {
            "username":"pato",
            "email":"pato@gmail.com",
            "phone_number":"455667",
            "password":"pato",
            "retype_password":"pato",
            "role":"Admin"
        }


        #validate role
        my_data["role"] = "etole"
        schema = CreateUserSchema()
        result = schema.load(my_data)

        self.assertTrue(("role" in result.errors), msg="role validator"+
        " is not working properly")
        my_data["role"] = "Admin"

        #validate username
        my_data["username"] = "etomovich"
        schema = CreateUserSchema()
        result = schema.load(my_data)

        self.assertTrue(("username" in result.errors), msg="username validator"+
        " is not working properly")
        my_data["username"] = "pato"

        #validate phone number
        my_data["phone_number"] = "0717823158"
        schema = CreateUserSchema()
        result = schema.load(my_data)

        self.assertTrue(("phone_number" in result.errors), msg="phone_number"+
        "validator is not working properly")
        my_data["phone_number"] = "455667"

        #validate email
        my_data["email"] = "etolejames@gmail.com"
        schema = CreateUserSchema()
        result = schema.load(my_data)

        self.assertTrue(("email" in result.errors), msg="email"+
        "validator is not working properly")
        my_data["email"] = "pato@gmail.com"

    def test_edit_user_schema(self):
        my_data = {
            "user_id":567866555,
            "username":"pato",
            "email":"pato@gmail.com",
            "phone_number":"455667",
            "password":"pato",
            "retype_password":"pato",
            "role":"Admin"
        }

        #validate user_id
        my_data["user_id"] = 567866555
        schema = EditUserSchema()
        result = schema.load(my_data)

        self.assertTrue(("user_id" in result.errors), msg="user_id"+
        "validator is not working properly")
        my_data["user_id"] = self.pogie_id


        #validate role
        my_data["role"] = "etole"
        schema = EditUserSchema()
        result = schema.load(my_data)

        self.assertTrue(("role" in result.errors), msg="role validator"+
        " is not working properly")
        my_data["role"] = "Admin"

        #validate username
        my_data["username"] = "etomovich"
        schema = EditUserSchema()
        result = schema.load(my_data)

        self.assertTrue(("username" in result.errors), msg="username validator"+
        " is not working properly")
        my_data["username"] = "pato"

        #validate email
        my_data["email"] = "etolejames@gmail.com"
        schema = EditUserSchema()
        result = schema.load(my_data)

        self.assertTrue(("email" in result.errors), msg="email"+
        "validator is not working properly")
        my_data["phone_number"] = "pato@gmail.com"


    def test_user_id_schema(self):
        my_data = {
            "user_id":567866555
        }

        #validate user_id
        my_data["user_id"] = 567866555
        schema = UserIdSchema()
        result = schema.load(my_data)

        self.assertTrue(("user_id" in result.errors), msg="user_id"+
        "validator is not working properly")
        my_data["user_id"] = self.pogie_id

