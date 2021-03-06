import os
from flask import request, make_response, jsonify
from flask_restful import Resource
from marshmallow import (Schema, fields, ValidationError,
        post_dump,post_load,validates)

from courier_app.send_it_apis.v2.validators import parcel_orders_validators 
from courier_app.send_it_apis.v2.models import (SystemUsers, SendItUserOrders,
    SendItParcels)

from courier_app.send_it_apis.v2.views.user_views import (_authenticate_admin,
    _authenticate_user)

from courier_app.send_it_apis.pagination import Kurasa
from instance.config import Config

from itsdangerous import (TimedJSONWebSignatureSerializer as
        Serializer, BadSignature, SignatureExpired)

BASE_URL = os.getenv('PAGINATE_BASE_URL') 

class Home(Resource):
    def get(self):
        reply = {
            "Routes Documentation":
            "https://documenter.getpostman.com/view/5585722/RzZ9GeuW"
            }
        answer = make_response(jsonify(reply),200)
        answer.content_type='application/json;charset=utf-8'
        return answer

class AllOrders(Resource):
    def get(self):
        auth_user = _authenticate_admin()
        if not isinstance(auth_user, dict):
            return auth_user
        all_users = SendItUserOrders(auth_user['user_id'])
        pack = all_users.return_all_orders()

        if (isinstance(pack, list)):
            #Return results
            kur = Kurasa(pack, 2)
            page = request.args.get('page', 1, type=int)
            page_items = kur.get_items(page)
            reply = {
                "Status":"OK",
                "Orders": page_items,
                "Total Orders": len(pack),
                "Total Pages": str(kur.no_of_pages),
                "Next Page":BASE_URL+"/api/v2/users?page="+\
                    str(page+1) if kur.has_next(page) else "END",
                "Prev Page":BASE_URL+"/api/v2/users?page="+\
                    str(page-1) if kur.has_prev(page) else "BEGINNING"
            }
            answer = make_response(jsonify(reply),200)
            answer.content_type='application/json;charset=utf-8'
            return answer 

    def post(self):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        user_inp = request.get_json() or {}
        schema = parcel_orders_validators.AddOrderSchema()
        result = schema.load(user_inp)
        if len(result.errors) < 1:
            this_data ={
                "parcel_id": result.data["parcel_id"],
                "parcel_name": result.data["parcel_name"] if\
                    "parcel_name" in result.data else None,
                "parcel_description": result.data["parcel_description"] if\
                    "parcel_description" in result.data else None,
                "pay_mode": result.data["pay_mode"] if\
                    "pay_mode" in result.data else None,
                "pay_proof": result.data["pay_proof"] if\
                    "pay_proof" in result.data else None,
                "amount_paid": result.data["amount_paid"] if\
                    "amount_paid" in result.data else None,
                "destination": result.data["destination"] if\
                    "destination" in result.data else None
            }
            create_order = SendItUserOrders(auth_user['user_id'])
            reply = create_order.add_order(
                parcel_id = this_data['parcel_id'],\
                parcel_name = this_data['parcel_name'],\
                parcel_description=this_data['parcel_description'],\
                pay_mode=this_data['pay_mode'],\
                pay_proof=this_data['pay_proof'],
                amount_paid=this_data['amount_paid'],\
                destination=this_data['destination'])

            if reply["message"] == "CREATED":
                reply["Status"] = "OK"
                answer = make_response(jsonify(reply),201)
                answer.content_type='application/json;charset=utf-8'
                return answer
            answer = make_response(jsonify(reply),401)
            answer.content_type='application/json;charset=utf-8'
            return answer
        pack = {"Status":"Bad Request","Errors":result.errors}
        answer = make_response(jsonify(pack),400)
        answer.content_type='application/json;charset=utf-8'
        return answer

class MyOrderView(Resource):
    def get(self, order_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = parcel_orders_validators.OrderIdSchema()
        input_data = {"order_id":order_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            this_user = SendItUserOrders(auth_user['user_id'])
            pack = this_user.return_my_order(str(order_id))
            if (pack['message'] ==  "FOUND"):
                pack["Status"] = "OK"
                answer = make_response(jsonify(pack),200)
                answer.content_type='application/json;charset=utf-8'
                return answer
            answer = make_response(jsonify(pack),401)
            answer.content_type='application/json;charset=utf-8'
            return answer
        pack = {"Status":"Bad Request","Errors":result.errors}
        answer = make_response(jsonify(pack),400)
        answer.content_type='application/json;charset=utf-8'
        return answer

    def put(self, order_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        user_inp = request.get_json() or {}
        user_inp['order_id'] = order_id
        schema = parcel_orders_validators.EditOrderSchema()
        result = schema.load(user_inp)

        if len(result.errors) < 1:
            this_data ={
                "order_id": result.data["order_id"],
                "parcel_id": result.data["parcel_id"]  if\
                    "parcel_id" in result.data else None,
                "parcel_name": result.data["parcel_name"]  if\
                    "parcel_name" in result.data else None,
                "parcel_description": result.data["parcel_description"] if\
                    "parcel_description" in result.data else None,
                "pay_mode": result.data["pay_mode"] if\
                    "pay_mode" in result.data else None,
                "pay_proof": result.data["pay_proof"] if\
                    "pay_proof" in result.data else None,
                "amount_paid": result.data["amount_paid"] if\
                    "amount_paid" in result.data else None,
                "destination": result.data["destination"] if\
                    "destination" in result.data else None,
                "submitted": result.data["submitted"] if\
                    "submitted" in result.data else None
            }

            edit_order = SendItUserOrders(auth_user['user_id'])
            reply = edit_order.edit_order_user(
                order_id = this_data['order_id'],\
                parcel_id = this_data['parcel_id'],\
                parcel_name = this_data['parcel_name'],\
                parcel_description=this_data['parcel_description'],\
                pay_mode=this_data['pay_mode'],\
                pay_proof=this_data['pay_proof'],
                amount_paid=this_data['amount_paid'],\
                destination=this_data['destination'],\
                submitted=this_data['submitted'])

            if reply["message"] == 'EDITED':
                answer = make_response(jsonify(reply),200)
                answer.content_type='application/json;charset=utf-8'
                return answer
            
            if reply["Status"] == 'bad':
                answer = make_response(jsonify(reply),400)
                answer.content_type='application/json;charset=utf-8'
                return answer

            answer = make_response(jsonify(reply),401)
            answer.content_type='application/json;charset=utf-8'
            return answer
        pack = {"Status":"Bad Request","Errors":result.errors}
        answer = make_response(jsonify(pack),400)
        answer.content_type='application/json;charset=utf-8'
        return answer
    
    def delete(self, order_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = parcel_orders_validators.OrderIdSchema()
        input_data = {"order_id":order_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            delete_order = SendItUserOrders(auth_user['user_id'])
            pack = delete_order.user_order_deletion(str(order_id))
            if pack["message"] == "DELETED":
                answer = make_response(jsonify(pack),200)
                answer.content_type='application/json;charset=utf-8'
                return answer
            answer = make_response(jsonify(pack),404)
            answer.content_type='application/json;charset=utf-8'
            return answer
        pack = {"Status":"Bad Request","Errors":result.errors}
        answer = make_response(jsonify(pack),400)
        answer.content_type='application/json;charset=utf-8'
        return answer

class AdminOrderView(Resource):
    def get(self, order_id):
        auth_user = _authenticate_admin()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = parcel_orders_validators.OrderIdSchema()
        input_data = {"order_id":order_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            this_user = SendItUserOrders(auth_user['user_id'])
            pack = this_user.return_an_order(str(order_id))
            if (pack['message'] ==  "FOUND"):
                pack["Status"] = "OK"
                answer = make_response(jsonify(pack),200)
                answer.content_type='application/json;charset=utf-8'
                return answer
            answer = make_response(jsonify(pack),401)
            answer.content_type='application/json;charset=utf-8'
            return answer
        pack = {"Status":"Bad Request","Errors":result.errors}
        answer = make_response(jsonify(pack),400)
        answer.content_type='application/json;charset=utf-8'
        return answer

    def delete(self, order_id):
        auth_user = _authenticate_admin()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = parcel_orders_validators.OrderIdSchema()
        input_data = {"order_id":order_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            delete_order = SendItUserOrders(auth_user['user_id'])
            pack = delete_order.admin_order_deletion(str(order_id))
            if pack["message"] == "DELETED":
                answer = make_response(jsonify(pack),200)
                answer.content_type='application/json;charset=utf-8'
                return answer
            answer = make_response(jsonify(pack),401)
            answer.content_type='application/json;charset=utf-8'
            return answer
        pack = {"Status":"Bad Request","Errors":result.errors}
        answer = make_response(jsonify(pack),400)
        answer.content_type='application/json;charset=utf-8'
        return answer

class RemoveSubmission(Resource):
    def put(self, order_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        user_inp = {}
        user_inp['order_id'] = order_id
        schema = parcel_orders_validators.OrderIdSchema()
        result = schema.load(user_inp)
        if len(result.errors) < 1:
            remove_sub = SendItUserOrders(auth_user['user_id'])
            reply = remove_sub.remove_submission(
                order_id = result.data['order_id'])

            if reply["message"] == "Submission Removed":
                answer = make_response(jsonify(reply),200)
                answer.content_type='application/json;charset=utf-8'
                return answer

            if reply["message"] == "This order is yet to be submitted.":
                answer = make_response(jsonify(reply),400)
                answer.content_type='application/json;charset=utf-8'
                return answer

            answer = make_response(jsonify(reply),401)
            answer.content_type='application/json;charset=utf-8'
            return answer
        pack = {"Status":"Bad Request","Errors":result.errors}
        answer = make_response(jsonify(pack),400)
        answer.content_type='application/json;charset=utf-8'
        return answer
    
class ProcessOrder(Resource):
    def put(self, order_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        user_inp = request.get_json() or {}
        user_inp['order_id'] = order_id
        schema = parcel_orders_validators.ProcessOrderSchema()
        result = schema.load(user_inp)

        if len(result.errors) < 1:
            process_ord = SendItUserOrders(auth_user['user_id'])
            reply = process_ord.process_order(
                order_id = result.data['order_id'],\
                order_status = result.data['order_status'],\
                feedback=result.data['feedback'],\
                approved = result.data['approved'])

            if reply["message"] == "Order proccessed.":
                answer = make_response(jsonify(reply),200)
                answer.content_type='application/json;charset=utf-8'
                return answer
            answer = make_response(jsonify(reply),401)
            answer.content_type='application/json;charset=utf-8'
            return answer
        pack = {"Status":"Bad Request","Errors":result.errors}
        answer = make_response(jsonify(pack),400)
        answer.content_type='application/json;charset=utf-8'
        return answer
    
class AllUnprocessedOrders(Resource):
    def get(self):
        auth_user = _authenticate_admin()
        if not isinstance(auth_user, dict):
            return auth_user
        all_users = SendItUserOrders(auth_user['user_id'])
        pack = all_users.return_all_unprocessed_orders()

        if (isinstance(pack, list)):
            #Return results
            kur = Kurasa(pack, 2)
            page = request.args.get('page', 1, type=int)
            page_items = kur.get_items(page)
            reply = {
                "Status":"OK",
                "Orders": page_items,
                "Total Orders": len(pack),
                "Total Pages": str(kur.no_of_pages),
                "Next Page":BASE_URL+"/api/v2/orders/unprocessed?page="+\
                    str(page+1) if kur.has_next(page) else "END",
                "Prev Page":BASE_URL+"/api/v2/orders/unprocessed?page="+\
                    str(page-1) if kur.has_prev(page) else "BEGINNING"
            }
            answer = make_response(jsonify(reply),200)
            answer.content_type='application/json;charset=utf-8'
            return answer 
        answer = make_response(jsonify(pack),401)
        answer.content_type='application/json;charset=utf-8'
        return answer

class MyProcessedOrders(Resource):
    def get(self,user_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        all_users = SendItUserOrders(auth_user['user_id'])
        pack = all_users.my_processed_orders(str(user_id))

        if (isinstance(pack, list)):
            #Return results
            kur = Kurasa(pack, 2)
            page = request.args.get('page', 1, type=int)
            page_items = kur.get_items(page)
            reply = {
                "Status":"OK",
                "Orders": page_items,
                "Total Orders": len(pack),
                "Total Pages": str(kur.no_of_pages),
                "Next Page":BASE_URL+"/api/v2/orders/"\
                    +str(user_id)+"/processed?page="+\
                    str(page+1) if kur.has_next(page) else "END",
                "Prev Page":BASE_URL+"/api/v2/orders/"\
                    +str(user_id)+"/processed?page="+\
                    str(page-1) if kur.has_prev(page) else "BEGINNING"
            }
            answer = make_response(jsonify(reply),200)
            answer.content_type='application/json;charset=utf-8'
            return answer 
        answer = make_response(jsonify(pack),401)
        answer.content_type='application/json;charset=utf-8'
        return answer

class MyUnprocessedOrders(Resource):
    def get(self,user_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        all_users = SendItUserOrders(auth_user['user_id'])
        pack = all_users.my_unprocessed_orders(str(user_id))

        if (isinstance(pack, list)):
            #Return results
            kur = Kurasa(pack, 2)
            page = request.args.get('page', 1, type=int)
            page_items = kur.get_items(page)
            reply = {
                "Status":"OK",
                "Orders": page_items,
                "Total Orders": len(pack),
                "Total Pages": str(kur.no_of_pages),
                "Next Page":BASE_URL+"/api/v2/orders/"\
                    +str(user_id)+"/unprocessed?page="+\
                    str(page+1) if kur.has_next(page) else "END",
                "Prev Page":BASE_URL+"/api/v2/orders/"\
                    +str(user_id)+"/unprocessed?page="+\
                    str(page-1) if kur.has_prev(page) else "BEGINNING"
            }
            answer = make_response(jsonify(reply),200)
            answer.content_type='application/json;charset=utf-8'
            return answer 
        answer = make_response(jsonify(pack),401)
        answer.content_type='application/json;charset=utf-8'
        return answer
