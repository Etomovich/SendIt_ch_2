import unittest
import json
from flask import jsonify
from instance.config import Config, TestConfiguration
from courier_app.send_it_apis.v2.models import (SystemUsers,
    SendItParcels)
from itsdangerous import (TimedJSONWebSignatureSerializer
     as Serializer, BadSignature, SignatureExpired)
from courier_app import create_app
from courier_app.database import remove_all_tables

class ParcelViewCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(
            config_class=TestConfiguration,
            testing=True
        )
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
            
        answ= self.client.post("/api/v2/register",
                data=self.user_3,content_type='application/json')

        self.user_3_data = json.loads(answ.data.decode())

        answ= self.client.post("/api/v2/register",
                data=self.user_1,content_type='application/json')

        self.user_1_data = json.loads(answ.data.decode())

        answ= self.client.post("/api/v2/register",
                data=self.user_2,content_type='application/json')

        self.user_2_data = json.loads(answ.data.decode())

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
        answ= self.client.post("/api/v2/login",
                data=admin_login,
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.admin_token = output["Token"]

        answ= self.client.post("/api/v2/login",
                data=user2_login,
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.user2_token = output["Token"]

        answ1= self.client.post("/api/v2/login",
                data=user_login,
                content_type='application/json')
        output = json.loads(answ1.data.decode())
        self.user_token = output["Token"]

        self.user_id = self.user_3_data["User"]["user_id"]

        self.user2_id = self.user_2_data["User"]["user_id"]

        self.admin_id = self.user_1_data["User"]["user_id"] 

        self.mk_parcel = json.dumps({
            "owner_id":self.user_id,
            "parcel_name":"parcel_name", 
            "weight":"456", 
            "submission_station":"Nairobi", 
            "present_location":"Nakuru"
        })
    
    def tearDown(self):
        toa = remove_all_tables()

    def test_create_parcel(self):
        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.user_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output["message"],
        "This is an Admin Page contact admin for more help!!",
            msg="Get users not working properly!")
        self.assertEqual(answ.status_code,401,
            msg="Get users not working properly!")

        the_parcel = json.dumps({
            "owner_id":self.user_id, 
            "weight":"456",  
            "present_location":"Nakuru"
        })

        answ= self.client.post("/api/v2/parcels",
                data = the_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = answ.data.decode()
        self.assertEqual(answ.status_code,400,
            msg="Creating parcel not working properly!")


        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = answ.data.decode()
        output = json.loads(output)
    
        self.assertEqual(output["message"],"CREATED",
            msg="Create parcel not working properly!")
        self.assertEqual(answ.status_code,201,
            msg="Create parcel not working properly!")

    def test_get_all_parcels(self):
        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        answ= self.client.get("/api/v2/parcels",
                headers={'Authorization': self.admin_token},
                content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"OK",
            msg="Get users not working properly!")
        self.assertEqual(answ.status_code,200,
            msg="Get users not working properly!")

        answ= self.client.get("/api/v2/parcels",
                headers={'Authorization': self.user_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        print(output)
        self.assertEqual(output["message"],
            "This is an Admin Page contact admin for more help!!",
            msg="Get users not working properly!")
        self.assertEqual(answ.status_code,401,
            msg="Get users not working properly!")

        answ= self.client.get("/api/v2/parcels",
                headers={'Authorization': '98765432'},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(answ.status_code,401,
            msg="Get users not working properly!")

    def test_get_a_parcel(self):
        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.parcel_id = output["parcel_id"]

        answ= self.client.get("/api/v2/parcels/"+str(self.parcel_id),
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"OK",
            msg="Get a parcel not working properly!")
        self.assertEqual(answ.status_code,200,
            msg="Get a parcel not working properly!")

        answ= self.client.get("/api/v2/parcels/"+str(self.parcel_id),
                headers={'Authorization': self.user2_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        print(output)
        self.assertEqual(output["message"],
            "UNAUTHORIZED",
            msg="Get a parcel not working properly!")
        self.assertEqual(answ.status_code,401,
            msg="Get a parcel not working properly!")

        answ= self.client.get("/api/v2/parcels/"+str(self.parcel_id),
                headers={'Authorization': '3455666'},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        
        self.assertEqual(output["message"],
            "You are not authorized to view this page!!",
            msg="Get a parcel not working properly!")
        self.assertEqual(answ.status_code,401,
            msg="Get a parcel not working properly!")

        answ= self.client.get("/api/v2/parcels/5435345",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(answ.status_code,400,
            msg="Get a parcel not working properly!")

    def test_edit_a_parcel(self):
        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.parcel_id = output["parcel_id"]

        this_data =json.dumps({
                "weight": "4567",
                "destination": "destination",
                "expected_pay":"2345",
                "submission_station":"submission_station",
                "feedback": "feedback",
                "present_location": "present_location",
                "status": "in_transit",
                "approved": "approved"
        })

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id),
                data= this_data,
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        print(output)
        self.assertEqual(output['message'],'EDITED',
            msg="Edit a parcel not working properly!")
        self.assertEqual(answ.status_code,200,
            msg="Edit a parcel not working properly!")

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id),
                data= this_data,
                headers={'Authorization': self.user2_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        print(output)
        self.assertEqual(output["message"],
            "This is an Admin Page contact admin for more help!!",
            msg="Edit a parcel not working properly!")
        self.assertEqual(answ.status_code,401,
            msg="Edit a parcel not working properly!")

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id),
                data= this_data,
                headers={'Authorization': self.user_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output["message"],
            "This is an Admin Page contact admin for more help!!",
            msg="Get a parcel not working properly!")
        self.assertEqual(answ.status_code,401,
            msg="Get a parcel not working properly!")

        answ= self.client.get("/api/v2/parcels/5435345",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(answ.status_code,400,
            msg="Get a parcel not working properly!")

    def test_delete_a_parcel(self):
        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.parcel_id = output["parcel_id"]

        answ= self.client.delete("/api/v2/parcels/"+str(self.parcel_id),
                headers={'Authorization': self.user_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        
        self.assertEqual(output["message"],
            "This is an Admin Page contact admin for more help!!",
            msg="Delete a parcel not working properly!")
        self.assertEqual(answ.status_code,401,
            msg="Delete a parcel not working properly!")

        answ= self.client.delete("/api/v2/parcels/"+str(self.parcel_id),
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        print(output)
        self.assertEqual(output['message'],"deleted",
            msg="Delete a parcel not working properly!")
        self.assertEqual(answ.status_code,200,
            msg="Delete a parcel not working properly!")

        answ= self.client.delete("/api/v2/parcels/"+str(self.parcel_id),
                headers={'Authorization': '3455666'},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        
        self.assertEqual(output["message"],
            "You are not authorized to view this page!!",
            msg="Delete a parcel not working properly!")
        self.assertEqual(answ.status_code,401,
            msg="Delete a parcel not working properly!")

        answ= self.client.delete("/api/v2/parcels/5435345",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(answ.status_code,400,
            msg="Delete a parcel not working properly!")

    def test_cancel_a_parcel(self):
        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.parcel_id = output["parcel_id"]

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id)+
                "/cancel",
                headers={'Authorization': self.user_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['message'],"cancelled",
            msg="Delete a parcel not working properly!")
        self.assertEqual(answ.status_code,200,
            msg="Delete a parcel not working properly!")

        answ= self.client.delete("/api/v2/parcels/"+str(self.parcel_id),
                headers={'Authorization': '3455666'},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        
        self.assertEqual(output["message"],
            "You are not authorized to view this page!!",
            msg="Delete a parcel not working properly!")
        self.assertEqual(answ.status_code,401,
            msg="Delete a parcel not working properly!")

        answ= self.client.delete("/api/v2/parcels/5435345",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(answ.status_code,400,
            msg="Delete a parcel not working properly!")