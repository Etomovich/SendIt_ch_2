import uuid
import psycopg2
from datetime import datetime
from courier_app.database import connection

class SendItUserOrders(object):
    '''This class implements storage of System user orders'''  

    def __init__(self, current_user_id):
        self.current_user_id = str(int(current_user_id)) 

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

    def db_order(self, order_id):
        order_id = int(order_id)
        try:
            con = connection()
            cur = con.cursor()

            select_query = """select * from sendit_orders where order_id = %s"""
            cur.execute(select_query, (order_id, ))
            record = cur.fetchone()

            # closing database connection.
            cur.close()
            con.close()
            print("PostgreSQL connection is closed")
            if record:
                out_data = {
                    "order_id": record[0],
                    "parcel_name": record[1],
                    "parcel_description": record[2],
                    "pay_mode": record[3],
                    "pay_proof": record[4],
                    "amount_paid": str(record[5]),
                    "destination": record[6],
                    "submitted": record[7],
                    "order_status": record[8],
                    "feedback": str(record[9]),
                    "owner_id": record[10],
                    "parcel_id": record[11]
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

    def add_order(self,parcel_id,parcel_name=None,parcel_description=None,pay_mode=None,
                            pay_proof=None,amount_paid=None,destination=None):
        '''This method allows a user to make an order. '''        
        this_user = self._user_is_there()

        ##Check parcel id owner is the one creating the order. Else raise 
        #an error 'You are not the owner of this parcel!!'
        is_parcel_owner = False
        from courier_app.send_it_apis.v2.models import SendItParcels
        parc = SendItParcels(0000)
        parcel_info = parc.db_parcel(int(parcel_id))
        if parcel_info:
            if parcel_info["approved"] == "approved":
                reply = {}
                reply["Status"] = "bad"
                reply["message"] = 'This parcel has already been processed and accepted!!'
                return reply

            if parcel_info["owner_id"] == this_user["user_id"]:
                is_parcel_owner = True
            
            if not is_parcel_owner:
                reply = {}
                reply["Status"] = "bad"
                reply["message"] = 'You are not the owner of this parcel!!'
                return reply

        if this_user and is_parcel_owner:
            try:
                con = connection()
                cur = con.cursor()

                #default values
                payload = {
                    "owner_id": this_user["user_id"],#CG
                    "parcel_id": int(parcel_id),
                    "parcel_name":parcel_name if \
                                         parcel_name else "",
                    "parcel_description": parcel_description if \
                                         parcel_description else "",
                    "pay_mode":pay_mode if pay_mode else "",
                    "pay_proof": pay_proof if pay_proof else "",
                    "amount_paid": float(amount_paid) if amount_paid else 0.0,
                    "destination": destination if destination else "",
                    "submitted": "False",#u
                    "order_status": "unprocessed",#A
                    "feedback":""#A
                }

                insert_query = """INSERT INTO sendit_orders 
                    (parcel_name, parcel_description, pay_mode,pay_proof,
                    amount_paid, destination,submitted,order_status,
                    feedback,owner_id, parcel_id) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                 
                the_record = (payload["parcel_name"], payload["parcel_description"],
                    payload["pay_mode"],payload["pay_proof"],
                    payload["amount_paid"], payload["destination"],
                    payload["submitted"],payload["order_status"],
                    payload["feedback"],payload["owner_id"], 
                    payload["parcel_id"])
                cur.execute(insert_query, the_record)
                
                con.commit()

                select_query = """select * from sendit_orders where parcel_id = %s"""
                cur.execute(select_query, (parcel_id, ))
                record = cur.fetchone()

                cur.close()
                con.close()
                print("PostgreSQL connection is closed")

                out_data = {
                    "message": "CREATED",
                    "order_id": record[0],
                    "parcel_name": record[1],
                    "parcel_description": record[2],
                    "pay_mode": record[3],
                    "pay_proof": record[4],
                    "amount_paid": str(record[5]),
                    "destination": record[6],
                    "submitted": record[7],
                    "order_status": record[8],
                    "feedback": str(record[9]),
                    "owner_id": record[10],
                    "parcel_id": record[11]
                }
                return out_data

            except (Exception, psycopg2.Error) as error:
                cur.close()
                con.close()
                print("Failed to insert record into sendit_orders table", error)
                print("PostgreSQL connection is closed")

                reply = {}
                reply["Status"] = "bad"
                reply["message"] = "An error has occured the administrator has been informed"
                return reply
       
        return {"message":"UNKNOWN USER or INVALID PARCEL ID"}

    def edit_order_user(self,order_id,parcel_id=None,parcel_name=None,
        parcel_description=None,pay_mode=None,pay_proof=None,
        amount_paid=None,destination=None,submitted=False):
        '''This method allows the owner of <order_id> to edit the order's details.
        NB: If the order is accepted you cannot edit.'''
        this_user = self._user_is_there()
        this_order = self.db_order(int(order_id))
        check_for_change = False
        if not this_user:
            reply = {}
            reply["Status"] = "bad"
            reply["message"] = "Please sign in or create a SendIt account"+\
                "to use the system."
            return reply
        if (this_user["user_id"]== this_order["owner_id"]):
            if parcel_id:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_orders set parcel_id= %s
                        where order_id= %s"""
                    the_record = (parcel_id, order_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    check_for_change = True
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update parcel_id.", error)
                    print("PostgreSQL connection is closed")

            if parcel_name:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_orders set parcel_name= %s
                        where order_id= %s"""
                    the_record = (parcel_name, order_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    check_for_change = True
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update parcel_name.", error)
                    print("PostgreSQL connection is closed")
            
            if parcel_description:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_orders set parcel_description= %s
                        where order_id= %s"""
                    the_record = (parcel_description, order_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    check_for_change = True
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update parcel_description.", error)
                    print("PostgreSQL connection is closed")

            if pay_mode:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_orders set pay_mode= %s
                        where order_id= %s"""
                    the_record = (pay_mode, order_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    check_for_change = True
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update pay_mode.", error)
                    print("PostgreSQL connection is closed")

            if pay_proof:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_orders set pay_proof= %s
                        where order_id= %s"""
                    the_record = (pay_proof, order_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    check_for_change = True
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update pay_proof.", error)
                    print("PostgreSQL connection is closed")

            if amount_paid:
                amount_paid = float(amount_paid)
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_orders set amount_paid= %s
                        where order_id= %s"""
                    the_record = (amount_paid, order_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    check_for_change = True
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update amount_paid.", error)
                    print("PostgreSQL connection is closed")

            if destination:
                try:
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_orders set destination= %s
                        where order_id= %s"""
                    the_record = (destination, order_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    check_for_change = True
                    print("PostgreSQL connection is closed")
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update amount_paid.", error)
                    print("PostgreSQL connection is closed")
            
            if submitted:
                expected = ("Yes","y","Y","YES","yes",)
                if submitted not in expected:
                    message={}
                    message["Status"] = "bad"
                    message["message"] = "Submitted can be filled by one of:"+\
                        "[Yes,y,Y,YES,yes]. To remove submission check mannual."
                    return message
                this_order = self.db_order(int(order_id))
                if ((len(this_order['parcel_description']) != 0) and
                    (len(this_order['pay_mode']) != 0) and
                    (len(this_order['pay_proof']) != 0) and
                    (this_order['amount_paid'] != 0.0) and
                    (len(this_order['destination']) != 0)):
                    try:
                        con = connection()
                        cur = con.cursor()
                        insert_query = """ Update sendit_orders set submitted= %s
                            where order_id= %s"""
                        submitted = "True"
                        the_record = (submitted, int(order_id))
                        cur.execute(insert_query, the_record)
                        con.commit()
                        cur.close()
                        con.close()
                        check_for_change = True
                        print("PostgreSQL connection is closed")
                    except (Exception, psycopg2.Error) as error:
                        cur.close()
                        con.close()
                        print("Failed to update amount_paid.", error)
                        print("PostgreSQL connection is closed")
                
                else:
                    return {
                        "Status": "bad",
                        "message":"Fill fields[parcel_description,"+\
                        "pay_mode, pay_proof,amount_paid,"+\
                        "destination] before submitting.",
                        "Submit":"Submission Rejected"}

            this_order = self.db_order(int(order_id))
            if not check_for_change:
                reply={}
                reply["Status"] = "bad"
                reply["fields"] = "A user can change the following fields: "+\
                    "[parcel_id,parcel_description,pay_mode,pay_proof, amount_paid"+\
                    ",destination,submitted]" 
                reply["message"] = "The required fields have not been changed!!"
                return reply
            if this_order:
                reply = {}
                reply["Status"] = "OK"
                this_order["message"] = "EDITED"
                return this_order
            reply = {}
            reply["Status"] = "bad"
            reply["message"] = "The order is not found."
            return reply        
        reply = {}
        reply["Status"] = "unauthorized"
        reply["message"] = "You are not the owner of this order."
        return reply 

    def remove_submission(self, order_id):
        '''This method allows a user to remove a submission.
        This method is useful if a user has made a premature submission
        or order has been rejected and wants to redo the order. NB: if
        the order is accepted you cannot remove submission''' 

        this_user = self._user_is_there()
        this_order = self.db_order(int(order_id))
        if this_user and (this_user["user_id"]== this_order["owner_id"]):
            if (this_order["order_status"] =="unprocessed" or
                this_order["order_status"] == "rejected"):
                try:
                    if this_order["submitted"] == "False":
                        reply  = {}
                        reply["Status"] = "bad"
                        reply["message"] = "This order is yet to be submitted."
                        return reply
                    con = connection()
                    cur = con.cursor()
                    insert_query = """ Update sendit_orders set submitted= %s
                        where order_id= %s"""
                    submitted = "False"
                    the_record = (submitted, order_id)
                    cur.execute(insert_query, the_record)
                    con.commit()
                    cur.close()
                    con.close()
                    print("PostgreSQL connection is closed")
                    reply = self.db_order(int(order_id))
                    reply["message"] = "Submission Removed"
                    return reply
                except (Exception, psycopg2.Error) as error:
                    cur.close()
                    con.close()
                    print("Failed to update submitted.", error)
                    print("PostgreSQL connection is closed")
                    reply["message"] = "Internal Error: Error removing submission."
                    return reply

            reply = {}
            reply["Status"] = "bad"
            reply["message"] = "Submission could not be removed!! The order cannot"+\
                "be altered because it has already been processed and accepted."
            return reply
        reply = {}
        reply["Status"] = "bad"
        reply["message"] = "You are not the owner of this order!!"        
        return reply
    
    def process_order(self,order_id,order_status,feedback,approved=False):
        '''This method allows the admin to process user order data'''
        this_user = self._user_is_there()
        this_order = self.db_order(int(order_id))
        if this_user and this_user["role"] == "Admin":
            try:
                con = connection()
                cur = con.cursor()
                insert_query = """ Update sendit_orders set order_status= %s
                    where order_id= %s"""
            
                the_record = (order_status, order_id)
                cur.execute(insert_query, the_record)

                insert_query = """ Update sendit_orders set feedback= %s
                    where order_id= %s"""
                the_record = (feedback, order_id)
                cur.execute(insert_query, the_record)

                if approved:
                    insert_query = """ Update sendit_parcels set approved= %s
                        where parcel_id= %s"""               
                    the_record = (str(approved), this_order["parcel_id"])
                    cur.execute(insert_query, the_record)

                    insert_query = """ Update sendit_parcels set destination= %s
                        where parcel_id= %s"""               
                    the_record = (this_order["destination"], this_order["parcel_id"])
                    cur.execute(insert_query, the_record)

                    insert_query = """ Update sendit_parcels set order_id= %s
                        where parcel_id= %s"""               
                    the_record = (this_order["order_id"], this_order["parcel_id"])
                    cur.execute(insert_query, the_record)

                con.commit()
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")
                reply = {}
                reply = self.db_order(int(order_id))
                reply["Status"] = "OK"
                reply["message"] = "Order proccessed."
                return reply

            except (Exception, psycopg2.Error) as error:
                cur.close()
                con.close()
                print("Failed to update order_status.", error)
                print("PostgreSQL connection is closed")
                reply = {}
                reply["Status"] = "Error"
                reply["message"] = "An Error has occured the admin has been notified"
                return reply

        answer = {}
        answer["Status"] = "UNAUTHORIZED"
        answer["message"] = "You are not allowed to process order. This is an admin function."
        return answer

    def return_all_orders(self):
        '''This is an admin method to return all orders in the system.'''
        this_user = self._user_is_there()
        if this_user and this_user["role"] == "Admin":
            reply = []
            try:
                con = connection()
                cur = con.cursor()
                insert_query = """ select * from sendit_orders"""
                cur.execute(insert_query)
                record = cur.fetchall()
                con.commit()
                cur.close()
                con.close()
                for thing in record:
                    out_data = {
                        "order_id": thing[0],
                        "parcel_name": thing[1],
                        "parcel_description": thing[2],
                        "pay_mode": thing[3],
                        "pay_proof": thing[4],
                        "amount_paid": str(thing[5]),
                        "destination": thing[6],
                        "submitted": thing[7],
                        "order_status": thing[8],
                        "feedback": str(thing[9]),
                        "owner_id": thing[10],
                        "parcel_id": thing[11]
                    }
                    reply.append(out_data)
                print("PostgreSQL connection is closed")
            except (Exception, psycopg2.Error) as error:
                cur.close()
                con.close()
                print("Failed to update order_status.", error)
                print("PostgreSQL connection is closed")
            return reply        
        return {"message":"UNAUTHORIZED"}
    
    def return_all_unprocessed_orders(self):
        '''This is an admin method to return all 
        unprocessed orders in the system.'''
        this_user = self._user_is_there()
        if this_user and this_user["role"] == "Admin":
            reply = []

            try:
                con = connection()
                cur = con.cursor()
                insert_query = """ select * from sendit_orders where order_status = %s"""
                cur.execute(insert_query,("unprocessed",))
                record = cur.fetchall()
                con.commit()
                cur.close()
                con.close()
                print(record)
                for thing in record:
                    out_data = {
                        "order_id": thing[0],
                        "parcel_name": thing[1],
                        "parcel_description": thing[2],
                        "pay_mode": thing[3],
                        "pay_proof": thing[4],
                        "amount_paid": str(thing[5]),
                        "destination": thing[6],
                        "submitted": thing[7],
                        "order_status": thing[8],
                        "feedback": str(thing[9]),
                        "owner_id": thing[10],
                        "parcel_id": thing[11]
                    }
                    reply.append(out_data)
                print("PostgreSQL connection is closed")
                return reply
            except (Exception, psycopg2.Error) as error:
                cur.close()
                con.close()
                print("Failed to fetch unprocessed parcels", error)
                print("PostgreSQL connection is closed")
            return reply        
        return {"message":"UNAUTHORIZED"}

    def return_an_order(self, order_id):
        '''This method is an admin method to fetch a single order'''
        this_user = self._user_is_there()
        if this_user and (this_user["role"] == "Admin"):
            the_order = self.db_order(int(order_id))
            if the_order:
                the_order["message"] = "FOUND"
                return the_order
            return {"message":"ORDER NOT FOUND"}        
        return {"message":"UNAUTHORIZED"}

    def return_my_order(self, order_id):
        '''This method is a user method to fetch a single order from
        his/her list of orders'''
        this_user = self._user_is_there()
        the_order = self.db_order(int(order_id))
        if (this_user and the_order and
        (this_user["user_id"] == the_order["owner_id"])):
            the_order["message"] = "FOUND"
            return the_order        
        return {"message":"UNAUTHORIZED"}

    def user_order_deletion(self, order_id):
        '''This method allows a user to delete an order that has been
        rejected or yet to be processed'''
        this_user = self._user_is_there()
        the_order = self.db_order(int(order_id))
        if (this_user and the_order and
        (this_user["user_id"] == the_order["owner_id"])):
            try:
                con = connection()
                cur = con.cursor()
                delete_query = """Delete from sendit_orders where order_id= %s"""
                cur.execute(delete_query, (int(order_id), ))
                con.commit()
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")
                       
                return {"message": "DELETED"}
                   
            except (Exception, psycopg2.Error) as error:
                print("Failed to delete parcel in db", error)
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")
                return {"message": "Order deletion failed"}

        return {"message":"UNAUTHORIZED"}

    def admin_order_deletion(self, order_id):
        '''This method allows an administrator to delete an order.'''
        this_user = self._user_is_there()
        the_order = self.db_order(int(order_id))
        if this_user and the_order and this_user["role"] == "Admin":
            try:
                con = connection()
                cur = con.cursor()
                delete_query = """Delete from sendit_orders where order_id= %s"""
                cur.execute(delete_query, (int(order_id), ))
                con.commit()
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")
                       
                return {"message": "DELETED"}
                   
            except (Exception, psycopg2.Error) as error:
                print("Failed to delete parcel in db", error)
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")
                return {"message": "Order deletion failed"}
       
        return {"message":"UNAUTHORIZED"}

    def my_processed_orders(self,user_id):
        '''This method allows a user to get his/her list of 
        processed orders.'''
        this_user = self._user_is_there()
        if this_user and (this_user["role"] == "Admin" or \
            this_user["user_id"] == int(user_id)):
            reply = []
            try:
                con = connection()
                cur = con.cursor()
                insert_query = """ select * from sendit_orders where 
                order_status= %s and owner_id = %s"""
                cur.execute(insert_query,("accepted",int(user_id),))
                record = cur.fetchall()
                con.commit()
                cur.close()
                con.close()
                for thing in record:
                    out_data = {
                        "order_id": thing[0],
                        "parcel_name": thing[1],
                        "parcel_description": thing[2],
                        "pay_mode": thing[3],
                        "pay_proof": thing[4],
                        "amount_paid": str(thing[5]),
                        "destination": thing[6],
                        "submitted": thing[7],
                        "order_status": thing[8],
                        "feedback": str(thing[9]),
                        "owner_id": thing[10],
                        "parcel_id": thing[11]
                    }
                    reply.append(out_data)
                print("PostgreSQL connection is closed")
            except (Exception, psycopg2.Error) as error:
                cur.close()
                con.close()
                print("Failed to update order_status.", error)
                print("PostgreSQL connection is closed")
            return reply 
        return {"message":"UNAUTHORIZED"}

    def my_unprocessed_orders(self, user_id):
        '''This method allows a user to get his/her list of 
        unprocessed orders.'''
        this_user = self._user_is_there()
        if this_user and (this_user["role"] == "Admin" or \
            this_user["user_id"] == int(user_id)):
            reply = []
            try:
                con = connection()
                cur = con.cursor()
                insert_query = """ select * from sendit_orders where 
                order_status= %s and owner_id = %s"""
                cur.execute(insert_query,("unprocessed",int(user_id),))
                record = cur.fetchall()
                con.commit()
                cur.close()
                con.close()
                for thing in record:
                    out_data = {
                        "order_id": thing[0],
                        "parcel_name": thing[1],
                        "parcel_description": thing[2],
                        "pay_mode": thing[3],
                        "pay_proof": thing[4],
                        "amount_paid": str(thing[5]),
                        "destination": thing[6],
                        "submitted": thing[7],
                        "order_status": thing[8],
                        "feedback": str(thing[9]),
                        "owner_id": thing[10],
                        "parcel_id": thing[11]
                    }
                    reply.append(out_data)
                print("PostgreSQL connection is closed")
            except (Exception, psycopg2.Error) as error:
                cur.close()
                con.close()
                print("Failed to update order_status.", error)
                print("PostgreSQL connection is closed")
            return reply 
        return {"message":"UNAUTHORIZED"}

