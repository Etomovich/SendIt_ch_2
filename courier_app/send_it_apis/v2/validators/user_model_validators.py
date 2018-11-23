import re 

from marshmallow import (Schema, fields, ValidationError,
        post_dump,post_load,validates, validates_schema)

from courier_app.send_it_apis.v2.models import SystemUsers
from courier_app.database import connection
import psycopg2

class CreateUserSchema(Schema):
    '''This schema validates user creation data '''
    username = fields.String(required =True) 
    email = fields.Email(required =True)
    phone_number = fields.String(required =True)
    password = fields.String(required =True)
    retype_password = fields.String(required =True)
    role = fields.String(required =True)

    @validates_schema
    def validate_password_retype_equality(self, data):
        if data['password'] != data['retype_password']:
            raise ValidationError\
            ("[password] and [retype_password] should be equal.")
        if len(data['password'].strip()) == 0:
            raise ValidationError\
            ("[password] cannot be null")

    @validates("role")
    def validate_role(self, role):
        if role != "Admin" and role != "User":
            raise ValidationError\
            ("[role] can either be Admin or User.")

    @validates("username")
    def validate_unique_username(self,username):
        if not username.isalpha():
            raise ValidationError\
            ("[username] should only contain alphabetic letters.")

        con = connection()
        cur = con.cursor()

        select_query = """select * from sendit_users"""
        cur.execute(select_query)
        record = cur.fetchall()

        cur.close()
        con.close()
        for item in record:
            if username == item[1]:
                raise ValidationError\
                    ("[username] is already taken.")
   
    @validates("phone_number")
    def validate_unique_phone_number(self,phone_number):
        r=re.compile("^[\+,\d]{1,}\d+$")

        if not r.match(phone_number):
            raise ValidationError\
                ("[phone_number] should be an integer but"+
                "can also begin with a plus for international"+
                "calls.")

        con = connection()
        cur = con.cursor()

        select_query = """select * from sendit_users"""
        cur.execute(select_query)
        record = cur.fetchall()

        # closing database connection.
        cur.close()
        con.close() 

        for item in record:
            if phone_number == item[3]:
                raise ValidationError\
                    ("[phone_number] is already taken.")

    @validates("email")
    def validate_unique_email(self,email):
        con = connection()
        cur = con.cursor()

        select_query = """select * from sendit_users"""
        cur.execute(select_query)
        record = cur.fetchall()

        cur.close()
        con.close()

        for item in record:
            if email == item[2]:
                raise ValidationError\
                    ("[email] is already taken.")

class EditUserSchema(Schema):
    user_id = fields.Integer(required = True)
    username= fields.String()
    email= fields.Email()
    phone_number= fields.String()
    password= fields.String()
    retype_password = fields.String()
    role= fields.String()

    @validates("user_id")
    def validate_user_id(self,user_id):
        con = connection()
        cur = con.cursor()

        select_query = """select * from sendit_users"""
        cur.execute(select_query)
        record = cur.fetchall()
        # closing database connection.
        cur.close()
        con.close()

        is_in=False
        for item in record:
            if user_id == item[0]:
                is_in = True
                break
        if is_in == False:
            raise ValidationError("[user_id] is not in system.")

    @validates_schema
    def validate_password_retype_equality(self, data):
        if "password" in data.keys():
            if data['password'] != data['retype_password']:
                raise ValidationError\
                ("[password] and [retype_password] should be equal.")

        if ("password" in data.keys() and 
            len(data['password'].strip()) == 0):
            raise ValidationError\
            ("[password] cannot be null")

    @validates("role")
    def validate_role(self, role):
        if role != "Admin" and role != "User":
            raise ValidationError\
            ("[role] can either be Admin or User.")

    @validates("username")
    def validate_unique_username(self,username):
        if not username.isalpha():
            raise ValidationError\
            ("[username] should only contain alphabetic letters.")

        con = connection()
        cur = con.cursor()

        select_query = """select * from sendit_users"""
        cur.execute(select_query)
        record = cur.fetchall()

        cur.close()
        con.close()
        for item in record:
            if username == item[1]:
                raise ValidationError\
                    ("[username] is already taken.")

    @validates("phone_number")
    def validate_unique_phone_number(self,phone_number):
        r=re.compile("^[\+,\d]{1,}\d+$")

        if not r.match(phone_number):
            raise ValidationError\
                ("[phone_number] should be an integer but"+
                "can also begin with a plus for international"+
                "calls.")

        con = connection()
        cur = con.cursor()

        select_query = """select * from sendit_users"""
        cur.execute(select_query)
        record = cur.fetchall()

        # closing database connection.
        cur.close()
        con.close() 

        for item in record:
            if phone_number == item[3]:
                raise ValidationError\
                    ("[phone_number] is already taken.")
  
    @validates("email")
    def validate_unique_email(self,email):
        con = connection()
        cur = con.cursor()

        select_query = """select * from sendit_users"""
        cur.execute(select_query)
        record = cur.fetchall()

        cur.close()
        con.close()

        for item in record:
            if email == item[2]:
                raise ValidationError\
                    ("[email] is already taken.")

class UserIdSchema(Schema):
    user_id = fields.Integer(required = True)

    @validates("user_id")
    def validate_user_id(self,user_id):
        con = connection()
        cur = con.cursor()

        select_query = """select * from sendit_users"""
        cur.execute(select_query)
        record = cur.fetchall()
        # closing database connection.
        cur.close()
        con.close()

        is_in=False
        for item in record:
            if user_id == item[0]:
                is_in = True
                break
        if not is_in:
            raise ValidationError("[user_id] is not in system.")

class LoginUserSchema(Schema):
    username = fields.String(required = True)
    password = fields.String(required = True)
