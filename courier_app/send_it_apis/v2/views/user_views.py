import os
import psycopg2

from flask import request, make_response, jsonify
from flask_restful import Resource
from marshmallow import Schema, fields, ValidationError,\
    post_dump, post_load, validates

from courier_app.send_it_apis.v2.validators import user_model_validators
from courier_app.send_it_apis.v2.models import SystemUsers

from courier_app.send_it_apis.pagination import Kurasa
from instance.config import Config

from itsdangerous import (TimedJSONWebSignatureSerializer as
                          Serializer, BadSignature, SignatureExpired)


BASE_URL = os.getenv('PAGINATE_BASE_URL')


class CreateUser(Resource):
    def post(self):
        # Register user
        user_inp = request.get_json() or {}
        schema = user_model_validators.CreateUserSchema()
        result = schema.load(user_inp)

        if len(result.errors) < 1:
            creator = SystemUsers(00)
            person = creator.add_user(
                username= result.data['username'], 
                email= result.data['email'],
                phoneNo=result.data['phone_number'], 
                password= result.data['password']
            )
            pack = {"Status": "Created", "User": person}
            answer = make_response(jsonify(pack), 201)
            answer.content_type = 'application/json;charset=utf-8'
            return answer
        pack = {"Status": "Bad Request", "Errors": result.errors}
        answer = make_response(jsonify(pack), 400)
        answer.content_type = 'application/json;charset=utf-8'
        return answer


class UserLogin(Resource):
    def post(self):
         # Login user
        user_inp = request.get_json() or {}
        schema = user_model_validators.LoginUserSchema()
        result = schema.load(user_inp)

        if len(result.errors) < 1:
            creator = SystemUsers(00)
            reply = creator.login_user(result.data['password'],
                                       result.data['username'])
            if reply:
                pack = {
                    "Status": "Logged In.", 
                    "Token": reply["token"],
                    "role": reply["role"],
                    "username":reply["username"],
                    "user_id": reply["user_id"]
                }
                answer = make_response(jsonify(pack), 200)
                answer.content_type = 'application/json;charset=utf-8'
                return answer
            pack = {"Status": "Invalid Credentials"}
            answer = make_response(jsonify(pack), 401)
            answer.content_type = 'application/json;charset=utf-8'
            return answer
        pack = {"Status": "Bad Request", "Errors": result.errors}
        answer = make_response(jsonify(pack), 400)
        answer.content_type = 'application/json;charset=utf-8'
        return answer


class FetchAllUsers(Resource):
    def get(self):
        auth_user = _authenticate_admin()
        if not isinstance(auth_user, dict):
            return auth_user
        all_users = SystemUsers(auth_user['user_id'])
        pack = all_users.get_all_users()

        if (isinstance(pack, list)):
            # Return results
            kur = Kurasa(pack, 2)
            page = request.args.get('page', 1, type=int)
            page_items = kur.get_items(page)
            reply = {
                "Status": "OK",
                "Users": page_items,
                "Total Users": len(pack),
                "Total Pages": str(kur.no_of_pages),
                "Next Page": BASE_URL+"/api/v2/users?page=" +
                str(page+1) if kur.has_next(page) else "END",
                "Prev Page": BASE_URL+"/api/v2/users?page=" +
                str(page-1) if kur.has_prev(page) else "BEGINNING"
            }
            answer = make_response(jsonify(reply), 200)
            answer.content_type = 'application/json;charset=utf-8'
            return answer
        answer = make_response(jsonify(pack), 401)
        answer.content_type = 'application/json;charset=utf-8'
        return answer


class TheUser(Resource):
    def get(self, user_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = user_model_validators.UserIdSchema()
        input_data = {"user_id": user_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            this_user = SystemUsers(auth_user['user_id'])
            pack = this_user.get_a_user(str(user_id))
            if (pack['message'] == "Authorized"):
                reply = {
                    "Status": "OK",
                    "User": pack
                }
                answer = make_response(jsonify(reply), 200)
                answer.content_type = 'application/json;charset=utf-8'
                return answer
            answer = make_response(jsonify(pack), 401)
            answer.content_type = 'application/json;charset=utf-8'
            return answer
        pack = {"Status": "Bad Request", "Errors": result.errors}
        answer = make_response(jsonify(pack), 400)
        answer.content_type = 'application/json;charset=utf-8'
        return answer

    def put(self, user_id):
        '''This function edits a user.'''
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        user_inp = request.get_json() or {}
        user_inp['user_id'] = user_id
        schema = user_model_validators.EditUserSchema()
        result = schema.load(user_inp)
        if len(result.errors) < 1:
            this_data = {
                "user_id": result.data["user_id"],
                "username": result.data["username"] if
                "username" in result.data else None,
                "email": result.data["email"] if
                "email" in result.data else None,
                "phone_number": result.data["phone_number"] if
                "phone_number" in result.data else None,
                "password": result.data["password"] if
                "password" in result.data else None,
                "role": result.data["role"] if
                "role" in result.data else None
            }
            edit_users = SystemUsers(auth_user['user_id'])
            reply = edit_users.edit_user(
                user_id=this_data['user_id'],
                username=this_data['username'],
                email=this_data['email'],
                phone_no=this_data['phone_number'],
                password=this_data['password'],
                role=this_data['role']
            )

            if reply['message'] == "Authorized":
                pack = {"Status": "Success", "Message": reply}
                answer = make_response(jsonify(pack), 200)
                answer.content_type = 'application/json;charset=utf-8'
                return answer
            pack = {"Status": "Unauthorized"}
            answer = make_response(jsonify(pack), 401)
            answer.content_type = 'application/json;charset=utf-8'
            return answer
        pack = {"Status": "Bad Request", "Errors": result.errors}
        answer = make_response(jsonify(pack), 400)
        answer.content_type = 'application/json;charset=utf-8'
        return answer

    def delete(self, user_id):
        '''This function deletes a user.'''
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = user_model_validators.UserIdSchema()
        input_data = {"user_id": user_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            this_user = SystemUsers(auth_user['user_id'])
            pack = this_user.delete_a_user(str(user_id))
            if pack["message"] == "DELETED":
                reply = {
                    "Status": "Deleted"
                }
                answer = make_response(jsonify(reply), 200)
                answer.content_type = 'application/json;charset=utf-8'
                return answer
            answer = make_response(jsonify(pack), 401)
            answer.content_type = 'application/json;charset=utf-8'
            return answer
        pack = {"Status": "Bad Request", "Errors": result.errors}
        answer = make_response(jsonify(pack), 400)
        answer.content_type = 'application/json;charset=utf-8'
        return answer


def _authenticate_admin():
    from courier_app.database import connection
    current_user = ""
    token = request.headers.get('Authorization')
    s = Serializer(Config.SECRET_KEY, expires_in=21600)
    try:
        con = connection()
        cur = con.cursor()

        data = s.loads(str(token))

        select_query = """select * from sendit_users where user_id = %s"""
        cur.execute(select_query, (data['user_id'], ))
        record = cur.fetchone()
        cur.close()
        con.close()
        print("PostgreSQL connection is closed")
        if record:
            current_user = {
                "message": "OK",
                "user_id": record[0],
                "username": record[1],
                "email": record[2],
                "phone_number": record[3],
                "role": record[4],
                "password": record[5]
            }
            if current_user['role'] == "User":
                reply = {
                    "message":
                    "This is an Admin Page contact admin for more help!!"
                }
                answer = make_response(jsonify(reply), 401)
                answer.content_type = 'application/json;charset=utf-8'
                return answer
            return current_user
        reply = {"message": "You are not authorized to view this page!!"}
        answer = make_response(jsonify(reply), 401)
        answer.content_type = 'application/json;charset=utf-8'
        return answer
    except (Exception, psycopg2.Error) as error:
        cur.close()
        con.close()
        print("User failed to load", error)
        print("PostgreSQL connection is closed")
        reply = {"message": "You are not authorized to view this page!!"}
        answer = make_response(jsonify(reply), 401)
        answer.content_type = 'application/json;charset=utf-8'
        return answer


def _authenticate_user():
    from courier_app.database import connection
    current_user = ""
    token = request.headers.get('Authorization')
    s = Serializer(Config.SECRET_KEY, expires_in=21600)
    try:
        con = connection()
        cur = con.cursor()

        data = s.loads(str(token))

        select_query = """select * from sendit_users where user_id = %s"""
        cur.execute(select_query, (data['user_id'], ))
        record = cur.fetchone()
        cur.close()
        con.close()
        print("PostgreSQL connection is closed")
        if record:
            current_user = {
                "message": "OK",
                "user_id": record[0],
                "username": record[1],
                "email": record[2],
                "phone_number": record[3],
                "role": record[4],
                "password": record[5]
            }
            return current_user
        reply = {"message": "You are not authorized to view this page!!"}
        answer = make_response(jsonify(reply), 401)
        answer.content_type = 'application/json;charset=utf-8'
        return answer
    except (Exception, psycopg2.Error) as error:
        cur.close()
        con.close()
        print("User failed to load", error)
        print("PostgreSQL connection is closed")
        reply = {"message": "You are not authorized to view this page!!"}
        answer = make_response(jsonify(reply), 401)
        answer.content_type = 'application/json;charset=utf-8'
        return answer
