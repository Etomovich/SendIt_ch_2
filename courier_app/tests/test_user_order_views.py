import unittest
import json
from datetime import datetime
from flask import jsonify
from instance.config import Config
from courier_app.send_it_apis.v1.models import (SystemUsers,
    SendItParcels, SendItUserOrders)
from itsdangerous import (TimedJSONWebSignatureSerializer
     as Serializer, BadSignature, SignatureExpired)
from courier_app import create_app

class OrdersViewCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.user_1=json.dumps(
            {"username":"etomovich",
            "email":"etomovich@gmail.com",
            "phone_number":"078",
            "password":"etole",
            "role":"Admin",
            "retype_password":"etole"})
        
        self.user_2=json.dumps(
            {"username":"anthony",
            "email":"antony@gmail.com",
            "phone_number":"+26777",
            "password":"kimani",
            "role":"User",
            "retype_password":"kimani"})

        self.user_3=json.dumps(
            {"username":"omushambulizi",
            "email":"lukaku@gmail.com",
            "phone_number":"+25434526777",
            "password":"luka",
            "role":"User",
            "retype_password":"luka"})

        answ= self.client.post("/api/v1/register",
            data=self.user_3,content_type='application/json')

        answ= self.client.post("/api/v1/register",
            data=self.user_2,content_type='application/json')

        answ= self.client.post("/api/v1/register",
            data=self.user_1,content_type='application/json')

        #get admin and user tokens
        admin_login = json.dumps({
                "username":"etomovich",
                "password":"etole"
            })
        user_login = json.dumps({
                "username":"omushambulizi",
                "password":"luka"
            })

        user2_login = json.dumps({
                "username":"anthony",
                "password":"kimani"
            })        
        answ= self.client.post("/api/v1/login",
                data=admin_login,
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.admin_token = output["Token"]

        answ= self.client.post("/api/v1/login",
                data=user2_login,
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.user2_token = output["Token"]

        answ1= self.client.post("/api/v1/login",
                data=user_login,
                content_type='application/json')
        output = json.loads(answ1.data.decode())
        self.user_token = output["Token"]

        self.user_id = ""
        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['username'] \
            == "omushambulizi":
                self.user_id = item

        self.user2_id = ""
        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['username'] \
            == "anthony":
                self.user2_id = item

        self.admin_id = ""
        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['username'] \
            == "etomovich":
                self.admin_id = item

        payload = {
                "owner_id": self.user_1,
                "expected_pay": "",
                "order_id": "",
                "submission_station": "submission_station",
                "present_location":"present_location",
                "weight": 45.90,
                "feedback": "",
                "destination": "",
                "submission_date": "4/5/2018",
                "status": "not_started",
                "approved":"No"
            }
        SendItParcels.sendit_parcels['12345'] = payload
        self.mk_order = json.dumps({
            "parcel_id":"12345",
            "parcel_description":"parcel_description",
            "pay_mode":"pay_mode",
            "pay_proof":"pay_proof",
            "amount_paid":"45.78",
            "destination":"destination",
        })

    def test_create_order(self):
        answ= self.client.post("/api/v1/orders",
                data = self.mk_order,
                headers={'Authorization': self.user_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output["Status"],"OK",
            msg="Create parcel not working properly!")
        self.assertEqual(answ.status_code,201,
            msg="Create parcel not working properly!")

        bad_order = json.dumps({
            "parcel_description":"parcel_description",
            "pay_mode":"pay_mode",
            "pay_proof":"pay_proof",
            "amount_paid":"45.78",
            "destination":"destination",
        })
        
        answ= self.client.post("/api/v1/orders",
                data = bad_order,
                headers={'Authorization': self.user_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(answ.status_code,400,
            msg="Create order not working properly!")

        answ= self.client.post("/api/v1/orders",
                data = self.mk_order,
                headers={'Authorization': "45566"},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output
            ,"You are not authorized to view this page!!",
            msg="Create order not working properly!")
        self.assertEqual(answ.status_code,401,
            msg="Create order not working properly!")
        #

    def test_get_all_orders(self):
        answ= self.client.post("/api/v1/orders",
                data = self.mk_order,
                headers={'Authorization': self.user_token},
                content_type='application/json')

        answ= self.client.get("/api/v1/orders",
                headers={'Authorization': self.admin_token},
                content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"OK",
            msg="Get users not working properly!")
        self.assertEqual(answ.status_code,200,
            msg="Get users not working properly!")

        answ= self.client.get("/api/v1/orders",
                headers={'Authorization': self.user_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        print(output)
        self.assertEqual(output,
            "This is an Admin Page contact admin for more help!!",
            msg="Get users not working properly!")
        self.assertEqual(answ.status_code,401,
            msg="Get users not working properly!")

        answ= self.client.get("/api/v1/orders",
                headers={'Authorization': '98765432'},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(answ.status_code,401,
            msg="Get users not working properly!")

    
