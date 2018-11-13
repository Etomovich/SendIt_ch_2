from flask import request, make_response, jsonify
from flask_restful import Resource
from marshmallow import Schema, fields, ValidationError,\
        post_dump,post_load,validates

from courier_app.send_it_apis.v1.validators import user_model_validators
from courier_app.send_it_apis.v1.models import SystemUsers

from courier_app.send_it_apis.pagination import Kurasa
from instance.config import Config

from itsdangerous import (TimedJSONWebSignatureSerializer as
        Serializer, BadSignature, SignatureExpired)

class CreateUser(Resource):

    def post(self):
        #Register user
        user_inp = request.get_json() or {}
        schema = user_model_validators.CreateUserSchema()
        result = schema.load(user_inp)
        
        if len(result.errors) < 1:
            creator = SystemUsers(00)
            creator.add_user(result.data['username'],result.data['email'],\
                result.data['phone_number'],result.data['password'], 
                result.data['role'])
            pack = {"Status":"Created","User":result.data}
            answer = make_response(jsonify(pack),201)
            answer.content_type='application/json;charset=utf-8'
            return answer
        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer

class UserLogin(Resource):
    def post(self):
         #Login user
        user_inp = request.get_json() or {}
        schema = user_model_validators.LoginUserSchema()
        result = schema.load(user_inp)
        
        if len(result.errors) < 1:
            creator = SystemUsers(00)
            reply=creator.login_user(result.data['password'],\
            result.data['username'])
            if reply:
                pack = {"Status":"Logged In.","Token":reply}
                answer = make_response(jsonify(pack),200)
                answer.content_type='application/json;charset=utf-8'
                return answer
            else:
                pack = {"Status":"Invalid Credentials"}
                answer = make_response(jsonify(pack),401)
                answer.content_type='application/json;charset=utf-8'
                return answer
        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer

class FetchAllUsers(Resource):
    def get(self):
        auth_user = _authenticate_admin()
        if not isinstance(auth_user, dict):
            return auth_user        
        all_users = SystemUsers(auth_user['user_id'])
        pack = all_users.get_all_users()

        if (isinstance(pack, list)):
            #Return results
            kur = Kurasa(pack, 2)
            page = request.args.get('page', 1, type=int)
            page_items = kur.get_items(page)
            reply = {
                "Status":"OK",
                "Users": page_items,
                "Total Users": len(pack),
                "Total Pages": str(kur.no_of_pages),
                "Next Page":"https://etomovich-sendit.herokuapp.com/api/v1/users?page="+\
                    str(page+1) if kur.has_next(page) else "END",
                "Prev Page":"https://etomovich-sendit.herokuapp.com/api/v1/users?page="+\
                    str(page-1) if kur.has_prev(page) else "BEGINNING"
            }
            answer = make_response(jsonify(reply),200)
            answer.content_type='application/json;charset=utf-8'
            return answer 


class TheUser(Resource):
    def get(self,user_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = user_model_validators.UserIdSchema()
        input_data = {"user_id":user_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            this_user = SystemUsers(auth_user['user_id'])
            pack = this_user.get_a_user(str(user_id))
            if (isinstance(pack, dict)):
                reply = {
                    "Status":"OK",
                    "User": pack
                }
                answer = make_response(jsonify(reply),200)
                answer.content_type='application/json;charset=utf-8'
                return answer
            else:
                answer = make_response(jsonify(pack),401)
                answer.content_type='application/json;charset=utf-8'
                return answer
        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer
    
    def put(self,user_id):
        '''This function edits a user.'''
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        user_inp = request.get_json() or {}
        user_inp['user_id'] = user_id
        schema = user_model_validators.EditUserSchema()
        result = schema.load(user_inp)
        if len(result.errors) < 1:
            this_data ={
                "user_id": result.data["user_id"],
                "username": result.data["username"] if\
                    "username" in result.data else None,
                "email": result.data["email"] if\
                    "email" in result.data else None,
                "phone_no": result.data["phone_no"] if\
                    "phone_no" in result.data else None,
                "password": result.data["password"] if\
                    "password" in result.data else None,
                "role": result.data["role"] if\
                    "role" in result.data else None
            }
            edit_users = SystemUsers(auth_user['user_id'])
            reply = edit_users.edit_user(
                user_id = this_data['user_id'],
                username=this_data['username'],
                email=this_data['email'],
                phone_no=this_data['phone_no'],
                password=this_data['password'],
                role=this_data['role']
            )

            if reply == True:
                pack = {"Status":"OK","Message":"User updated successfullly!!"}
                answer = make_response(jsonify(pack),200)
                answer.content_type='application/json;charset=utf-8'
                return answer
            else:
                pack = {"Status":"Unauthorized","Message":reply}
                answer = make_response(jsonify(pack),401)
                answer.content_type='application/json;charset=utf-8'
                return answer

        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer

    def delete(self,user_id):
        '''This function deletes a user.'''
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = user_model_validators.UserIdSchema()
        input_data = {"user_id":user_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            this_user = SystemUsers(auth_user['user_id'])
            pack = this_user.delete_a_user(str(user_id))
            if pack == True:
                reply = {
                    "Status":"Deleted"
                }
                answer = make_response(jsonify(reply),200)
                answer.content_type='application/json;charset=utf-8'
                return answer
            else:
                answer = make_response(jsonify(pack),401)
                answer.content_type='application/json;charset=utf-8'
                return answer
        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer

def _authenticate_admin():
    current_user = ""
    token = request.headers.get('Authorization')
    s = Serializer(Config.SECRET_KEY, expires_in=21600)
    try:
        data = s.loads(str(token))
        current_user = SystemUsers.send_it_users[data['user_id']]
    except:
        reply="You are not authorized to view this page!!"
        answer = make_response(jsonify(reply),401)
        answer.content_type='application/json;charset=utf-8'
        return answer

    if current_user['role'] == "User":
        reply="This is an Admin Page contact admin for more help!!"
        answer = make_response(jsonify(reply),401)
        answer.content_type='application/json;charset=utf-8'
        return answer

    current_user['user_id'] = data['user_id']
    return current_user

def _authenticate_user():
    current_user = ""
    token = request.headers.get('Authorization')
    s = Serializer(Config.SECRET_KEY, expires_in=21600)
    try:
        data = s.loads(str(token))
        current_user = SystemUsers.send_it_users[data['user_id']]
    except:
        reply="You are not authorized to view this page!!"
        answer = make_response(jsonify(reply),401)
        answer.content_type='application/json;charset=utf-8'
        return answer

    current_user['user_id'] = data['user_id']
    return current_user
