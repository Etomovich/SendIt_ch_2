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

        answ= self.client.put("/api/v2/parcels/"+str(23)+
                "/cancel",
                headers={'Authorization': self.user_token},
                content_type='application/json')

        self.assertEqual(answ.status_code,400,
            msg="Cancel a parcel not working properly!")

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id)+
                "/cancel",
                headers={'Authorization': self.user_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['message'],"cancelled",
            msg="Cancel a parcel not working properly!")
        self.assertEqual(answ.status_code,200,
            msg="Cancel a parcel not working properly!")

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

    def test_destination_changer(self):
        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.parcel_id = output["parcel_id"]

        self.assertEqual(output['destination'],"",
            msg="Adding a parcel should have empty string destination by default.")

        new_destination=json.dumps({
            "destination": "Mombasa"
        })
        destination_not_string =json.dumps({
            "destination": 30
        })

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id)+"/destination",
                data = new_destination,
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['message'],"UNAUTHORIZED",
            msg="Destination changer not working properly!!")

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id)+"/destination",
                data = new_destination,
                headers={'Authorization': self.user_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        print(answ.status_code)
        self.assertEqual(output['message'],"Destination Changed",
            msg="Destination changer not working properly!!")

        self.assertEqual(output['destination'],"Mombasa",
            msg="Adding a parcel should have empty destination by default.")

        self.assertEqual(answ.status_code,200,
            msg="Destination changer not working properly!!")

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id)+"/destination",
                data = destination_not_string,
                headers={'Authorization': self.user_token},
                content_type='application/json')

        self.assertEqual(answ.status_code,400,
            msg="Destination changer not working properly!!")

    def test_status_changer(self):
        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.parcel_id = output["parcel_id"]

        self.assertEqual(output["status"],"not_started",
            msg="The status of a parcel should be by default 'not_started'!!")

        new_status =json.dumps({
            "status": "in_transit"
        })
        wrong_status=json.dumps({
            "status": "my_status"
        })

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id)+"/status",
                data = new_status,
                headers={'Authorization': self.user_token},
                content_type='application/json')

        self.assertEqual(answ.status_code,401,
            msg="Status changer not working properly!!")

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id)+"/status",
                data = new_status,
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['message'],"EDITED",
            msg="Status changer not working properly!!")

        self.assertEqual(output['Status'],"OK",
            msg="Status changer not working correctly!!")

        self.assertEqual(answ.status_code,200,
            msg="Destination changer not working properly!!")

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id)+"/status",
                data = wrong_status,
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        self.assertEqual(answ.status_code,400,
            msg="Status changer not working properly!!")

    def test_location_changer(self):
        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.parcel_id = output["parcel_id"]

        self.assertEqual(output["present_location"],"Nakuru",
            msg="The status of a parcel should be by default 'not_started'!!")

        new_location =json.dumps({
            "present_location": "Kisumu"
        })
        wrong_location=json.dumps({
            "present_location": 50
        })

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id)+"/presentLocation",
                data = new_location,
                headers={'Authorization': self.user_token},
                content_type='application/json')

        self.assertEqual(answ.status_code,401,
            msg="present location changer not working properly!!")

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id)+"/presentLocation",
                data = new_location,
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        print(answ.status_code)
        self.assertEqual(output['message'],"EDITED",
            msg="present location  changer not working properly!!")

        self.assertEqual(output['Status'],"OK",
            msg="present location  changer not working correctly!!")

        self.assertEqual(answ.status_code,200,
            msg="present location changer not working properly!!")

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id)+"/presentLocation",
                data = wrong_location,
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        self.assertEqual(answ.status_code,400,
            msg="present location changer not working properly!!")

    def test_delivered_parcels(self):
        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.parcel_id = output["parcel_id"]

        self.assertEqual(output["owner_id"],self.user_id,
            msg="Error in making parcel [owner_id]!!")

        new_status =json.dumps({
            "status": "delivered"
        })

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id)+"/status",
                data = new_status,
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())

        self.assertEqual(output['Status'],"OK",
            msg="Status changer not working correctly!!")

        self.assertEqual(answ.status_code,200,
            msg="Status changer not working properly!!")

        answ= self.client.get("/api/v2/parcels/"+str(23)+
                "/delivered",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        self.assertEqual(answ.status_code,400,
            msg="Get parcel delivery by user id not working properly!")

        answ= self.client.get("/api/v2/parcels/"+str(23)+
                "/delivered",
                headers={'Authorization': '45566'},
                content_type='application/json')

        self.assertEqual(answ.status_code,401,
            msg="Get parcel delivery by user id not working properly!")
        
        answ= self.client.get("/api/v2/parcels/"+str(self.user_id)+"/delivered",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"OK",
            msg="Get delivered parcels not working correctly!!")

        self.assertEqual(answ.status_code,200,
            msg="Get delivered parcels not working properly!!")

    def test_cancelled_parcels(self):
        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.parcel_id = output["parcel_id"]

        self.assertEqual(output["owner_id"],self.user_id,
            msg="Error in making parcel [owner_id]!!")

        new_status =json.dumps({
            "status": "cancelled"
        })

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id)+"/status",
                data = new_status,
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())

        self.assertEqual(output['Status'],"OK",
            msg="Status changer not working correctly!!")

        self.assertEqual(answ.status_code,200,
            msg="Status changer not working properly!!")

        answ= self.client.get("/api/v2/parcels/"+str(23)+
                "/cancelled",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        self.assertEqual(answ.status_code,400,
            msg="Get cancelled parcels not working properly!")

        answ= self.client.get("/api/v2/parcels/"+str(23)+
                "/cancelled",
                headers={'Authorization': '45566'},
                content_type='application/json')

        self.assertEqual(answ.status_code,401,
            msg="Get cancelled parcels not working properly!")
        
        answ= self.client.get("/api/v2/parcels/"+str(self.user_id)+"/cancelled",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"OK",
            msg="Get cancelled parcels not working properly!")

        self.assertEqual(answ.status_code,200,
            msg="Get cancelled parcels not working properly!")

    def test_intransit_parcels(self):
        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.parcel_id = output["parcel_id"]

        self.assertEqual(output["owner_id"],self.user_id,
            msg="Error in making parcel [owner_id]!!")

        new_status =json.dumps({
            "status": "in_transit"
        })

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id)+"/status",
                data = new_status,
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())

        self.assertEqual(output['Status'],"OK",
            msg="Status changer not working correctly!!")

        self.assertEqual(answ.status_code,200,
            msg="Status changer not working properly!!")

        answ= self.client.get("/api/v2/parcels/"+str(23)+
                "/in-transit",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        self.assertEqual(answ.status_code,400,
            msg="Get in_transit parcels not working properly!")

        answ= self.client.get("/api/v2/parcels/"+str(23)+
                "/in-transit",
                headers={'Authorization': '45566'},
                content_type='application/json')

        self.assertEqual(answ.status_code,401,
            msg="Get in_transit parcels not working properly!")
        
        answ= self.client.get("/api/v2/parcels/"+str(self.user_id)+"/in-transit",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"OK",
            msg="Get in_transit parcels not working properly!")

        self.assertEqual(answ.status_code,200,
            msg="Get in_transit parcels not working properly!")

    def test_notstarted_parcels(self):
        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.parcel_id = output["parcel_id"]

        self.assertEqual(output["owner_id"],self.user_id,
            msg="Error in making parcel [owner_id]!!")

        new_status =json.dumps({
            "status": "not_started"
        })

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id)+"/status",
                data = new_status,
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())

        self.assertEqual(output['Status'],"OK",
            msg="Status changer not working correctly!!")

        self.assertEqual(answ.status_code,200,
            msg="Status changer not working properly!!")

        answ= self.client.get("/api/v2/parcels/"+str(23)+
                "/not-started",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        self.assertEqual(answ.status_code,400,
            msg="Get not-started parcels not working properly!")

        answ= self.client.get("/api/v2/parcels/"+str(23)+
                "/not-started",
                headers={'Authorization': '45566'},
                content_type='application/json')

        self.assertEqual(answ.status_code,401,
            msg="Get not-started parcels not working properly!")
        
        answ= self.client.get("/api/v2/parcels/"+str(self.user_id)+"/not-started",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"OK",
            msg="Get not-started parcels not working properly!")

        self.assertEqual(answ.status_code,200,
            msg="Get not-started parcels not working properly!") 

    def test_get_approved_parcels(self):
        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.parcel_id = output["parcel_id"]

        self.assertEqual(output["owner_id"],self.user_id,
            msg="Error in making parcel [owner_id]!!")

        approve_parcel =json.dumps({
            "approved": "approved"
        })

        answ= self.client.put("/api/v2/parcels/"+str(self.parcel_id),
                data = approve_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())

        self.assertEqual(output['message'],"EDITED",
            msg="Parcel editor not working correctly!!")

        self.assertEqual(answ.status_code,200,
            msg="Parcel editor not working properly!!")

        answ= self.client.get("/api/v2/parcels/"+str(23)+
                "/approved",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        self.assertEqual(answ.status_code,400,
            msg="Get approved parcels not working properly!")

        answ= self.client.get("/api/v2/parcels/"+str(23)+
                "/approved",
                headers={'Authorization': '45566'},
                content_type='application/json')

        self.assertEqual(answ.status_code,401,
            msg="Get approved parcels not working properly!")
        
        answ= self.client.get("/api/v2/parcels/"+str(self.user_id)+"/approved",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"OK",
            msg="Get approved parcels not working properly!")

        self.assertEqual(answ.status_code,200,
            msg="Get approved parcels not working properly!")
    
    def test_get_user_parcels_by_id(self):
        answ= self.client.post("/api/v2/parcels",
                data = self.mk_parcel,
                headers={'Authorization': self.admin_token},
                content_type='application/json')
        
        output = json.loads(answ.data.decode())
        self.parcel_id = output["parcel_id"]

        self.assertEqual(output["owner_id"],self.user_id,
            msg="Error in making parcel [owner_id]!!")


        answ= self.client.get("/api/v2/users/"+str(23)+
                "/parcels",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        self.assertEqual(answ.status_code,400,
            msg="Get a user's parcels not working properly!")

        answ= self.client.get("/api/v2/users/"+str(23)+
                "/parcels",
                headers={'Authorization': '45566'},
                content_type='application/json')

        self.assertEqual(answ.status_code,401,
            msg="Get a user's parcels not working properly!")
        
        answ= self.client.get("/api/v2/users/"+str(self.user_id)+"/parcels",
                headers={'Authorization': self.admin_token},
                content_type='application/json')

        output = json.loads(answ.data.decode())
        self.assertEqual(output['Status'],"OK",
            msg="Get a user's parcels not working properly!")

        self.assertEqual(answ.status_code,200,
            msg="Get a user's parcels not working properly!")