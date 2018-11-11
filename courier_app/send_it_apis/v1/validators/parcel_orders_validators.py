from marshmallow import Schema, fields, ValidationError,\
        post_dump,post_load,validates, validates_schema

from courier_app.send_it_apis.v1.models import SendItUserOrders,SendItParcels

class AddOrderSchema(Schema):
    parcel_id = fields.Integer(required=True)
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
        try:
            value = SendItParcels.sendit_parcels[(str(parcel_id))]
            if value["order_id"]!= "":
                raise ValidationError\
                ("[parcel_id] This parcel has another order to "+
                "a different destination. Please delete order "+value["order_id"]+
                " if it has not been processed.")
        except:
            raise ValidationError\
            ("[parcel_id] The Parcel ID does not exist.")

class EditOrderSchema(Schema):
    order_id = fields.Integer(required=True)
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
        try:
            value = SendItParcels.sendit_parcels[(str(parcel_id))]
            if value["order_id"]!= "":
                raise ValidationError\
                ("[parcel_id] This parcel has another order to "+
                "a different destination. Please delete order "+value["order_id"]+
                " if it has not been processed.")
        except:
            raise ValidationError\
            ("[parcel_id] The Parcel ID does not exist.")


class OrderIdSchema(Schema):
    order_id = fields.Integer(required=True)

class ProcessOrderSchema(Schema):
    order_id = fields.Integer(required=True)
    order_status = fields.String(required = True)
    feedback = fields.String(required = True)

    @validates("order_status")
    def validate_amount_paid(self, order_status):
        accepted = ['accepted','rejected','unprocessed']
        if order_status not in accepted:
            raise ValidationError\
            ("[order_status] Order status can takeup one of "+
            " 'accepted', 'rejected' or 'unprocessed'")  
    


