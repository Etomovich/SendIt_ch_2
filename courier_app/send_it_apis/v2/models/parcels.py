import uuid
import psycopg2
from datetime import datetime
from courier_app.database import connection

class SendItParcels(object):
    '''This class deals with storing user parcels.'''

    def __init__(self, current_user_id):
        self.current_user_id = int(current_user_id)

    def _user_is_there(self):
        from courier_app.send_it_apis.v2.models import SystemUsers
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

    def db_parcel(self, parcel_id):
        parcel_id = int(parcel_id)
        try:
            con = connection()
            cur = con.cursor()

            select_query = """select * from sendit_parcels where parcel_id = %s"""
            cur.execute(select_query, (parcel_id, ))
            record = cur.fetchone()

            # closing database connection.
            cur.close()
            con.close()
            print("PostgreSQL connection is closed")
            if record:
                out_data = {
                    "message": "CREATED",
                    "parcel_id": record[0],
                    "parcel_name": record[1],
                    "submission_station": record[2],
                    "present_location": record[3],
                    "weight": str(record[4]),
                    "expected_pay": str(record[5]),
                    "order_id": str(record[6]),
                    "feedback": record[7],
                    "destination": record[8],
                    "submission_date": str(record[9]),
                    "status": record[10],
                    "approved": record[11],
                    "owner_id": record[12],
                }
                return out_data
            return False
        except (Exception, psycopg2.Error) as error:
            # closing database connection.
            cur.close()
            con.close()
            print("Parcel failed to load", error)
            print("PostgreSQL connection is closed")
            return False

    def db_parcels_all(self, owner_id =None,status=None):
        '''This method returns all parcels'''
        reply = []
        try:
            con = connection()
            cur = con.cursor()
            select_query = ""
            record = ""

            if owner_id and status:
                select_query = """select * from sendit_parcels where owner_id = %s
                    and status = %s """
                cur.execute(select_query,(int(owner_id), status, ))
                record = cur.fetchall()
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")
            
            if owner_id and not status:
                select_query = """select * from sendit_parcels where owner_id = %s"""
                cur.execute(select_query,(int(owner_id),))
                record = cur.fetchall()
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")

            if not owner_id and status:
                select_query = """select * from sendit_parcels where status = %s"""
                cur.execute(select_query,(status,))
                record = cur.fetchall()
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")

            if not owner_id and not status:
                select_query = """select * from sendit_parcels"""
                cur.execute(select_query)
                record = cur.fetchall()
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")
            
            if not isinstance(record, str):
                for item in record:
                    out_data = {
                        "parcel_id": item[0],
                        "parcel_name": item[1],
                        "submission_station": item[2],
                        "present_location": item[3],
                        "weight": str(item[4]),
                        "expected_pay": str(item[5]),
                        "order_id": str(item[6]),
                        "feedback": item[7],
                        "destination": item[8],
                        "submission_date": str(item[9]),
                        "status": item[10],
                        "approved": item[11],
                        "owner_id": item[12],
                    }
                    reply.append(out_data)

            return reply
            
        except (Exception, psycopg2.Error) as error:
            cur.close()
            con.close()
            print("all parcels failed to load", error)
            print("PostgreSQL connection is closed")
            return False

    def db_my_approved(self, user_id, approved):
        '''This method returns all parcels'''
        reply = []
        try:
            con = connection()
            cur = con.cursor()
            select_query = ""
            record = ""

            select_query = """select * from sendit_parcels where owner_id = %s
                and approved = %s """
            cur.execute(select_query,(int(user_id), approved, ))
            record = cur.fetchall()
            cur.close()
            con.close()
            print("PostgreSQL connection is closed")
            
            if not isinstance(record, str):
                for item in record:
                    out_data = {
                        "parcel_id": item[0],
                        "parcel_name": item[1],
                        "submission_station": item[2],
                        "present_location": item[3],
                        "weight": str(item[4]),
                        "expected_pay": str(item[5]),
                        "order_id": str(item[6]),
                        "feedback": item[7],
                        "destination": item[8],
                        "submission_date": str(item[9]),
                        "status": item[10],
                        "approved": item[11],
                        "owner_id": item[12],
                    }
                    reply.append(out_data)

            return reply
            
        except (Exception, psycopg2.Error) as error:
            cur.close()
            con.close()
            print("all parcels failed to load", error)
            print("PostgreSQL connection is closed")
            return False

    def add_parcel(self,owner_id,parcel_name,weight,submission_station,\
                    present_location):
        '''This is an admin function that is activated when the customer 
        brings a parcel to a station and its details are taken by an ADMIN. 
        The client then leaves with a parcel_id. He/she is then required 
        to go make an order of where he/she wants the parcel to go and 
        prove payments are valid.'''
        this_user = self._user_is_there()
        
        if this_user and this_user['role'] == "Admin":
            try:
                con = connection()
                cur = con.cursor()
                #default values
                expected_pay = 0.0
                order_id = 0
                feedback = ""
                destination=""
                submission_date = datetime.utcnow()
                status="not_started"
                approved="No"

                insert_query = """INSERT INTO sendit_parcels 
                    (parcel_name, submission_station, present_location,
                    weight, expected_pay,order_id,feedback,destination,submission_date,
                    status,approved, owner_id) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""" 
                 
                the_record = (parcel_name, submission_station, present_location,weight,
                     expected_pay,order_id,feedback,destination,submission_date,
                     status,approved, owner_id)
                cur.execute(insert_query, the_record)
                
                con.commit()

                select_query = """select * from sendit_parcels where parcel_name = %s"""
                cur.execute(select_query, (parcel_name, ))
                record = cur.fetchone()

                cur.close()
                con.close()
                print("PostgreSQL connection is closed")

                out_data = {
                    "message": "CREATED",
                    "parcel_id": record[0],
                    "parcel_name": record[1],
                    "submission_station": record[2],
                    "present_location": record[3],
                    "weight": str(record[4]),
                    "expected_pay": str(record[5]),
                    "order_id": str(record[6]),
                    "feedback": record[7],
                    "destination": record[8],
                    "submission_date": str(record[9]),
                    "status": record[10],
                    "approved": record[11],
                    "owner_id": record[12],
                }
                return out_data

            except (Exception, psycopg2.Error) as error:
                cur.close()
                con.close()
                print("Failed to insert record into sendit_parcels table", error)
                print("PostgreSQL connection is closed")

                reply = {}
                reply["message"] = "An error has occured the administrator has been informed"
                return reply

        return {"message":"UNAUTHORIZED"}

    def edit_parcel(self,parcel_id,parcel_name=None,weight=None,
            destination=None, expected_pay=None,submission_station=None,
            feedback=None, order_id=None, owner_id=None,
            present_location=None, status=None, approved = None):
        '''This method allows an admin to edit a parcel.'''
        parcel_id = int(parcel_id)
        this_user = self._user_is_there()
        if this_user and this_user['role'] == "Admin":
            if parcel_name:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_parcels set parcel_name= %s
                        where parcel_id= %s"""
                    the_record = (parcel_name, parcel_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update parcel_name.", error)
                    print("PostgreSQL connection is closed")

            if approved:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_parcels set approved= %s
                        where parcel_id= %s"""
                    the_record = (approved, parcel_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update approved.", error)
                    print("PostgreSQL connection is closed")

            if weight:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_parcels set weight= %s
                        where parcel_id= %s"""
                    the_record = (weight, parcel_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update weight.", error)
                    print("PostgreSQL connection is closed")

            if destination:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_parcels set destination= %s
                        where parcel_id= %s"""
                    the_record = (destination, parcel_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update destination.", error)
                    print("PostgreSQL connection is closed")

            if expected_pay:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_parcels set expected_pay= %s
                        where parcel_id= %s"""
                    the_record = (expected_pay, parcel_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update expected_pay.", error)
                    print("PostgreSQL connection is closed")

            if submission_station:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_parcels set submission_station= %s
                        where parcel_id= %s"""
                    the_record = (submission_station, parcel_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update submission_station.", error)
                    print("PostgreSQL connection is closed")
                
            if feedback:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_parcels set feedback= %s
                        where parcel_id= %s"""
                    the_record = (feedback, parcel_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update feedback.", error)
                    print("PostgreSQL connection is closed")

            if order_id:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_parcels set order_id= %s
                        where parcel_id= %s"""
                    the_record = (order_id, parcel_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update order_id.", error)
                    print("PostgreSQL connection is closed")

            if owner_id:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_parcels set owner_id= %s
                        where parcel_id= %s"""
                    the_record = (owner_id, parcel_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update owner_id.", error)
                    print("PostgreSQL connection is closed")

            if present_location:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_parcels set present_location= %s
                        where parcel_id= %s"""
                    the_record = (present_location, parcel_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update present_location.", error)
                    print("PostgreSQL connection is closed")

            if status:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_parcels set status= %s
                        where parcel_id= %s"""
                    the_record = (status, parcel_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update status.", error)
                    print("PostgreSQL connection is closed")
    
            payload = self.db_parcel(parcel_id)
            payload["message"] = "EDITED"
            return payload

        return {"message":"UNAUTHORIZED"} 

    def change_destination(self,parcel_id,destination):
        '''This method allows an admin to edit a parcel.'''
        parcel_id = int(parcel_id)
        this_user = self._user_is_there()
        this_parcel = self.db_parcel(parcel_id)
        if (this_user and this_user['role'] == "User"
        and this_user["user_id"] == this_parcel["owner_id"]):
            try:
                con = connection()
                cur = con.cursor()
                insert_query = """ Update sendit_parcels set destination= %s
                    where parcel_id= %s"""
                the_record = (destination, parcel_id)
                cur.execute(insert_query, the_record)
                con.commit()
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")
                payload = self.db_parcel(parcel_id)
                payload["message"] = "Destination Change"
                return payload
            except (Exception, psycopg2.Error) as error:
                cur.close()
                con.close()
                print("Failed to update destination.", error)
                print("PostgreSQL connection is closed")
                return {
                    "message":"Failed to change destination."
                }
        return {"message":"UNAUTHORIZED"}

    def user_cancels_delivery(self, parcel_id):
        '''This method implements a user cancelling a delivery. It is 
        assumed that the current_user is the user making the action.'''
        this_user = self._user_is_there()
        this_parcel = self.db_parcel(int(parcel_id))
        if this_user["user_id"]== this_parcel["owner_id"]:
            #cancel parcel
            try:
                con = connection()
                cur = con.cursor()
                status = "cancelled"
                insert_query = """ Update sendit_parcels set status= %s
                        where parcel_id= %s"""
                the_record = (status, parcel_id)
                cur.execute(insert_query, the_record)
                con.commit()
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")
            except (Exception, psycopg2.Error) as error:
                cur.close()
                con.close()
                print("Failed to update status.", error)
                print("PostgreSQL connection is closed")
            
            payload = self.db_parcel(parcel_id)
            return {
                "message":"cancelled",
                "Cancelled Parcel": payload
            }

        return {"message":"UNAUTHORIZED"}        

    def get_all_parcels(self):
        '''This method returns all parcels in the system which makes it an 
        admin function.'''
        this_user = self._user_is_there()
        if this_user and this_user['role'] == "Admin":
            reply = []
            try:
                con = connection()
                cur = con.cursor()

                select_query = """select * from sendit_parcels"""
                cur.execute(select_query)
                record = cur.fetchall()
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")

                for item in record:
                    out_data = {
                        "parcel_id": item[0],
                        "parcel_name": item[1],
                        "submission_station": item[2],
                        "present_location": item[3],
                        "weight": str(item[4]),
                        "expected_pay": str(item[5]),
                        "order_id": str(item[6]),
                        "feedback": item[7],
                        "destination": item[8],
                        "submission_date": str(item[9]),
                        "status": item[10],
                        "approved": item[11],
                        "owner_id": item[12],
                    }
                    reply.append(out_data)

                return reply
            
            except (Exception, psycopg2.Error) as error:
                cur.close()
                con.close()
                print("all parcels failed to load", error)
                print("PostgreSQL connection is closed")
            

        return {"message":"UNAUTHORIZED"}



    def delete_parcel(self, parcel_id):
        '''This method deletes a parcels in the system which makes it an 
        admin function. A user can only cancel a parcel delivery order'''
        this_user = self._user_is_there()
        if this_user and this_user['role'] == "Admin":
            try:
                con = connection()
                cur = con.cursor()
                delete_query = """Delete from sendit_parcels where parcel_id= %s"""
                cur.execute(delete_query, (int(parcel_id), ))
                con.commit()
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")
                       
                return {"message": "deleted"}
                   
            except (Exception, psycopg2.Error) as error:
                print("Failed to delete parcel in db", error)
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")
                return {"message": "Parcel deletion failed"}
    
        return {"message":"UNAUTHORIZED"}

    def get_parcel(self, parcel_id):
        '''This method is only available to the admin and user who delivered
        the parcel.[current_user]'''
        this_user = self._user_is_there()
        this_parcel = self.db_parcel(int(parcel_id))
        if this_user and (this_user['role']\
            == "Admin" or this_user['user_id'] == this_parcel['owner_id']):
            payload= self.db_parcel(int(parcel_id))
            payload["message"] = "FOUND"
            return payload
        return {"message":"UNAUTHORIZED"}

    def get_all_my_parcels(self, user_id):
        '''This method is only available to the admin and user who delivered
        the parcel.[current_user]'''
        this_user = self._user_is_there()

        if this_user:
            reply = self.db_parcels_all(owner_id=int(user_id))
            if reply and (reply[0]["owner_id"] == this_user["user_id"] or
                this_user["role"] == "Admin"):
                return reply
        return {"message":"UNAUTHORIZED"}
    
    def get_my_approved_parcels(self,user_id):
        '''This method is only available to the admin and user who delivered
        the parcel.[current_user]'''
        this_user = self._user_is_there()
        if this_user:
            reply = self.db_my_approved(user_id=int(user_id),approved="approved")
            if reply and (reply[0]["owner_id"] == this_user["user_id"] or
                this_user["role"] == "Admin"):
                return reply
            return []
        return {"message":"UNAUTHORIZED"}
        
    def get_my_notstarted_parcels(self, user_id):
        '''This method is only available to the admin and user who delivered
        the parcel.[current_user]'''
        this_user = self._user_is_there()
        if this_user:
            reply = self.db_parcels_all(owner_id=int(user_id),status="not_started")
            if reply and (reply[0]["owner_id"] == this_user["user_id"] or
                this_user["role"] == "Admin"):
                return reply
            return []
        return {"message":"UNAUTHORIZED"}

    def get_my_intransit_parcels(self, user_id):
        '''This method is only available to the admin and user who delivered
        the parcel.[current_user]'''
        this_user = self._user_is_there()
        if this_user:
            reply = self.db_parcels_all(owner_id=int(user_id),status="in_transit")
            if reply and (reply[0]["owner_id"] == this_user["user_id"] or
                this_user["role"] == "Admin"):
                return reply
            return []
        return {"message":"UNAUTHORIZED"}
 
    def get_my_cancelled_parcels(self,user_id):
        '''This method is only available to the admin and user who delivered
        the parcel.[current_user]'''
        this_user = self._user_is_there()
        if this_user:
            reply = self.db_parcels_all(owner_id=int(user_id),status="cancelled")
            if reply and (reply[0]["owner_id"] == this_user["user_id"] or
                this_user["role"] == "Admin"):
                return reply
            return []
        return {"message":"UNAUTHORIZED"}

    def get_my_delivered_parcels(self, user_id):
        '''This method is only available to the admin and user who delivered
        the parcel.[current_user]'''
        this_user = self._user_is_there()
        if this_user:
            reply = self.db_parcels_all(owner_id=int(user_id),status="delivered")
            if reply and (reply[0]["owner_id"] == this_user["user_id"] or
                this_user["role"] == "Admin"):
                return reply
            return []
        return {"message":"UNAUTHORIZED"}


