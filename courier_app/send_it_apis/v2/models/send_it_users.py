import uuid
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer as
                          Serializer, BadSignature, SignatureExpired)
from courier_app.database import connection

from instance.config import Config


class SystemUsers(object):
    '''This class implements storage of SystemUsers'''

    def __init__(self, current_user_id):
        self.current_user_id = int(current_user_id)

    def add_user(self, username, email, phoneNo, password, role):
        '''This method adds a new user to the database'''
        try:
            con = connection()
            cur = con.cursor()
            insert_query = """ INSERT INTO sendit_users 
                (username, email, phone_number, role, password) 
                VALUES (%s,%s,%s,%s,%s)"""
            the_record = (username, email, phoneNo, role, 
                generate_password_hash(password))
            cur.execute(insert_query, the_record)
            con.commit()

            select_query = """select * from sendit_users where username = %s"""
            cur.execute(select_query, (username, ))
            record = cur.fetchone()

            cur.close()
            con.close()
            print("PostgreSQL connection is closed")

            out_data = {
                "user_id": record[0],
                "username": record[1],
                "email": record[2],
                "phone_number": record[3],
                "role": record[4]
            }
            return out_data

        except (Exception, psycopg2.Error) as error:
            cur.close()
            con.close()
            print("Failed to insert record into sendit_users table", error)
            print("PostgreSQL connection is closed")

    def _user_is_there(self):
        try:
            con = connection()
            cur = con.cursor()

            select_query = """select * from sendit_users where user_id = %s"""
            cur.execute(select_query, (self.current_user_id, ))
            record = cur.fetchone()

            # closing database connection.
            cur.close()
            con.close()
            print("PostgreSQL connection is closed")
            if record:
                out_data = {
                    "user_id": record[0],
                    "username": record[1],
                    "email": record[2],
                    "phone_number": record[3],
                    "role": record[4]
                }
                return out_data
            return False
        except (Exception, psycopg2.Error) as error:
            # closing database connection.
            cur.close()
            con.close()
            print("User failed to load", error)
            print("PostgreSQL connection is closed")
            return False

    def _fetch_db_user(self, user_id): 
        try:
            con = connection()
            cur = con.cursor()

            select_query = """select * from sendit_users where user_id = %s"""
            cur.execute(select_query, (user_id, ))
            record = cur.fetchone()
            cur.close()
            con.close()
            print("PostgreSQL connection is closed")
            if record:
                out_data = {
                    "user_id": record[0],
                    "username": record[1],
                    "email": record[2],
                    "phone_number": record[3],
                    "role": record[4],
                    "password": record[5]
                }
                return out_data
            return False
        except (Exception, psycopg2.Error) as error:
            cur.close()
            con.close()
            print("User failed to load", error)
            print("PostgreSQL connection is closed")
            return False
                
    def edit_user(self, user_id, username=None, email=None, phone_no=None,
                  password=None, role=None):
        '''This method allows current_user to edit his/her personal details and
        also allows an Admin to revoke a password. You pass in the user_id of 
        the user you want to edit and details of the specifics.'''
        this_user = self._user_is_there()
        if this_user:
            if this_user["user_id"] == int(user_id) or this_user["role"] == "Admin":
                if username:
                    try:
                        con = connection()
                        cur = con.cursor()
                        insert_query = """ Update sendit_users set username= %s
                            where user_id= %s"""
                        the_record = (username, user_id)
                        cur.execute(insert_query, the_record)
                        con.commit()
                        cur.close()
                        con.close()
                        print("PostgreSQL connection is closed")
                    except (Exception, psycopg2.Error) as error:
                        cur.close()
                        con.close()
                        print("Failed to update username.", error)
                        print("PostgreSQL connection is closed")

                if email:
                    try:
                        con = connection()
                        cur = con.cursor()
                        insert_query = """ Update sendit_users set email= %s
                            where user_id= %s"""
                        the_record = (email, user_id)
                        cur.execute(insert_query, the_record)
                        con.commit()
                        cur.close()
                        con.close()
                        print("PostgreSQL connection is closed")
                    except (Exception, psycopg2.Error) as error:
                        cur.close()
                        con.close()
                        print("Failed to update email.", error)
                        print("PostgreSQL connection is closed")

                if phone_no:
                    try:
                        con = connection()
                        cur = con.cursor()
                        insert_query = """ Update sendit_users set phone_number= %s
                            where user_id= %s"""
                        the_record = (phone_no, user_id)
                        cur.execute(insert_query, the_record)
                        con.commit()
                        cur.close()
                        con.close()
                        print("PostgreSQL connection is closed")
                    except (Exception, psycopg2.Error) as error:
                        cur.close()
                        con.close()
                        print("Failed to update phone_number.", error)
                        print("PostgreSQL connection is closed")

                if password:
                    try:
                        con = connection()
                        cur = con.cursor()
                        insert_query = """ Update sendit_users set password= %s
                            where user_id= %s"""
                        the_record = (generate_password_hash(password), 
                             user_id)
                        cur.execute(insert_query, the_record)
                        con.commit()
                        cur.close()
                        con.close()
                        print("PostgreSQL connection is closed")
                    except (Exception, psycopg2.Error) as error:
                        cur.close()
                        con.close()
                        print("Failed to update password.", error)
                        print("PostgreSQL connection is closed")

                if role:        
                    if this_user["role"] == "Admin":
                        try:
                            con = connection()
                            cur = con.cursor()
                            insert_query = """ Update sendit_users set role= %s
                                where user_id= %s"""
                            the_record = (role, user_id)
                            cur.execute(insert_query, the_record)
                            con.commit()
                            cur.close()
                            con.close()
                            print("PostgreSQL connection is closed")
                        except (Exception, psycopg2.Error) as error:
                            cur.close()
                            con.close()
                            print("Failed to update role.", error)
                            print("PostgreSQL connection is closed")
                    else:
                        return {"message":"UNAUTHORIZED<Field:'role'>"}
                        
                this_user = self._fetch_db_user(user_id)
                out_data = {
                    "message": "Authorized",
                    "user_id": this_user["user_id"],
                    "username": this_user["username"],
                    "email": this_user["email"],
                    "phone_number": this_user["phone_number"],
                    "role": this_user["role"]
                }
                return out_data
            return {"message": "UNAUTHORIZED"}
        return {"message": "UNAUTHORIZED"}

    def get_a_user(self, userid):
        '''This method returns a single user. It is only visible to Admin 
        and current user'''

        try:
            this_user = self._user_is_there()
            if this_user:
                if this_user["user_id"] == int(userid) or\
                    this_user["role"] == "Admin":
                    my_user = self._fetch_db_user(userid)
                    out_data = {
                        "message": "Authorized",
                        "user_id": my_user["user_id"],
                        "username": my_user["username"],
                        "email": my_user["email"],
                        "phone_number": my_user["phone_number"],
                        "role": my_user["role"]
                    }
                    return out_data
                return {"message": "UNAUTHORIZED"}
            return {"message": "UNKNOWN USER"}
        except:
            return {"message": "UNKNOWN USER"}

    def delete_a_user(self, userid):
        '''This method allows the admin to delete a single user.'''
        this_user = self._user_is_there()
        if this_user:
            if this_user["user_id"] == int(userid) or \
                    this_user["role"] == "Admin":
                try:
                    con = connection()
                    cur = con.cursor()
                    delete_query = """Delete from sendit_users where user_id= %s"""
                    cur.execute(delete_query, (int(userid), ))
                    con.commit()
                    cur.close()
                    con.close()
                    print("PostgreSQL connection is closed")
                        
                    return {"message": "DELETED"}
                    
                except (Exception, psycopg2.Error) as error:
                    print("Failed to delete user in db", error)
                    cur.close()
                    con.close()
                    print("PostgreSQL connection is closed")
                    return {"message": "User deletion failed"}
    
            return {"message": "UNAUTHORIZED"}
        return {"message": "UNAUTHORIZED"}

    def login_user(self, password, my_name):
        '''This method allows the admin to create a user'''
        try:
            con = connection()
            cur = con.cursor()

            select_query = """select * from sendit_users where username = %s"""
            cur.execute(select_query, (my_name, ))
            record = cur.fetchone()
            cur.close()
            con.close()
            print("PostgreSQL connection is closed")
            if record:
                out_data = {
                    "user_id": record[0],
                    "username": record[1],
                    "email": record[2],
                    "phone_number": record[3],
                    "role": record[4],
                    "password": record[5]
                }
                if check_password_hash(out_data["password"], password):
                    s = Serializer(Config.SECRET_KEY, expires_in=21600)
                    token = (s.dumps({'user_id': out_data["user_id"]})).decode("ascii")
                    out_data["token"] = token
                    return out_data
                else:
                     return False
            return False
        except (Exception, psycopg2.Error) as error:
            cur.close()
            con.close()
            print("User failed to load", error)
            print("PostgreSQL connection is closed")

    def get_all_users(self):
        this_user = self._user_is_there()
        if this_user and this_user["role"] == "Admin":
            reply = []
            try:
                con = connection()
                cur = con.cursor()

                select_query = """select * from sendit_users"""
                cur.execute(select_query)
                record = cur.fetchall()
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")

                for item in record:
                    my_user = self._fetch_db_user(item[0])
                    out_data = {
                        "message": "Authorized",
                        "user_id": my_user["user_id"],
                        "username": my_user["username"],
                        "email": my_user["email"],
                        "phone_number": my_user["phone_number"],
                        "role": my_user["role"]
                    }
                    reply.append(out_data)

            except (Exception, psycopg2.Error) as error:
                cur.close()
                con.close()
                print("Users failed to load", error)
                print("PostgreSQL connection is closed")

            return reply
        return {"message": "UNAUTHORIZED"}
