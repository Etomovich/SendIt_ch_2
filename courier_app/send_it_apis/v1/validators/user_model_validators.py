import re 

from marshmallow import (Schema, fields, ValidationError,
        post_dump,post_load,validates, validates_schema)

from courier_app.send_it_apis.v1.models import SystemUsers


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
            
        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['username'] == username:
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

        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['phone_number'] == phone_number:
                raise ValidationError\
                ("[phone_number] is already taken.")
    
    @validates("email")
    def validate_unique_email(self,email):
        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['email'] == email:
                raise ValidationError\
                ("[email] is already taken.")

class EditUserSchema(Schema):
    user_id = fields.Integer(required = True)
    username= fields.String()
    email= fields.Email()
    phone_no= fields.String()
    password= fields.String()
    retype_password = fields.String()
    role= fields.String()

    @validates("user_id")
    def validate_user_id(self,user_id):
        if str(user_id) not in SystemUsers.send_it_users.keys():
            raise ValidationError\
            ("[user_id] is not in system.")


    @validates_schema
    def validate_password_retype_equality(self, data):
        if "password" in data.keys():
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
        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['username'] == username:
                raise ValidationError\
                ("[username] is already taken.")

    @validates("phone_no")
    def validate_unique_phone_number(self,phone_number):
        r=re.compile("^[\+,\d]{1,}\d+$")

        if not r.match(phone_number):
            raise ValidationError\
                ("[phone_number] should be a string of integers but"+
                "can also begin with a plus for international"+
                "calls.")

        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['phone_number'] == phone_number:
                raise ValidationError\
                ("[phone_number] is already taken.")
  
    @validates("email")
    def validate_unique_email(self,email):
        for item in SystemUsers.send_it_users.keys():
            if SystemUsers.send_it_users[item]['email'] == email:
                raise ValidationError\
                ("[email] is already taken.")

class UserIdSchema(Schema):
    user_id = fields.Integer(required = True)

    @validates("user_id")
    def validate_user_id(self,user_id):
        if str(user_id) not in SystemUsers.send_it_users.keys():
            raise ValidationError\
            ("[user_id] is not in system.")

class LoginUserSchema(Schema):
    username = fields.String(required = True)
    password = fields.String(required = True)