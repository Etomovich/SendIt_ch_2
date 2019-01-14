from marshmallow import (Schema, fields, ValidationError,
        post_dump,post_load,validates, validates_schema)

from courier_app.send_it_apis.v2.models import (
        SendItParcels, SystemUsers)
from courier_app.database import connection
import psycopg2 

class AddParcelSchema(Schema):
    owner_id = fields.Integer(required=True)
    weight= fields.String(required=True)
    parcel_name = fields.String(required=True)
    submission_station=fields.String(required=True)
    present_location=fields.String(required=True)

    @validates("owner_id")
    def validate_owner(self, owner_id):
        con = connection()
        cur = con.cursor()

        select_query = """select * from sendit_users where user_id= %s """
        cur.execute(select_query,(int(owner_id),))
        record = cur.fetchone()

        cur.close()
        con.close()
        if  not record:
            raise ValidationError\
            ("[owner_id] The owner does not exist in the system.")


    @validates("weight")
    def validate_weight(self, weight):
        try:
            value = float(weight)
        except:
            raise ValidationError\
            ("[weight] should be an integer string"+
            " i.e '3456' or float string i.e. '33445.657'")

class EditParcelSchema(Schema):
    parcel_id = fields.Integer(required=True)
    parcel_name = fields.String()
    weight= fields.String()
    destination=fields.String()
    expected_pay=fields.String()
    submission_station=fields.String()
    feedback=fields.String()
    order_id=fields.String()
    owner_id=fields.String()
    present_location=fields.String()
    status=fields.String()
    approved=fields.String()

    @validates("parcel_id")
    def validate_parcel_id(self,parcel_id):
        con = connection()
        cur = con.cursor()

        select_query = """select * from sendit_parcels where parcel_id= %s """
        cur.execute(select_query,(int(parcel_id),))
        record = cur.fetchone()

        cur.close()
        con.close()
        if  not record:
            raise ValidationError\
            ("[parcel_id] The Parcel ID does not exist.")


    @validates("owner_id")
    def validate_owner(self, owner_id):
        con = connection()
        cur = con.cursor()

        select_query = """select * from sendit_users where user_id= %s"""
        cur.execute(select_query,(int(owner_id),))
        record = cur.fetchone()

        cur.close()
        con.close()
        if  not record:
            raise ValidationError\
            ("[owner_id] The owner does not exist in the system.")


    @validates("weight")
    def validate_weight(self, weight):
        try:
            value = float(weight)
        except:
            raise ValidationError\
            ("[weight] should be an integer string"+
            " i.e '3456' or float string i.e. '33445.657'")

    @validates("order_id")
    def validate_order_id(self, order_id):
        con = connection()
        cur = con.cursor()

        select_query = """select * from sendit_orders where order_id= %s """
        cur.execute(select_query,(int(order_id),))
        record = cur.fetchone()

        cur.close()
        con.close()
        if  not record:
            raise ValidationError\
            ("[order_id] The order_id does not exist.")
        

    @validates("expected_pay")
    def validate_expected_pay(self, expected_pay):
        try:
            value = float(expected_pay)
        except:
            raise ValidationError\
            ("[expected_pay] should be an integer string"+
            " i.e '3456' or float string i.e. '33445.657'")

    @validates("status")
    def validate_status(self, status):
        accepted = ['in_transit','not_started','delivered','cancelled']
        if status not in accepted:
            raise ValidationError\
            ("[status] Parcel status can takeup one of 'not_started'"+
            " 'in_transit', 'cancelled' or 'delivered'")

    @validates("approved")
    def validate_approved(self, approved):
        accepted = ['approved','No',]
        if approved not in accepted:
            raise ValidationError\
            ("[status] Order status can takeup one of 'approved','No'")

class ParcelIdSchema(Schema):
    parcel_id = fields.Integer(required=True)

    @validates("parcel_id")
    def validate_parcel_id(self,parcel_id):
        con = connection()
        cur = con.cursor()

        select_query = """select * from sendit_parcels where parcel_id= %s """
        cur.execute(select_query,(int(parcel_id),))
        record = cur.fetchone()

        cur.close()
        con.close()
        if  not record:
            raise ValidationError\
            ("[parcel_id] The Parcel ID does not exist.") 

class UserIdSchema(Schema):
    user_id = fields.Integer(required=True)

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


