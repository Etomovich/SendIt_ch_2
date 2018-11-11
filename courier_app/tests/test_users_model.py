import unittest
from instance.config import Config
from courier_app.send_it_apis.v1.models import SystemUsers,\
    SendItParcels, SendItUserOrders

class UserModelCase(unittest.TestCase):
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

    def tearDown(self):
        SystemUsers.send_it_users = {}
        SendItParcels.sendit_parcels ={}
        SendItUserOrders.sendit_user_orders ={}

    def test_create_user_from_root(self):
        users_DB = SystemUsers(0000)
        answ = users_DB.add_user(self.user_1['username'],self.user_1['email'],\
            self.user_1['phoneNo'],self.user_1['password'],\
            self.user_1['role'])
        self.assertTrue(answ, msg="There is an error when creating user"+ 
        "with valid credentials")
        #remove user after test

    def test_check_invalid_user(self):
        users_DB = SystemUsers(0000)
        answ = users_DB._user_is_there()
        self.assertFalse(answ, msg="User does not exist, expects False")

    def test_check_valid_user(self):
        users_DB = SystemUsers(0000)
        answ = users_DB.add_user(self.user_1['username'],self.user_1['email'],\
            self.user_1['phoneNo'],self.user_1['password'],\
            self.user_1['role'])

        user_id = ""
        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['username'] \
            == "etomovich":
                user_id = item         

        this_user = SystemUsers(user_id)
        answ = this_user._user_is_there()
        self.assertTrue(isinstance(answ, dict),\
            msg="User exist, expects True")
        self.assertEqual(answ['username'],"etomovich",
            msg="User exist, expects True")          
    
    def test_check_edit_user(self):
        users_DB = SystemUsers(0000)
        answ = users_DB.add_user(self.user_1['username'],self.user_1['email'],\
            self.user_1['phoneNo'],self.user_1['password'],\
            self.user_1['role'])

        answ = users_DB.add_user(self.user_2['username'],self.user_2['email'],\
            self.user_2['phoneNo'],self.user_2['password'],\
            self.user_2['role'])
        
        etomovich_id = ""
        pogie_id = ""
        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['username'] \
            == "etomovich":
                etomovich_id = item
            if SystemUsers.send_it_users[item]['username'] \
            == "pogie":
                pogie_id = item  

        admin_ob = SystemUsers(etomovich_id)
        user_ob = SystemUsers(pogie_id)

        reply = users_DB.edit_user(pogie_id, phone_no="54678")
        self.assertEqual(reply,"UNAUTHORIZED",
            msg="Edit User not working")

        reply = user_ob.edit_user(etomovich_id, phone_no="54678")
        self.assertEqual(reply,"UNAUTHORIZED",
            msg="Edit User not working")

        reply = user_ob.edit_user(pogie_id, role="Admin")
        self.assertEqual(reply,"UNAUTHORIZED<Field:'role'>",
            msg="Edit User not working")

        reply = admin_ob.edit_user(pogie_id, role="Admin")
        self.assertEqual(reply,True, 
            msg="Edit User not working")

        reply = admin_ob.edit_user(pogie_id, username="Pogba")
        self.assertEqual(reply,True, 
            msg="Edit User not working")

        reply = admin_ob.edit_user(pogie_id, email="pog@g.com")
        self.assertEqual(reply,True, 
            msg="Edit User not working")

        reply = admin_ob.edit_user(pogie_id, phone_no="034556")
        self.assertEqual(reply,True, 
            msg="Edit User not working")

        reply = admin_ob.edit_user(pogie_id, password="pogz")
        self.assertEqual(reply,True, 
            msg="Edit User not working")

    def test_get_a_user(self):
        users_DB = SystemUsers(0000)
        answ = users_DB.add_user(self.user_1['username'],self.user_1['email'],\
            self.user_1['phoneNo'],self.user_1['password'],\
            self.user_1['role'])

        answ = users_DB.add_user(self.user_2['username'],self.user_2['email'],\
            self.user_2['phoneNo'],self.user_2['password'],\
            self.user_2['role'])
        
        etomovich_id = ""
        pogie_id = ""
        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['username'] \
            == "etomovich":
                etomovich_id = item
            if SystemUsers.send_it_users[item]['username'] \
            == "pogie":
                pogie_id = item  

        admin_ob = SystemUsers(etomovich_id)
        user_ob = SystemUsers(pogie_id)

        reply = users_DB.get_a_user(pogie_id)
        self.assertEqual(reply,"UNKNOWN_USER",
            msg="Get User not working")

        reply = user_ob.get_a_user(etomovich_id)
        self.assertEqual(reply,"UNAUTHORIZED",
            msg="Get User not working")

        reply = user_ob.get_a_user(pogie_id)
        self.assertTrue(isinstance(reply, dict),
            msg="Get User not working")

        reply = admin_ob.get_a_user(000000)
        self.assertEqual(reply,"UNKNOWN_USER", 
            msg="Get User not working")

    def test_delete_a_user(self):
        users_DB = SystemUsers(0000)
        answ = users_DB.add_user(self.user_1['username'],self.user_1['email'],\
            self.user_1['phoneNo'],self.user_1['password'],\
            self.user_1['role'])

        answ = users_DB.add_user(self.user_2['username'],self.user_2['email'],\
            self.user_2['phoneNo'],self.user_2['password'],\
            self.user_2['role'])
        
        etomovich_id = ""
        pogie_id = ""
        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['username'] \
            == "etomovich":
                etomovich_id = item
            if SystemUsers.send_it_users[item]['username'] \
            == "pogie":
                pogie_id = item  

        admin_ob = SystemUsers(etomovich_id)
        user_ob = SystemUsers(pogie_id)

        reply = user_ob.delete_a_user(etomovich_id)
        self.assertEqual(reply,"UNAUTHORIZED",
            msg="Delete User not working")

        reply = users_DB.delete_a_user(etomovich_id)
        self.assertEqual(reply,"UNAUTHORIZED",
            msg="Delete User not working")

        reply = user_ob.delete_a_user(pogie_id)
        self.assertEqual(reply,True,
            msg="Delete User not working")

    def test_login_a_user(self):
        users_DB = SystemUsers(0000)
        answ = users_DB.add_user(self.user_1['username'],self.user_1['email'],\
            self.user_1['phoneNo'],self.user_1['password'],\
            self.user_1['role'])

        answ = users_DB.add_user(self.user_2['username'],self.user_2['email'],\
            self.user_2['phoneNo'],self.user_2['password'],\
            self.user_2['role'])
        
        etomovich_id = ""
        pogie_id = ""
        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['username'] \
            == "etomovich":
                etomovich_id = item
            if SystemUsers.send_it_users[item]['username'] \
            == "pogie":
                pogie_id = item  

        admin_ob = SystemUsers(etomovich_id)
        user_ob = SystemUsers(pogie_id)

        reply = users_DB.login_user("Mayweather","money-man")
        self.assertFalse(reply,
            msg="Login User not working")

        reply = users_DB.login_user("etomovich","money-man")
        self.assertFalse(reply,
            msg="Login User not working")

        reply = users_DB.login_user("pogie","etomovich")
        self.assertFalse(reply,
            msg="Login User not working")

        reply = users_DB.login_user("etomovich","etomovich")
        self.assertTrue(reply,
            msg="Login User not working")

    def test_get_all_users(self):
        users_DB = SystemUsers(0000)
        answ = users_DB.add_user(self.user_1['username'],self.user_1['email'],\
            self.user_1['phoneNo'],self.user_1['password'],\
            self.user_1['role'])

        answ = users_DB.add_user(self.user_2['username'],self.user_2['email'],\
            self.user_2['phoneNo'],self.user_2['password'],\
            self.user_2['role'])
        
        etomovich_id = ""
        pogie_id = ""
        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['username'] \
            == "etomovich":
                etomovich_id = item
            if SystemUsers.send_it_users[item]['username'] \
            == "pogie":
                pogie_id = item  

        admin_ob = SystemUsers(etomovich_id)
        user_ob = SystemUsers(pogie_id)

        reply = user_ob.get_all_users()
        self.assertEqual(reply,"UNAUTHORIZED",
            msg="Get all users not working")

        reply = admin_ob.get_all_users()
        self.assertTrue(isinstance(reply, list),
            msg="Get all users not working")