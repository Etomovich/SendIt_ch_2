import uuid
from datetime import datetime

class SendItParcels(object):
    '''This class deals with storing user parcels.'''
    sendit_parcels= {}

    def __init__(self, current_user_id):
        self.current_user_id = str(int(current_user_id))

    def _user_is_there(self):
        from courier_app.send_it_apis.v1.models import SystemUsers
        try:
            my_user={}
            my_user = SystemUsers.send_it_users[self.current_user_id]
            my_user["user_id"] = self.current_user_id
            return my_user
        except:
            return False

    def add_parcel(self,owner_id,weight,submission_station,\
                    present_location):
        '''This is an admin function that is activated when the customer 
        brings a parcel to a station and its details are taken by an ADMIN. 
        The client then leaves with a parcel_id. He/she is then required 
        to go make an order of where he/she wants the parcel to go and 
        prove payments are valid.'''
        this_user = self._user_is_there()
        
        if this_user and this_user['role'] == "Admin":
            new_id = uuid.uuid4().int
            payload = {
                "owner_id": str(owner_id),
                "expected_pay": "",
                "order_id": "",
                "submission_station": submission_station,
                "present_location":present_location,
                "weight": float(weight),
                "feedback": "",
                "destination": "",
                "submission_date": str(datetime.utcnow()),
                "status": "not_started",
                "approved":"No"
            }            
            SendItParcels.sendit_parcels[str(new_id)] = payload
            return True            
        return "UNAUTHORIZED"

    def edit_parcel(self,parcel_id,weight=None,destination=None,\
        expected_pay=None,submission_station=None,feedback=None,\
        order_id=None, owner_id=None,present_location=None,\
        status=None, approved = None):
        '''This method allows an admin to edit a parcel.'''
        this_user = self._user_is_there()
        if this_user and this_user['role'] == "Admin":
            if approved:
                SendItParcels.sendit_parcels[str(parcel_id)]\
                ['approved'] = str(approved)
            if weight:
                SendItParcels.sendit_parcels[str(parcel_id)]\
                ['weight'] = float(weight)
            if destination:
                SendItParcels.sendit_parcels[str(parcel_id)]\
                ['destination'] = str(destination)
            if expected_pay:
                SendItParcels.sendit_parcels[str(parcel_id)]\
                ['expected_pay'] = str(expected_pay)
            if submission_station:
                SendItParcels.sendit_parcels[str(parcel_id)]\
                ['submission_station'] = str(submission_station)
            if feedback:
                SendItParcels.sendit_parcels[str(parcel_id)]\
                ['feedback'] = str(feedback)
            if order_id:
                SendItParcels.sendit_parcels[str(parcel_id)]\
                ['order_id'] = str(order_id)
            if owner_id:
                SendItParcels.sendit_parcels[str(parcel_id)]\
                ['owner_id'] = str(owner_id)
            if present_location:
                SendItParcels.sendit_parcels[str(parcel_id)]\
                ['present_location'] = str(present_location)
            if status:
                SendItParcels.sendit_parcels[str(parcel_id)]\
                ['status'] = str(status)

            return True
        return "UNAUTHORIZED"

    def user_cancels_delivery(self, parcel_id):
        '''This method implements a user cancelling a delivery. It is 
        assumed that the current_user is the user making the action.'''
        this_user = self._user_is_there()
        if this_user["user_id"]== SendItParcels.sendit_parcels\
            [str(parcel_id)]['owner_id']:
            SendItParcels.sendit_parcels[str(parcel_id)]\
            ['status'] = "cancelled"
            return True
        return "UNAUTHORIZED"        

    def get_all_parcels(self):
        '''This method returns all parcels in the system which makes it an 
        admin function.'''
        this_user = self._user_is_there()
        if this_user and this_user['role'] == "Admin":
            reply = []
            for item in SendItParcels.sendit_parcels.keys():
                payload = SendItParcels.sendit_parcels[item]
                payload["parcel_id"] = item
                reply.append(payload)
            return reply
        return "UNAUTHORIZED"

    def delete_parcel(self, parcel_id):
        '''This method deletes a parcels in the system which makes it an 
        admin function. A user can only cancel a parcel delivery order'''
        this_user = self._user_is_there()
        if this_user and this_user['role'] == "Admin":
            del SendItParcels.sendit_parcels[str(parcel_id)]
            return True
        return "UNAUTHORIZED"

    def get_parcel(self, parcel_id):
        '''This method is only available to the admin and user who delivered
        the parcel.[current_user]'''
        this_user = self._user_is_there()
        if this_user and (this_user['role']\
            == "Admin" or this_user['user_id'] == SendItParcels.\
            sendit_parcels[str(parcel_id)]['owner_id']):
            return SendItParcels.sendit_parcels[str(parcel_id)]
        return "UNAUTHORIZED"

    def get_all_my_parcels(self, user_id):
        '''This method is only available to the admin and user who delivered
        the parcel.[current_user]'''
        this_user = self._user_is_there()
        if this_user:
            reply = []
            for item in SendItParcels.sendit_parcels.keys():
                if (SendItParcels.sendit_parcels[item]['owner_id'] == \
                    str(user_id) and (this_user['role'] == "Admin" or \
                    this_user['user_id'] == str(user_id))):
                    reply.append(SendItParcels.sendit_parcels[item])
            return reply
        return "UNAUTHORIZED"
    
    def get_my_approved_parcels(self,user_id):
        '''This method is only available to the admin and user who delivered
        the parcel.[current_user]'''
        this_user = self._user_is_there()
        if this_user:
            reply = []
            for item in SendItParcels.sendit_parcels.keys():
                if (SendItParcels.sendit_parcels[item]['approved']=="Yes"and\
                    SendItParcels.sendit_parcels[item]['owner_id'] == \
                    str(user_id) and (this_user['role'] == "Admin" or \
                    this_user['user_id'] == str(user_id))):
                    reply.append(SendItParcels.sendit_parcels[item])
            return reply
        return "UNAUTHORIZED"

    def get_my_notstarted_parcels(self, user_id):
        '''This method is only available to the admin and user who delivered
        the parcel.[current_user]'''
        this_user = self._user_is_there()
        if this_user:
            reply = []
            for item in SendItParcels.sendit_parcels.keys():
                if (SendItParcels.sendit_parcels[item]['status']==\
                    "not_started"and SendItParcels.sendit_parcels\
                    [item]['owner_id'] == str(user_id) and 
                    (this_user['role'] == "Admin" or \
                    this_user['user_id'] == str(user_id))):
                    reply.append(SendItParcels.sendit_parcels[item])
            return reply
        return "UNKNOWN_USER"

    def get_my_intransit_parcels(self, user_id):
        '''This method is only available to the admin and user who delivered
        the parcel.[current_user]'''
        this_user = self._user_is_there()
        if this_user:
            reply = []
            for item in SendItParcels.sendit_parcels.keys():
                if (SendItParcels.sendit_parcels[item]['status'] == \
                    "in_transit" and SendItParcels.sendit_parcels\
                    [item]['owner_id'] == str(user_id) and 
                    (this_user['role'] == "Admin" or \
                    this_user['user_id'] == str(user_id))):
                    reply.append(SendItParcels.sendit_parcels[item])
            return reply
        return "UNKNOWN_USER"
    
    def get_my_cancelled_parcels(self,user_id):
        '''This method is only available to the admin and user who delivered
        the parcel.[current_user]'''
        this_user = self._user_is_there()
        if this_user:
            reply = []
            for item in SendItParcels.sendit_parcels.keys():
                if (SendItParcels.sendit_parcels[item]['status']==\
                    "cancelled"and SendItParcels.sendit_parcels\
                    [item]['owner_id'] == str(user_id) and 
                    (this_user['role'] == "Admin" or \
                    this_user['user_id'] == str(user_id))):
                        reply.append(SendItParcels.sendit_parcels[item])
            return reply
        return "UNKNOWN_USER"

    def get_my_delivered_parcels(self, user_id):
        '''This method is only available to the admin and user who delivered
        the parcel.[current_user]'''
        this_user = self._user_is_there()
        if this_user:
            reply = []
            for item in SendItParcels.sendit_parcels.keys():
                if (SendItParcels.sendit_parcels[item]['status']==\
                    "delivered"and SendItParcels.sendit_parcels\
                    [item]['owner_id'] == str(user_id) and 
                    (this_user['role'] == "Admin" or \
                    this_user['user_id'] == str(user_id))):
                        reply.append(SendItParcels.sendit_parcels[item])
            return reply
        return "UNKNOWN_USER"


