import unittest
from instance.config import Config
from courier_app.send_it_apis.v1.models import (SystemUsers,
    SendItParcels, SendItUserOrders)

class ParcelOrdersModelCase(unittest.TestCase):
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
        
    def test_user_is_there(self):
        admin_ob = SendItUserOrders(self.etomovich_id)
        user_ob = SendItUserOrders(self.pogie_id)
        false_user = SendItUserOrders(00000)

        reply = false_user._user_is_there()
        self.assertFalse(reply,
            msg="User does not exist, expects False")

        reply = user_ob._user_is_there()
        self.assertTrue(reply,
            msg="User exist, expects True")

    def test_add_order(self):
        admin_ob = SendItUserOrders(self.etomovich_id)
        user_ob = SendItUserOrders(self.pogie_id)
        false_user = SendItUserOrders(00000)

        admin_parc = SendItParcels(self.etomovich_id)

        reply = admin_parc.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add order function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item


        reply = false_user.add_order(parcel_id)

        self.assertEqual(reply["message"],"UNKNOWN USER",
            msg="Add order function not working")

        reply = user_ob.add_order(parcel_id)

        self.assertTrue(isinstance(reply, dict),
            msg="Add parcels function not working")

    def test_edit_order(self):
        admin_ob = SendItUserOrders(self.etomovich_id)
        user_ob = SendItUserOrders(self.pogie_id)
        false_user = SendItUserOrders(00000)

        admin_parc = SendItParcels(self.etomovich_id)

        reply = admin_parc.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        #Create an order
        reply = user_ob.add_order(parcel_id)

        self.assertTrue(isinstance(reply, dict),
            msg="Add order function not working")

        pog_order_list=SendItUserOrders.sendit_user_orders\
            [self.pogie_id]

        order_item = ""
        for thing in pog_order_list:
            if thing["parcel_id"] == parcel_id:
                order_item = thing
        
        reply = user_ob.edit_order_user(order_id = order_item["order_id"],
            parcel_id= parcel_id,
            parcel_description="parcel_description",
            pay_mode="pay_mode",
            pay_proof="pay_proof",
            destination="destination",
            submitted="submitted")

        self.assertTrue(("fields[parcel_description" in reply["message"]),
            msg="Add parcels function not working")
            
        reply = user_ob.edit_order_user(order_id = order_item["order_id"],
            parcel_id= parcel_id,
            parcel_description="parcel_description",
            pay_mode="pay_mode",
            pay_proof="pay_proof",
            amount_paid = "456",
            destination="destination",
            submitted="submitted")

        self.assertEqual(reply["message"],"EDITED",
            msg="Add parcels function not working")

        reply = user_ob.edit_order_user(order_id = "1234",
            parcel_id= parcel_id,
            parcel_description="parcel_description",
            pay_mode="pay_mode",
            pay_proof="pay_proof",
            amount_paid = "456",
            destination="destination",
            submitted="submitted")

        self.assertEqual(reply["message"],"ORDER NOT FOUND",
            msg="Add parcels function not working")

        reply = false_user.edit_order_user(order_id = "1234",
            parcel_id= parcel_id,
            parcel_description="parcel_description",
            pay_mode="pay_mode",
            pay_proof="pay_proof",
            amount_paid = "456",
            destination="destination",
            submitted="submitted")

        self.assertEqual(reply["message"],"UNKNOWN USER",
            msg="Add parcels function not working")
    
    def test_process_order(self):
        admin_ob = SendItUserOrders(self.etomovich_id)
        user_ob = SendItUserOrders(self.pogie_id)
        false_user = SendItUserOrders(00000)

        admin_parc = SendItParcels(self.etomovich_id)

        reply = admin_parc.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        #Create an order
        reply = user_ob.add_order(parcel_id)

        self.assertTrue(isinstance(reply, dict),
            msg="Add order function not working")

        pog_order_list=SendItUserOrders.sendit_user_orders\
            [self.pogie_id]

        order_item = ""
        for thing in pog_order_list:
            if thing["parcel_id"] == parcel_id:
                order_item = thing

        reply = user_ob.process_order(
            order_id = order_item["order_id"],
            order_status = "accepted",
            feedback = "Will begin transit soon")

        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="Add parcels function not working")

        reply = admin_ob.process_order(
            order_id = order_item["order_id"],
            order_status = "accepted",
            feedback = "Will begin transit soon")

        self.assertEqual(reply["message"],"PROCESSED",
            msg="Add parcels function not working")

    def test_remove_submission(self):
        admin_ob = SendItUserOrders(self.etomovich_id)
        user_ob = SendItUserOrders(self.pogie_id)
        false_user = SendItUserOrders(00000)

        admin_parc = SendItParcels(self.etomovich_id)

        reply = admin_parc.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        #Create an order
        reply = user_ob.add_order(parcel_id)

        self.assertTrue(isinstance(reply, dict),
            msg="Add order function not working")

        pog_order_list=SendItUserOrders.sendit_user_orders\
            [self.pogie_id]

        order_item = ""
        for thing in pog_order_list:
            if thing["parcel_id"] == parcel_id:
                order_item = thing

        reply = false_user.remove_submission(
            order_id=order_item["order_id"])

        self.assertEqual(reply["message"],"UNKNOWN USER",
            msg="Remove submission function not working")
        
        reply = user_ob.remove_submission(
            order_id=order_item["order_id"])

        self.assertEqual(reply["message"],"Submission Removed",
            msg="Remove submission function not working")

        reply = user_ob.remove_submission(
            order_id="1234")

        self.assertEqual(reply["message"],"ORDER NOT FOUND",
            msg="Remove submission function not working")

    def test_return_all_orders(self):
        admin_ob = SendItUserOrders(self.etomovich_id)
        user_ob = SendItUserOrders(self.pogie_id)
        false_user = SendItUserOrders(00000)

        admin_parc = SendItParcels(self.etomovich_id)

        reply = admin_parc.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        #Create an order
        reply = user_ob.add_order(parcel_id)

        self.assertTrue(isinstance(reply, dict),
            msg="Add order function not working")

        pog_order_list=SendItUserOrders.sendit_user_orders\
            [self.pogie_id]

        order_item = ""
        for thing in pog_order_list:
            if thing["parcel_id"] == parcel_id:
                order_item = thing

        reply = user_ob.return_all_orders()

        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="Return all orders function not working")

        reply = admin_ob.return_all_orders()

        self.assertTrue(isinstance(reply, list),
            msg="Return all orders function not working")

    def test_return_unprocessed_orders(self):
        admin_ob = SendItUserOrders(self.etomovich_id)
        user_ob = SendItUserOrders(self.pogie_id)
        false_user = SendItUserOrders(00000)

        admin_parc = SendItParcels(self.etomovich_id)

        reply = admin_parc.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        #Create an order
        reply = user_ob.add_order(parcel_id)

        self.assertTrue(isinstance(reply, dict),
            msg="Add order function not working")

        pog_order_list=SendItUserOrders.sendit_user_orders\
            [self.pogie_id]

        order_item = ""
        for thing in pog_order_list:
            if thing["parcel_id"] == parcel_id:
                order_item = thing

        reply = user_ob.return_all_unprocessed_orders()

        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="Return all orders function not working")

        reply = admin_ob.return_all_unprocessed_orders()

        self.assertTrue(isinstance(reply, list),
            msg="Return all orders function not working")
        
    def test_return_an_order(self):
        admin_ob = SendItUserOrders(self.etomovich_id)
        user_ob = SendItUserOrders(self.pogie_id)
        false_user = SendItUserOrders(00000)

        admin_parc = SendItParcels(self.etomovich_id)

        reply = admin_parc.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        #Create an order
        reply = user_ob.add_order(parcel_id)

        self.assertTrue(isinstance(reply, dict),
            msg="Add order function not working")

        pog_order_list=SendItUserOrders.sendit_user_orders\
            [self.pogie_id]

        order_item = ""
        for thing in pog_order_list:
            if thing["parcel_id"] == parcel_id:
                order_item = thing

        reply = user_ob.return_an_order(order_item['order_id'])

        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="Return an order function not working")

        reply = admin_ob.return_an_order(order_item['order_id'])

        self.assertTrue(isinstance(reply, dict),
            msg="Return all orders function not working")

        reply = admin_ob.return_an_order("457777")

        self.assertEqual(reply["message"],"ORDER NOT FOUND",
            msg="Return all orders function not working")
        
    def test_return_my_order(self):
        admin_ob = SendItUserOrders(self.etomovich_id)
        user_ob = SendItUserOrders(self.pogie_id)
        false_user = SendItUserOrders(00000)

        admin_parc = SendItParcels(self.etomovich_id)

        reply = admin_parc.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        #Create an order
        reply = user_ob.add_order(parcel_id)

        self.assertTrue(isinstance(reply, dict),
            msg="Add order function not working")

        pog_order_list=SendItUserOrders.sendit_user_orders\
            [self.pogie_id]

        order_item = ""
        for thing in pog_order_list:
            if thing["parcel_id"] == parcel_id:
                order_item = thing

        reply = false_user.return_my_order(order_item['order_id'])

        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="Return my order function not working")

        reply = user_ob.return_my_order('56467')

        self.assertEqual(reply["message"],"ORDER NOT FOUND",
            msg="Return my order function not working")

        reply = user_ob.return_my_order(order_item['order_id'])

        self.assertTrue(isinstance(reply, dict),
            msg="Return my order function not working")

    def test_my_processed_orders(self):
        admin_ob = SendItUserOrders(self.etomovich_id)
        user_ob = SendItUserOrders(self.pogie_id)
        false_user = SendItUserOrders(00000)

        admin_parc = SendItParcels(self.etomovich_id)

        reply = admin_parc.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        #Create an order
        reply = user_ob.add_order(parcel_id)

        self.assertTrue(isinstance(reply, dict),
            msg="Add order function not working")

        pog_order_list=SendItUserOrders.sendit_user_orders\
            [self.pogie_id]

        order_item = ""
        for thing in pog_order_list:
            if thing["parcel_id"] == parcel_id:
                order_item = thing

        reply = false_user.my_processed_orders(self.pogie_id)

        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="my_processed_orders function not working")

        reply = admin_ob.my_processed_orders(self.pogie_id)

        self.assertTrue(isinstance(reply, list),
            msg="my_processed_orders function not working")

    def test_my_unprocessed_orders(self):
        admin_ob = SendItUserOrders(self.etomovich_id)
        user_ob = SendItUserOrders(self.pogie_id)
        false_user = SendItUserOrders(00000)

        admin_parc = SendItParcels(self.etomovich_id)

        reply = admin_parc.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        #Create an order
        reply = user_ob.add_order(parcel_id)

        self.assertTrue(isinstance(reply, dict),
            msg="Add order function not working")

        pog_order_list=SendItUserOrders.sendit_user_orders\
            [self.pogie_id]

        order_item = ""
        for thing in pog_order_list:
            if thing["parcel_id"] == parcel_id:
                order_item = thing

        reply = false_user.my_unprocessed_orders(self.pogie_id)

        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="my_processed_orders function not working")

        reply = admin_ob.my_unprocessed_orders(self.pogie_id)

        self.assertTrue(isinstance(reply, list),
            msg="my_unprocessed_orders function not working")

    def test_user_order_deletion(self):
        admin_ob = SendItUserOrders(self.etomovich_id)
        user_ob = SendItUserOrders(self.pogie_id)
        false_user = SendItUserOrders(00000)

        admin_parc = SendItParcels(self.etomovich_id)

        reply = admin_parc.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        #Create an order
        reply = user_ob.add_order(parcel_id)

        self.assertTrue(isinstance(reply, dict),
            msg="Add order function not working")

        pog_order_list=SendItUserOrders.sendit_user_orders\
            [self.pogie_id]

        order_item = ""
        for thing in pog_order_list:
            if thing["parcel_id"] == parcel_id:
                order_item = thing

        reply = false_user.user_order_deletion(order_item['order_id'])

        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="user_order_deletion function not working")

        reply = user_ob.user_order_deletion("457777")

        self.assertEqual(reply["message"],"ORDER PROCCESSED OR NOT FOUND",
            msg="Return all orders function not working")

        reply = user_ob.user_order_deletion(order_item['order_id'])

        self.assertEqual(reply["message"],"DELETED",
            msg="Return all orders function not working")

    def test_admin_order_deletion(self):
        admin_ob = SendItUserOrders(self.etomovich_id)
        user_ob = SendItUserOrders(self.pogie_id)
        false_user = SendItUserOrders(00000)

        admin_parc = SendItParcels(self.etomovich_id)

        reply = admin_parc.add_parcel(self.pogie_id,\
            "parecel_name","45","submission_station",\
                    "present_location")

        self.assertEqual(reply["message"],"CREATED",
            msg="Add parcels function not working")

        parcel_id = ""
        for item in SendItParcels.sendit_parcels.keys():
            if SendItParcels.sendit_parcels[item]['owner_id'] \
            == self.pogie_id:
                parcel_id = item

        #Create an order
        reply = user_ob.add_order(parcel_id)

        self.assertTrue(isinstance(reply, dict),
            msg="Add order function not working")

        pog_order_list=SendItUserOrders.sendit_user_orders\
            [self.pogie_id]

        order_item = ""
        for thing in pog_order_list:
            if thing["parcel_id"] == parcel_id:
                order_item = thing

        reply = user_ob.admin_order_deletion(order_item['order_id'])

        self.assertEqual(reply["message"],"UNAUTHORIZED",
            msg="user_order_deletion function not working")

        reply = admin_ob.admin_order_deletion("457777")

        self.assertEqual(reply["message"],"ORDER NOT FOUND",
            msg="Return all orders function not working")

        reply = admin_ob.admin_order_deletion(order_item['order_id'])

        self.assertEqual(reply["message"],"DELETED",
            msg="Return all orders function not working")

        