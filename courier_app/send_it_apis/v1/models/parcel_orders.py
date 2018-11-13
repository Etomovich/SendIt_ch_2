import uuid

class SendItUserOrders(object):
    '''This class implements storage of System user orders'''    
    sendit_user_orders = {}

    def __init__(self, current_user_id):
        self.current_user_id = str(int(current_user_id))

    def _user_is_there(self):
        from courier_app.send_it_apis.v1.models import SystemUsers
        try:
            my_user={}
            my_user = SystemUsers.send_it_users[str(self.current_user_id)]
            my_user["user_id"] = str(self.current_user_id)
            return my_user
        except:
            return False

    #
    def add_order(self,parcel_id,parcel_description=None,pay_mode=None,\
                            pay_proof=None,amount_paid=None,destination=None):
        '''This method allows a user to make an order. '''        
        this_user = self._user_is_there()
        from courier_app.send_it_apis.v1.models import SendItParcels
        
        if this_user:
            new_id = uuid.uuid4().int
           
            payload = {
                "order_id": str(new_id),#CG
                "owner_id": str(self.current_user_id),#CG
                "parcel_id": str(int(parcel_id)),
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
            SendItUserOrders.sendit_user_orders[this_user["user_id"]]\
            .append(payload)
            return payload            
        return "UNKNOWN_USER"

    #
    def edit_order_user(self,order_id,parcel_id=None,parcel_description=None,\
        pay_mode=None,pay_proof=None,amount_paid=None,destination=None,\
        submitted=False):
        '''This method allows the owner of <order_id> to edit the order's details.
        NB: If the order is accepted you cannot edit.'''
        this_user = self._user_is_there()
        if this_user:
            #Check if current user is owner of order
            for item in SendItUserOrders.sendit_user_orders\
                [this_user["user_id"]]:
                
                if item['order_id'] == str(order_id) and \
                    (item['order_status'] == 'unprocessed' or \
                        item['order_status'] == 'rejected'):
                        
                    if item['order_status'] == 'accepted':
                        return "PROCESSED"

                    if parcel_id:
                        item['parcel_id'] = str(parcel_id)
                    if parcel_description:
                        item['parcel_description'] = str(parcel_description)
                    if pay_mode:
                        item['pay_mode'] = str(pay_mode)
                    if pay_proof:
                        item['pay_proof'] = str(pay_proof)
                    if amount_paid:
                        item['amount_paid'] = float(amount_paid)
                    if destination:
                        item['destination'] = str(destination)
                    if submitted:
                        if (len(item['parcel_description']) != 0) and\
                           (len(item['pay_mode']) != 0) and\
                           (len(item['pay_proof']) != 0) and\
                           (item['amount_paid'] != 0.0) and\
                           (len(item['destination']) != 0):
                            item['submitted'] = str(submitted)
                        else:
                            return "Fill fields[parcel_description,"+\
                                "pay_mode, pay_proof,amount_paid,"+\
                                "destination] before submitting."
                    return "EDITED"

            return "ORDER_NOT_FOUND"           
        
        return "UNKNOWN USER"

    #
    def remove_submission(self, order_id):
        '''This method allows a user to remove a submission.
        This method is useful if a user has made a premature submission
        or order has been rejected and wants to redo the order. NB: if
        the order is accepted you cannot remove submission'''
        this_user = self._user_is_there()
        if this_user:
            #Check if current user is owner of order
            for item in SendItUserOrders.sendit_user_orders\
                [this_user["user_id"]]:
                
                if item['order_id'] == str(order_id) and \
                    (item['order_status'] == 'unprocessed' or \
                    item['order_status'] == 'rejected'):

                    item['submitted'] = "False"
                    item['order_status'] == 'unprocessed'
                    return "DONE"

            return "ORDER_NOT_FOUND"
        
        return "UNKNOWN_USER"
    
    def process_order(self,order_id,order_status,feedback):
        '''This method allows the admin to process user order data'''
        from courier_app.send_it_apis.v1.models import SendItParcels
        this_user = self._user_is_there()
        if this_user and this_user["role"] == "Admin":
            for item in SendItUserOrders.sendit_user_orders.keys():
                for thing in SendItUserOrders.sendit_user_orders[item]:
                    if thing['order_id'] == str(order_id):
                        thing['order_status'] = str(order_status)
                        thing['feedback'] = str(feedback)
                        if order_status == "accepted":
                            SendItParcels.sendit_parcels[thing['parcel_id']]\
                            ['destination'] = thing['destination']
                        SendItParcels.sendit_parcels[thing['parcel_id']]\
                            ['status'] = 'not_started'
                        SendItParcels.sendit_parcels[thing['parcel_id']]\
                            ['approved'] = 'Yes'
                    return "DONE"
            return "ORDER_NOT_FOUND"
        return "UNAUTHORIZED"

    def return_all_orders(self):
        '''This is an admin method to return all orders in the system.'''
        this_user = self._user_is_there()
        if this_user and this_user["role"] == "Admin":
            reply = []
            for item in SendItUserOrders.sendit_user_orders.keys():
                orders_for_item = SendItUserOrders.sendit_user_orders[item] 
                reply = reply + orders_for_item
            return reply        
        return "UNAUTHORIZED"
    
    def return_all_unprocessed_orders(self):
        '''This is an admin method to return all 
        unprocessed orders in the system.'''
        this_user = self._user_is_there()
        if this_user and this_user["role"] == "Admin":
            reply = []
            for item in SendItUserOrders.sendit_user_orders.keys():
                orders_for_item = SendItUserOrders.sendit_user_orders[item]
                un_p = [] 
                for thing in orders_for_item:
                    if thing['order_status'] == "unprocessed":
                        un_p.append(thing)
                reply = reply + un_p
            return reply        
        return "UNAUTHORIZED"

    def return_an_order(self, order_id):
        '''This method is an admin method to fetch a single order'''
        this_user = self._user_is_there()
        if this_user and this_user["role"] == "Admin":
            for item in SendItUserOrders.sendit_user_orders.keys():
                orders_for_item = SendItUserOrders.sendit_user_orders[item] 
                for thing in orders_for_item:
                    if thing['order_id'] == str(order_id):
                        return thing
            return "ORDER_NOT_FOUND"        
        return "UNAUTHORIZED"

    def return_my_order(self, order_id):
        '''This method is a user method to fetch a single order from
        his/her list of orders'''
        this_user = self._user_is_there()
        if this_user:
            orders_for_item = SendItUserOrders.sendit_user_orders\
                            [str(self.current_user_id)] 
            for thing in orders_for_item:
                if thing['order_id'] == str(order_id):
                    return thing
            return "ORDER_NOT_FOUND"
        return "UNAUTHORIZED"

    #
    def user_order_deletion(self, order_id):
        '''This method allows a user to delete an order that has been
        rejected or yet to be processed'''
        from courier_app.send_it_apis.v1.models import SendItParcels
        this_user = self._user_is_there()
        if this_user:
            for item in SendItUserOrders.sendit_user_orders\
                                [str(self.current_user_id)]:
                if item["order_id"] == str(order_id) and \
                    (item['order_status'] == 'unprocessed' or \
                        item['order_status'] == 'rejected'):
                    SendItUserOrders.sendit_user_orders\
                                [str(self.current_user_id)].remove(item)
                    for item in SendItParcels.sendit_parcels.keys():
                        if SendItParcels.sendit_parcels[item]['order_id']\
                         == str(order_id):
                            SendItParcels.sendit_parcels[item]\
                            ['order_id'] = ""
                    return "DELETED"
            return "ORDER_PROCCESSED_OR_NOT_FOUND"
        return "UNAUTHORIZED"

    def admin_order_deletion(self, order_id):
        '''This method allows an administrator to delete an order.'''
        this_user = self._user_is_there()
        if this_user and this_user["role"] == "Admin":
            for item in SendItUserOrders.sendit_user_orders.keys():
                orders_for_item = SendItUserOrders.sendit_user_orders[item] 
                for thing in orders_for_item:
                    if thing['order_id'] == str(order_id):
                        SendItUserOrders.sendit_user_orders[item]\
                        .remove(thing)
                        return "DELETED"
            return "ORDER_NOT_FOUND"        
        return "UNAUTHORIZED"

    def my_processed_orders(self,user_id):
        '''This method allows a user to get his/her list of 
        processed orders.'''
        this_user = self._user_is_there()
        if this_user and (this_user["role"] == "Admin" or \
            this_user["user_id"] == str(user_id)):
            orders_for_item = SendItUserOrders.sendit_user_orders\
                            [str(user_id)]
            reply = [] 
            for thing in orders_for_item:
                if (thing['order_status'] == "accepted") or \
                (thing['order_status'] == "rejected"):
                    reply.append(thing)
            return reply
        return "UNAUTHORIZED"

    def my_unprocessed_orders(self, user_id):
        '''This method allows a user to get his/her list of 
        unprocessed orders.'''
        this_user = self._user_is_there()
        if this_user and (this_user["role"] == "Admin" or \
            this_user["user_id"] == str(user_id)):
            orders_for_item = SendItUserOrders.sendit_user_orders\
                            [str(user_id)]
            reply = [] 
            for thing in orders_for_item:
                if (thing['order_status'] == "unprocessed"):
                    reply.append(thing)
            return reply
        return "UNAUTHORIZED"


