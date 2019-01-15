import unittest
import json
from flask import jsonify
from instance.config import Config, TestConfiguration
from courier_app.send_it_apis.v2.models import (SystemUsers,
    SendItParcels)
from itsdangerous import (TimedJSONWebSignatureSerializer
     as Serializer, BadSignature, SignatureExpired)
from courier_app import create_app
from courier_app.database import remove_all_tables, add_root_user

class UserViewsCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            config_class=TestConfiguration,
            testing=True
        )
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.user_1={
            "username":"etomovich",
            "email":"etomovich@gmail.com",
            "phone_number":"078",
            "password":"etole",
            "role":"Admin"
        }
        
        self.user={
            "username":"anthony",
            "email":"anto@gmail.com",
            "phone_number":"+25423",
            "password":"kimani",
            "role":"Admin"
        }
        self.user_1_data = {}
        self.user_1_data["Status"] = "OK"
        self.user_1_data["User"] = add_root_user(
            username = self.user_1["username"],
            email=self.user_1["email"],
            phone_number=self.user_1["phone_number"],
            password=self.user_1["password"],
            role=self.user_1["role"]
        )
        self.user_data = {}
        self.user_data["Status"] = "OK"
        self.user_data["User"] = add_root_user(
            username = self.user["username"],
            email=self.user["email"],
            phone_number=self.user["phone_number"],
            password=self.user["password"],
            role=self.user["role"]
        )
        self.user_2=json.dumps(
            {"username":"anthony",
            "email":"anto",
            "password":"kimani",
            "role":"Admin",
            "retype_password":"kimani"})

        self.user_3=json.dumps(
            {"username":"omushambulizi",
            "email":"lukaku@gmail.com",
            "phone_number":"+25434526777",
            "password":"luka",
            "role":"User",
            "retype_password":"luka"})

        answ= self.client.post("/api/v2/register",
                data=self.user_3,content_type='application/json')

        self.user_3_data = json.loads(answ.data.decode())

        answ= self.client.post("/api/v2/register",
                data=self.user_1,content_type='application/json')

       
    def tearDown(self):
        toa = remove_all_tables()

    def test_create_user(self):
        my_trial = json.dumps(
            {"username":"theuser",
            "email":"theuser@gmail.com",
            "phone_number":"+2543777",
            "password":"theuser",
            "role":"User",
            "retype_password":"theuser"})
        answ= self.client.post("/api/v2/register",
                data=my_trial,content_type='application/json')
        output = json.loads(answ.data.decode())
        print(output)
        self.assertEqual(output['Status'],"Created",
            msg="Register not working properly!")
        self.assertEqual(answ.status_code,201,
            msg="Register not working properly!")

    def test_wrong_create_user(self): 
        answ= self.client.post("/api/v2/register",
                data=self.user_2,content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"Bad Request",
            msg="Register not working properly!")
        self.assertEqual(answ.status_code,400,
            msg="Register not working properly!")

    def test_login_invalid_user(self):
        answ= self.client.post("/api/v2/register",
                data=self.user,content_type='application/json')

        wrong_my_data = json.dumps({
                "username":"anthony",
                "password":"ancom"
            })
        answ= self.client.post("/api/v2/login",
                data=wrong_my_data,
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"Invalid Credentials",
            msg="Login not working properly!")
        self.assertEqual(answ.status_code,401,
            msg="Register not working properly!")

    def test_login_valid_user(self):
        answ= self.client.post("/api/v2/register",
                data=self.user,content_type='application/json')

        right_my_data = json.dumps({
                "username":"anthony",
                "password":"kimani"
            }) 
        answ= self.client.post("/api/v2/login",
                data=right_my_data,
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"Logged In.",
            msg="Login not working properly!")
        self.assertEqual(answ.status_code,200,
            msg="Register not working properly!")

    def test_login_incomplete(self):
        answ= self.client.post("/api/v2/register",
                data=self.user_2,content_type='application/json')

        wrong_my_data = json.dumps({
                "username":"anthony"
            })
        answ= self.client.post("/api/v2/login",
                data=wrong_my_data,
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"Bad Request",
            msg="Login not working properly!")
        self.assertEqual(answ.status_code,400,
            msg="Register not working properly!")

    def test_get_all_users(self):
        #get admin and user tokens
        admin_login = json.dumps({
                "username":"etomovich",
                "password":"etole"
            })
        user_login = json.dumps({
                "username":"omushambulizi",
                "password":"luka"
            })        
        answ= self.client.post("/api/v2/login",
                data=admin_login,
                content_type='application/json')

        output = json.loads(answ.data.decode())
        admin_token = output["Token"]

        answ1= self.client.post("/api/v2/login",
                data=user_login,
                content_type='application/json')
        output = json.loads(answ1.data.decode())
        user_token = output["Token"]

        answ= self.client.get("/api/v2/users",
                headers={'Authorization': admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        print(output)
        self.assertEqual(answ.status_code,200,
            msg="Get users not working properly!")

        answ= self.client.get("/api/v2/users",
                headers={'Authorization': user_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(answ.status_code,401,
            msg="Get users not working properly!")

    def test_get_a_user(self):
        #get admin and user tokens
        admin_login = json.dumps({
                "username":"etomovich",
                "password":"etole"
            })
        user_login = json.dumps({
                "username":"omushambulizi",
                "password":"luka"
            })        
        answ= self.client.post("/api/v2/login",
                data=admin_login,
                content_type='application/json')

        output = json.loads(answ.data.decode())
        admin_token = output["Token"]

        answ1= self.client.post("/api/v2/login",
                data=user_login,
                content_type='application/json')
        output = json.loads(answ1.data.decode())
        user_token = output["Token"]

        user_id = self.user_3_data["User"]["user_id"]

        admin_id = self.user_1_data["User"]["user_id"]

        answ= self.client.get("/api/v2/user/34455556",
                headers={'Authorization': admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"Bad Request",
            msg="Get a user not working properly!")
        self.assertEqual(answ.status_code,400,
            msg="Get a user not working properly!")

        answ= self.client.get("/api/v2/user/"+str(admin_id),
                headers={'Authorization': user_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(answ.status_code,401,
            msg="Get a user not working properly!")

        answ= self.client.get("/api/v2/user/"+str(user_id),
                headers={'Authorization': admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"OK",
            msg="Get a user not working properly!")
        self.assertEqual(answ.status_code,200,
            msg="Get a user not working properly!")

    def test_edit_a_user(self):
        #get admin and user tokens
        admin_login = json.dumps({
                "username":"etomovich",
                "password":"etole"
            })
        user_login = json.dumps({
                "username":"omushambulizi",
                "password":"luka"
            })        
        answ= self.client.post("/api/v2/login",
                data=admin_login,
                content_type='application/json')
        output = json.loads(answ.data.decode())
        admin_token = output["Token"]

        answ1= self.client.post("/api/v2/login",
                data=user_login,
                content_type='application/json')
        output = json.loads(answ1.data.decode())
        user_token = output["Token"]

        user_id = self.user_3_data["User"]["user_id"]
        print(self.user_1_data)
        admin_id = self.user_1_data["User"]["user_id"]

        change=json.dumps({
            "username": "jemmo",
            "email":"jemo@gmail.com",
            "phone_number":"+20000",
            "password":"jim",
            "retype_password":"jim"})


        answ= self.client.put("/api/v2/user/34455556",
                data = change,
                headers={'Authorization': admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"Bad Request",
            msg="Edit a user not working properly!")
        self.assertEqual(answ.status_code,400,
            msg="Edit a user not working properly!")

        answ= self.client.put("/api/v2/user/"+str(admin_id),
                data = change,
                headers={'Authorization': user_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(answ.status_code,401,
            msg="Edit a user not working properly!")

        answ= self.client.put("/api/v2/user/"+str(user_id),
                data = change,
                headers={'Authorization': admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        print(output)
        self.assertEqual(output['Status'],"Success",
            msg="Edit a user not working properly!")
        self.assertEqual(answ.status_code,200,
            msg="Edit a user not working properly!")

    def test_delete_a_user(self):
            #get admin and user tokens
        admin_login = json.dumps({
                "username":"etomovich",
                "password":"etole"
            })
        user_login = json.dumps({
                "username":"omushambulizi",
                "password":"luka"
            })        
        answ= self.client.post("/api/v2/login",
                data=admin_login,
                content_type='application/json')
                
        output = json.loads(answ.data.decode())
        print(output)
        admin_token = output["Token"]

        answ1= self.client.post("/api/v2/login",
                data=user_login,
                content_type='application/json')
        output = json.loads(answ1.data.decode())
        user_token = output["Token"]

        user_id = self.user_3_data["User"]["user_id"]

        admin_id = self.user_1_data["User"]["user_id"]


        answ= self.client.delete("/api/v2/user/34455556",
                headers={'Authorization': admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"Bad Request",
            msg="Get a user not working properly!")
        self.assertEqual(answ.status_code,400,
            msg="Get a user not working properly!")

        answ= self.client.delete("/api/v2/user/"+str(admin_id),
                headers={'Authorization': user_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(answ.status_code,401,
            msg="Get a user not working properly!")

        answ= self.client.delete("/api/v2/user/"+str(user_id),
                headers={'Authorization': admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"Deleted",
            msg="Get a user not working properly!")
        self.assertEqual(answ.status_code,200,
            msg="Get a user not working properly!")