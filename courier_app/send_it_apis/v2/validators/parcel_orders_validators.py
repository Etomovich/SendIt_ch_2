from marshmallow import (Schema, fields, ValidationError,
        post_dump,post_load,validates, validates_schema)

from courier_app.send_it_apis.v2.models import (SendItUserOrders,
SendItParcels)
from courier_app.database import connection
import psycopg2 

class AddOrderSchema(Schema):
    parcel_id = fields.Integer(required=True)
    parcel_name = fields.String()
    parcel_description= fields.String()
    pay_mode= fields.String()
    pay_proof=fields.String()
    amount_paid=fields.String()
    destination= fields.String()

    @validates("amount_paid")
    def validate_amount_paid(self, amount_paid):
        try:
            value = float(amount_paid)
        except:
            raise ValidationError\
            ("[amount_paid] should be an integer string"+
            " i.e '3456' or float string i.e. '33445.657'")

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

        the_parcel101 = SendItParcels(0000)
        parcel_data = the_parcel101.db_parcel(parcel_id)
        if parcel_data and parcel_data["order_id"] != 0:
            raise ValidationError\
            ("[parcel_id] The Parcel ID already has an order. Try editing the order.") 

class EditOrderSchema(Schema):
    order_id = fields.Integer(required=True)
    parcel_name = fields.String()
    parcel_id= fields.String()
    pay_mode= fields.String()
    pay_proof=fields.String()
    amount_paid=fields.String()
    destination= fields.String()
    parcel_description = fields.String()
    submitted = fields.String()

    @validates("amount_paid")
    def validate_amount_paid(self, amount_paid):
        try:
            value = float(amount_paid)
        except:
            raise ValidationError\
            ("[amount_paid] should be an integer string"+
            " i.e '3456' or float string i.e. '33445.657'")

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


class OrderIdSchema(Schema):
    order_id = fields.Integer(required=True)

class ProcessOrderSchema(Schema):
    order_id = fields.Integer(required=True)
    order_status = fields.String(required = True)
    feedback = fields.String(required = True)
    approved = fields.String()

    @validates("order_status")
    def validate_order_status(self, order_status):
        accepted = ['accepted','rejected','unprocessed']
        if order_status not in accepted:
            raise ValidationError\
            ("[order_status] Order status can takeup one of "+
            " 'accepted', 'rejected' or 'unprocessed'")  
    
    @validates("approved")
    def validate_approved(self, approved):
        accepted = ["approved", "No"]
        if approved not in accepted:
            raise ValidationError\
            ( "The approved variable can either be: "+\
                "[approved, No]")  


