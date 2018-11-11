from marshmallow import Schema, fields, ValidationError,\
        post_dump,post_load,validates, validates_schema

from courier_app.send_it_apis.v1.models import SendItUserOrders,SendItParcels,\
        SystemUsers

class AddParcelSchema(Schema):
    owner_id = fields.Integer(required=True)
    weight= fields.String(required=True)
    submission_station=fields.String(required=True)
    present_location=fields.String(required=True)

    @validates("owner_id")
    def validate_amount_paid(self, owner_id):
        try:
            value = SystemUsers.send_it_users[str(owner_id)]
        except:
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
        try:
            value = SendItParcels.sendit_parcels[(str(parcel_id))]
        except:
            raise ValidationError\
            ("[parcel_id] The Parcel ID does not exist.")

    @validates("owner_id")
    def validate_owner_id(self, owner_id):
        try:
            value = SystemUsers.send_it_users[str(owner_id)]
        except:
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
        found = False
        for item in SendItUserOrders.sendit_user_orders.keys():
            for list_thing in SendItUserOrders.sendit_user_orders[item]:
                if list_thing["order_id"] == str(order_id):
                    found = True
                    break
        
        if not found:
            raise ValidationError\
            ("[order_id] This order id cannot be located.")

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
            ("[status] Order status can takeup one of 'not_started'"+
            " 'in_transit', 'cancelled' or 'delivered'")

    @validates("approved")
    def validate_approved(self, approved):
        accepted = ['approved','not_yet',]
        if approved not in accepted:
            raise ValidationError\
            ("[status] Order status can takeup one of 'approved','not_yet'")

class ParcelIdSchema(Schema):
    parcel_id = fields.Integer(required=True)

    @validates("parcel_id")
    def validate_parcel_id(self,parcel_id):
        try:
            value = SendItParcels.sendit_parcels[(str(parcel_id))]
        except:
            raise ValidationError\
            ("[parcel_id] The Parcel ID does not exist.")

class UserIdSchema(Schema):
    user_id = fields.Integer(required=True)

    @validates("user_id")
    def validate_user_id (self, user_id):
        try:
            value = SystemUsers.send_it_users[str(user_id)]
        except:
            raise ValidationError\
            ("[user_id] The user does not exist in the system.")


