import unittest
from instance.config import Config
from courier_app.send_it_apis.v1.models import (SystemUsers,
    SendItParcels, SendItUserOrders)

class ParcelModelCase(unittest.TestCase):
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

        admin_ob = SendItParcels(self.etomovich_id)
        user_ob = SendItParcels(self.pogie_id)
        false_user = SendItParcels(00000)

    def test_user_is_there(self):
        admin_ob = SendItParcels(self.etomovich_id)
        user_ob = SendItParcels(self.pogie_id)
        false_user = SendItParcels(00000)

        reply = false_user._user_is_there()
        self.assertFalse(reply,
            msg="User does not exist, expects False")

        reply = user_ob._user_is_there()
        self.assertTrue(reply,
            msg="User exist, expects True")

    def tearDown(self):
        SystemUsers.send_it_users = {}
        SendItParcels.sendit_parcels ={}
        SendItUserOrders.sendit_user_orders ={}
        
    def test_add_false_parcels(self):
        admin_ob = SendItParcels(self.etomovich_id)
        user_ob = SendItParcels(self.pogie_id)
        false_user = SendItParcels(00000) 

        reply = user_ob.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")
        
        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="Add parcels function not working")

    def test_add_parcels(self):
        admin_ob = SendItParcels(self.etomovich_id)
        user_ob = SendItParcels(self.pogie_id)
        false_user = SendItParcels(00000)

        reply = admin_ob.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")
        
        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

    def test_edit_parcel(self):
        admin_ob = SendItParcels(self.etomovich_id)
        user_ob = SendItParcels(self.pogie_id)
        false_user = SendItParcels(00000)

        reply = admin_ob.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item


        reply = user_ob.edit_parcel(parcel_id,
            feedback = "Yesu ni Bwana!")

        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="Add parcels function not working")

        reply = admin_ob.edit_parcel(parcel_id,
            weight= "34",
            destination="Kisumu",
            expected_pay="1200",
            submission_station="Malindi",
            feedback = "Yesu ni Bwana!",
            order_id="56788765",
            owner_id= self.pogie_id,
            present_location="Nakuru",
            status="in_transit",
            approved = "Yes")

        self.assertEqual(reply["message"],"EDITED",
            msg="Add parcels function not working")

    def test_cancel_parcel_delivery(self):
        admin_ob = SendItParcels(self.etomovich_id)
        user_ob = SendItParcels(self.pogie_id)
        false_user = SendItParcels(00000)

        reply = admin_ob.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        reply = admin_ob.user_cancels_delivery(parcel_id)
        
        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="User cancel delivery function not working")

        reply = user_ob.user_cancels_delivery(parcel_id)
        self.assertEqual(reply["message"],"cancelled",
            msg="User cancel delivery function not working")

    def test_get_all_parcels(self):
        admin_ob = SendItParcels(self.etomovich_id)
        user_ob = SendItParcels(self.pogie_id)
        false_user = SendItParcels(00000)

        reply = admin_ob.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        reply = admin_ob.get_all_parcels()

        self.assertTrue(isinstance(reply, list),
            msg="Check Get All Parcels function works")

        reply = user_ob.get_all_parcels()

        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="Check Get All Parcels function works")

    def test_delete_parcels(self):
        admin_ob = SendItParcels(self.etomovich_id)
        user_ob = SendItParcels(self.pogie_id)
        false_user = SendItParcels(00000)

        reply = admin_ob.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        reply = user_ob.delete_parcel(parcel_id)

        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="Check delete Parcels function works")

        reply = admin_ob.delete_parcel(parcel_id)

        self.assertEqual(reply["message"],"deleted",
            msg="Check delete Parcels function works")

    def test_get_a_parcel(self):
        admin_ob = SendItParcels(self.etomovich_id)
        user_ob = SendItParcels(self.pogie_id)
        false_user = SendItParcels(00000)

        reply = admin_ob.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        reply = user_ob.get_parcel(parcel_id)

        self.assertTrue(isinstance(reply, dict),
            msg="Fetching a parcel function not working")

        reply = false_user.get_parcel(parcel_id)

        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="Fetching a parcel function not working")

    def test_get_all_my_parcels(self):
        admin_ob = SendItParcels(self.etomovich_id)
        user_ob = SendItParcels(self.pogie_id)
        false_user = SendItParcels(00000)

        reply = admin_ob.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        reply = user_ob.get_all_my_parcels(self.pogie_id)

        self.assertTrue(isinstance(reply, list),
            msg="Fetching a parcel function not working")

        reply = admin_ob.get_all_my_parcels(self.pogie_id)

        self.assertTrue(isinstance(reply, list),
            msg="Fetching a parcel function not working")

        reply = false_user.get_all_my_parcels(self.pogie_id)

        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="Fetching a parcel function not working")        
    
    def test_get_my_approved_parcels(self):
        admin_ob = SendItParcels(self.etomovich_id)
        user_ob = SendItParcels(self.pogie_id)
        false_user = SendItParcels(00000)

        reply = admin_ob.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        reply = user_ob.get_my_approved_parcels(self.pogie_id)

        self.assertTrue(isinstance(reply, list),
            msg="Fetching a parcel function not working")

        reply = admin_ob.get_my_approved_parcels(self.pogie_id)

        self.assertTrue(isinstance(reply, list),
            msg="Fetching a parcel function not working")

        reply = false_user.get_my_approved_parcels(self.pogie_id)

        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="Fetching a parcel function not working")

    def test_get_my_notstarted_parcels(self):
        admin_ob = SendItParcels(self.etomovich_id)
        user_ob = SendItParcels(self.pogie_id)
        false_user = SendItParcels(00000)

        reply = admin_ob.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        reply = user_ob.get_my_notstarted_parcels(self.pogie_id)

        self.assertTrue(isinstance(reply, list),
            msg="Fetching a parcel function not working")

        reply = admin_ob.get_my_notstarted_parcels(self.pogie_id)

        self.assertTrue(isinstance(reply, list),
            msg="Fetching a parcel function not working")

        reply = false_user.get_my_notstarted_parcels(self.pogie_id)

        self.assertEqual(reply["message"],"UNKNOWN USER",
            msg="Fetching a parcel function not working")

    def test_get_my_intransit_parcels(self):
        admin_ob = SendItParcels(self.etomovich_id)
        user_ob = SendItParcels(self.pogie_id)
        false_user = SendItParcels(00000)

        reply = admin_ob.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        reply = user_ob.get_my_intransit_parcels(self.pogie_id)

        self.assertTrue(isinstance(reply, list),
            msg="Fetching a parcel function not working")

        reply = admin_ob.get_my_intransit_parcels(self.pogie_id)

        self.assertTrue(isinstance(reply, list),
            msg="Fetching a parcel function not working")

        reply = false_user.get_my_intransit_parcels(self.pogie_id)
        self.assertEqual(reply["message"],"UNKNOWN USER",
            msg="Fetching a parcel function not working")

    def test_get_my_cancelled_parcels(self):
        admin_ob = SendItParcels(self.etomovich_id)
        user_ob = SendItParcels(self.pogie_id)
        false_user = SendItParcels(00000)

        reply = admin_ob.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"], "CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        reply = user_ob.get_my_cancelled_parcels(self.pogie_id)

        self.assertTrue(isinstance(reply, list),
            msg="Fetching a parcel function not working")

        reply = admin_ob.get_my_cancelled_parcels(self.pogie_id)

        self.assertTrue(isinstance(reply, list),
            msg="Fetching a parcel function not working")

        reply = false_user.get_my_cancelled_parcels(self.pogie_id)

        self.assertEqual(reply["message"],"UNKNOWN USER",
            msg="Fetching a parcel function not working")

    def test_get_my_delivered_parcels(self):
        admin_ob = SendItParcels(self.etomovich_id)
        user_ob = SendItParcels(self.pogie_id)
        false_user = SendItParcels(00000)

        reply = admin_ob.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        reply = user_ob.get_my_delivered_parcels(self.pogie_id)

        self.assertTrue(isinstance(reply, list),
            msg="Fetching a parcel function not working")

        reply = admin_ob.get_my_delivered_parcels(self.pogie_id)

        self.assertTrue(isinstance(reply, list),
            msg="Fetching a parcel function not working")

        reply = false_user.get_my_delivered_parcels(self.pogie_id)

        self.assertEqual(reply["message"],"UNKNOWN USER",
            msg="Fetching a parcel function not working")
   

