import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer as
    Serializer, BadSignature, SignatureExpired)

from instance.config import Config
class SystemUsers(object):
    '''This class implements storage of SystemUsers'''    
    send_it_users = {}
    
    def __init__(self, current_user_id):
        self.current_user_id = str(int(current_user_id))

    def add_user(self, username, email,phoneNo,password, role):
        '''This method adds a new user to the database'''
        from courier_app.send_it_apis.v1.models import SendItUserOrders
        payload = {
            "username": username,
            "email": email,
            "phone_number":phoneNo,
            "role": role,
            "password": generate_password_hash(password)
        }

        new_id = uuid.uuid4().int
        SendItUserOrders.sendit_user_orders[str(new_id)] = []
        SystemUsers.send_it_users[str(new_id)] = payload
        payload['user_id'] = str(new_id)
        out_data = {
            "user_id": payload['user_id'],
            "username": payload['username'],
            "email": payload['email'],
            "phone_number": payload['phone_number'],
            "role": payload['role']
        }
        return out_data

    def _user_is_there(self):
        try:
            my_user={}
            my_user = SystemUsers.send_it_users[str(self.current_user_id)]
            my_user["user_id"] = self.current_user_id
            return my_user
        except:
            return False

    def edit_user(self,user_id,username=None,email=None,phone_no=None,\
                                                password=None,role=None):
        '''This method allows current_user to edit his/her personal details and
        also allows an Admin to revoke a password. You pass in the user_id of 
        the user you want to edit and details of the specifics.'''        
        this_user = self._user_is_there()
        if this_user:
            if this_user["user_id"] == str(user_id) or this_user["role"] == "Admin":
                if username:
                    SystemUsers.send_it_users[str(user_id)]["username"] = username
                if email:
                    SystemUsers.send_it_users[str(user_id)]["email"] = email
                if phone_no:
                    SystemUsers.send_it_users[str(user_id)]["phone_number"] = phone_no
                if password:
                    SystemUsers.send_it_users[str(user_id)]["password"] = password
                if role:
                    if SystemUsers.send_it_users[this_user["user_id"]]\
                        ["role"] == "Admin":
                        SystemUsers.send_it_users[str(user_id)]["role"] = role
                    else:
                        return {"message":"UNAUTHORIZED<Field:'role'>"}
                my_user = SystemUsers.send_it_users[str(user_id)]
                my_user["message"] = "Authorized"
                out_data = {
                    "message": my_user['message'],
                    "user_id": my_user['user_id'],
                    "username": my_user['username'],
                    "email": my_user['email'],
                    "phone_number": my_user['phone_number'],
                    "role": my_user['role']
                }
                return out_data
            return {"message":"UNAUTHORIZED"}
        return {"message":"UNAUTHORIZED"}
                   
    def  get_a_user(self, userid):
        '''This method returns a single user. It is only visible to Admin 
        and current user'''
        try:
            this_user = self._user_is_there()
            if this_user:
                if this_user["user_id"] == str(userid) or this_user["role"] == "Admin":
                    my_user={}
                    my_user = SystemUsers.send_it_users[str(userid)]
                    my_user["user_id"] = str(userid)
                    my_user["message"] = "Authorized"

                    out_data = {
                        "message": my_user['message'],
                        "user_id": my_user['user_id'],
                        "username": my_user['username'],
                        "email": my_user['email'],
                        "phone_number": my_user['phone_number'],
                        "role": my_user['role']
                    }
                    return out_data
                return {"message":"UNAUTHORIZED"}
            return {"message":"UNKNOWN USER"}
        except:
            return {"message":"UNKNOWN USER"}

    def delete_a_user(self, userid):
        '''This method allows the admin to delete a single user.'''        
        this_user = self._user_is_there()
        if this_user:
            if this_user["user_id"] == str(userid) or \
                this_user["role"] == "Admin":
                del SystemUsers.send_it_users[str(userid)]
                return {"message":"DELETED"}
            return {"message":"UNAUTHORIZED"}
        return {"message":"UNAUTHORIZED"}

    def login_user(self, password, my_name):
        '''This method allows the admin to create a user'''
        from courier_app.send_it_apis.v1.models import SystemUsers
        for item in SystemUsers.send_it_users.keys():
            if my_name == SystemUsers.send_it_users[item]\
                ['email'] or my_name == SystemUsers.send_it_users\
                [item]['username']:
                pass_code = SystemUsers.send_it_users[item]\
                    ['password']
                if check_password_hash(pass_code,password):
                    s = Serializer(Config.SECRET_KEY, expires_in=21600)
                    token = (s.dumps({'user_id': item})).decode("ascii")
                    return token
                else:
                    return False
        return False

    def get_all_users(self):
        this_user = self._user_is_there()
        if this_user and this_user["role"] == "Admin":
            reply = []
            for thing in SystemUsers.send_it_users.keys():
                user = SystemUsers.send_it_users[thing]
                user["user_id"] = thing
                out_data = {
                    "user_id": user['user_id'],
                    "username": user['username'],
                    "email": user['email'],
                    "phone_number": user['phone_number'],
                    "role": user['role']
                }
                reply.append(out_data)
            return reply
        return {"message":"UNAUTHORIZED"}


