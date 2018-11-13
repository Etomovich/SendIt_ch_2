from flask import request, make_response, jsonify
from flask_restful import Resource
from marshmallow import (Schema, fields, ValidationError,
        post_dump,post_load,validates)

from courier_app.send_it_apis.v1.validators import parcels_validators
from courier_app.send_it_apis.v1.models import (SystemUsers, 
    SendItUserOrders, SendItParcels)

from courier_app.send_it_apis.v1.views.user_views import (_authenticate_admin,
    _authenticate_user)

from courier_app.send_it_apis.pagination import Kurasa
from instance.config import Config

from itsdangerous import (TimedJSONWebSignatureSerializer as
        Serializer, BadSignature, SignatureExpired)

class AllParcels(Resource):
    def get(self):
        auth_user = _authenticate_admin()
        if not isinstance(auth_user, dict):
            return auth_user
        all_parcels = SendItParcels(auth_user['user_id'])
        pack = all_parcels.get_all_parcels()

        if (isinstance(pack, list)):
            #Return results
            kur = Kurasa(pack, 2)
            page = request.args.get('page', 1, type=int)
            page_items = kur.get_items(page)
            reply = {
                "Status":"OK",
                "All Parcels": page_items,
                "Total Parcels": len(pack),
                "Total Pages": str(kur.no_of_pages),
                "Next Page":"https://etomovich-sendit.herokuapp.com/api/v1/parcels?page="+\
                    str(page+1) if kur.has_next(page) else "END",
                "Prev Page":"https://etomovich-sendit.herokuapp.com/api/v1/parcels?page="+\
                    str(page-1) if kur.has_prev(page) else "BEGINNING"
            }
            answer = make_response(jsonify(reply),200)
            answer.content_type='application/json;charset=utf-8'
            return answer 

    def post(self):
        auth_user = _authenticate_admin()
        if not isinstance(auth_user, dict):
            return auth_user
        user_inp = request.get_json() or {}
        schema = parcels_validators.AddParcelSchema()
        result = schema.load(user_inp)
        if len(result.errors) < 1:
            
            create_parcel = SendItParcels(auth_user['user_id'])
            reply = create_parcel.add_parcel(
                owner_id = result.data['owner_id'],\
                weight = result.data['weight'],\
                submission_station = result.data['submission_station'],\
                present_location = result.data['present_location'])

            if reply:
                pack = {"Status":"OK","Message":"Created Sucessfully"}
                answer = make_response(jsonify(pack),201)
                answer.content_type='application/json;charset=utf-8'
                return answer
        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer

class AParcels(Resource):

    def get(self, parcel_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = parcels_validators.ParcelIdSchema()
        input_data = {"parcel_id":parcel_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            all_parcels = SendItParcels(auth_user['user_id'])
            pack = all_parcels.get_parcel(str(parcel_id))
            if (isinstance(pack, dict)):
                reply = {
                    "Status":"OK",
                    "Parcel": pack
                }
                answer = make_response(jsonify(reply),200)
                answer.content_type='application/json;charset=utf-8'
                return answer
            else:
                answer = make_response(jsonify(pack),401)
                answer.content_type='application/json;charset=utf-8'
                return answer
        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer

    def put(self, parcel_id):
        auth_user = _authenticate_admin()
        if not isinstance(auth_user, dict):
            return auth_user
        input_data = request.get_json() or {}
        schema = parcels_validators.EditParcelSchema()
        input_data["parcel_id"]=parcel_id
        result = schema.load(input_data)

        if len(result.errors) < 1:
            this_data ={
                "parcel_id": result.data["parcel_id"],
                "weight": result.data["weight"]  if\
                    "weight" in result.data else None,
                "destination": result.data["destination"] if\
                    "destination" in result.data else None,
                "expected_pay": result.data["expected_pay"] if\
                    "expected_pay" in result.data else None,
                "submission_station": result.data["submission_station"] if\
                    "submission_station" in result.data else None,
                "feedback": result.data["feedback"] if\
                    "feedback" in result.data else None,
                "order_id": result.data["order_id"] if\
                    "order_id" in result.data else None,
                "owner_id": result.data["owner_id"] if\
                    "owner_id" in result.data else None,
                "present_location": result.data["present_location"] if\
                    "present_location" in result.data else None,
                "status": result.data["status"] if\
                    "status" in result.data else None,
                "approved": result.data["approved"] if\
                    "approved" in result.data else None
            }

            edit_parcel = SendItParcels(auth_user['user_id'])
            reply = edit_parcel.edit_parcel(                
                parcel_id = this_data['parcel_id'],
                weight = this_data['weight'],
                destination = this_data['destination'],
                expected_pay = this_data['expected_pay'],
                submission_station = this_data['submission_station'],
                feedback = this_data['feedback'],
                order_id = this_data['order_id'],
                owner_id = this_data['owner_id'],
                present_location = this_data['present_location'],
                status = this_data['status'],
                approved = this_data['approved'])

            if reply == True :
                pack = {"Status":"Edited successfully"}
                answer = make_response(jsonify(pack),200)
                answer.content_type='application/json;charset=utf-8'
                return answer
            else:
                answer = make_response(jsonify(reply),401)
                answer.content_type='application/json;charset=utf-8'
                return answer
        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer

    def delete(self, parcel_id):
        auth_user = _authenticate_admin()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = parcels_validators.ParcelIdSchema()
        input_data = {"parcel_id":parcel_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            delete_order = SendItParcels(auth_user['user_id'])
            pack = delete_order.delete_parcel(str(parcel_id))
            if pack:
                reply = {
                    "Status":"Deleted"
                }
                answer = make_response(jsonify(reply),200)
                answer.content_type='application/json;charset=utf-8'
                return answer
        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer

class UserParcels(Resource):
    def get(self, user_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = parcels_validators.UserIdSchema()
        input_data = {"user_id":user_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            all_parcels = SendItParcels(auth_user['user_id'])
            pack = all_parcels.get_all_my_parcels(str(user_id))

            if (isinstance(pack, list)):
                #Return results
                kur = Kurasa(pack, 2)
                page = request.args.get('page', 1, type=int)
                page_items = kur.get_items(page)
                reply = {
                    "Status":"OK",
                    "Parcels": page_items,
                    "Total Parcels": len(pack),
                    "Total Pages": str(kur.no_of_pages),
                    "Next Page":"https://etomovich-sendit.herokuapp.com/api/v1/users/"\
                        +str(user_id)+"/parcels?page="+\
                        str(page+1) if kur.has_next(page) else "END",
                    "Prev Page":"https://etomovich-sendit.herokuapp.com/api/v1/users/"\
                        +str(user_id)+"/parcels?page="+\
                        str(page-1) if kur.has_prev(page) else "BEGINNING"
                }
                answer = make_response(jsonify(reply),200)
                answer.content_type='application/json;charset=utf-8'
                return answer 
            else:
                answer = make_response(jsonify(pack),401)
                answer.content_type='application/json;charset=utf-8'
                return answer
        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer

class ApprovedParcels(Resource):
    def get(self, user_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = parcels_validators.UserIdSchema()
        input_data = {"user_id":user_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            all_parcels = SendItParcels(auth_user['user_id'])
            pack = all_parcels.get_my_approved_parcels(str(user_id))

            if (isinstance(pack, list)):
                #Return results
                kur = Kurasa(pack, 2)
                page = request.args.get('page', 1, type=int)
                page_items = kur.get_items(page)
                reply = {
                    "Status":"OK",
                    "Approved Parcels": page_items,
                    "Total Parcels": len(pack),
                    "Total Pages": str(kur.no_of_pages),
                    "Next Page":"https://etomovich-sendit.herokuapp.com/api/v1/parcels/"\
                        +str(user_id)+"/approved?page="+\
                        str(page+1) if kur.has_next(page) else "END",
                    "Prev Page":"https://etomovich-sendit.herokuapp.com/api/v1/parcels/"\
                        +str(user_id)+"/approved?page="+\
                        str(page-1) if kur.has_prev(page) else "BEGINNING"
                }
                answer = make_response(jsonify(reply),200)
                answer.content_type='application/json;charset=utf-8'
                return answer 
            else:
                answer = make_response(jsonify(pack),401)
                answer.content_type='application/json;charset=utf-8'
                return answer
        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer

#
class CancelParcels(Resource):
    def put(self, parcel_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = parcels_validators.ParcelIdSchema()
        input_data = {"parcel_id":parcel_id}
        result = schema.load(input_data)

        if len(result.errors) < 1:
            cancel_parcel = SendItParcels(auth_user['user_id'])
            pack = cancel_parcel.user_cancels_delivery(str(parcel_id))
            if pack:
                reply = {
                    "Status":"Cancelled"
                }
                answer = make_response(jsonify(reply),200)
                answer.content_type='application/json;charset=utf-8'
                return answer
            else:
                answer = make_response(jsonify(pack),401)
                answer.content_type='application/json;charset=utf-8'
                return answer
        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer

class NotStartedParcels(Resource):
    def get(self, user_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = parcels_validators.UserIdSchema()
        input_data = {"user_id":user_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            all_parcels = SendItParcels(auth_user['user_id'])
            pack = all_parcels.get_my_notstarted_parcels(str(user_id))

            if (isinstance(pack, list)):
                #Return results
                kur = Kurasa(pack, 2)
                page = request.args.get('page', 1, type=int)
                page_items = kur.get_items(page)
                reply = {
                    "Status":"OK",
                    "Not Started Parcels": page_items,
                    "Total Parcels": len(pack),
                    "Total Pages": str(kur.no_of_pages),
                    "Next Page":"https://etomovich-sendit.herokuapp.com/api/v1/parcels/"\
                        +str(user_id)+"/not-started?page="+\
                        str(page+1) if kur.has_next(page) else "END",
                    "Prev Page":"https://etomovich-sendit.herokuapp.com/api/v1/parcels/"\
                        +str(user_id)+"/not-started?page="+\
                        str(page-1) if kur.has_prev(page) else "BEGINNING"
                }
                answer = make_response(jsonify(reply),200)
                answer.content_type='application/json;charset=utf-8'
                return answer 
            else:
                answer = make_response(jsonify(pack),401)
                answer.content_type='application/json;charset=utf-8'
                return answer
        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer

class InTransitParcels(Resource):
    def get(self, user_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = parcels_validators.UserIdSchema()
        input_data = {"user_id":user_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            all_parcels = SendItParcels(auth_user['user_id'])
            pack = all_parcels.get_my_intransit_parcels(str(user_id))

            if (isinstance(pack, list)):
                #Return results
                kur = Kurasa(pack, 2)
                page = request.args.get('page', 1, type=int)
                page_items = kur.get_items(page)
                reply = {
                    "Status":"OK",
                    "Intransit Parcels": page_items,
                    "Total Parcels": len(pack),
                    "Total Pages": str(kur.no_of_pages),
                    "Next Page":"https://etomovich-sendit.herokuapp.com/api/v1/parcels/"\
                        +str(user_id)+"/in-transit?page="+\
                        str(page+1) if kur.has_next(page) else "END",
                    "Prev Page":"https://etomovich-sendit.herokuapp.com/api/v1/parcels/"\
                        +str(user_id)+"/in-transit?page="+\
                        str(page-1) if kur.has_prev(page) else "BEGINNING"
                }
                answer = make_response(jsonify(reply),200)
                answer.content_type='application/json;charset=utf-8'
                return answer 
            else:
                answer = make_response(jsonify(pack),401)
                answer.content_type='application/json;charset=utf-8'
                return answer
        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer

class CancelledParcels(Resource):
    def get(self, user_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = parcels_validators.UserIdSchema()
        input_data = {"user_id":user_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            all_parcels = SendItParcels(auth_user['user_id'])
            pack = all_parcels.get_my_cancelled_parcels(str(user_id))

            if (isinstance(pack, list)):
                #Return results
                kur = Kurasa(pack, 2)
                page = request.args.get('page', 1, type=int)
                page_items = kur.get_items(page)
                reply = {
                    "Status":"OK",
                    "Cancelled Parcels": page_items,
                    "Total Parcels": len(pack),
                    "Total Pages": str(kur.no_of_pages),
                    "Next Page":"https://etomovich-sendit.herokuapp.com/api/v1/parcels/"\
                        +str(user_id)+"/cancelled?page="+\
                        str(page+1) if kur.has_next(page) else "END",
                    "Prev Page":"https://etomovich-sendit.herokuapp.com/api/v1/parcels/"\
                        +str(user_id)+"/cancelled?page="+\
                        str(page-1) if kur.has_prev(page) else "BEGINNING"
                }
                answer = make_response(jsonify(reply),200)
                answer.content_type='application/json;charset=utf-8'
                return answer 
            else:
                answer = make_response(jsonify(pack),401)
                answer.content_type='application/json;charset=utf-8'
                return answer
        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer

class DeliveredParcels(Resource):
    def get(self, user_id):
        auth_user = _authenticate_user()
        if not isinstance(auth_user, dict):
            return auth_user
        schema = parcels_validators.UserIdSchema()
        input_data = {"user_id":user_id}
        result = schema.load(input_data)
        if len(result.errors) < 1:
            all_parcels = SendItParcels(auth_user['user_id'])
            pack = all_parcels.get_my_delivered_parcels(str(user_id))

            if (isinstance(pack, list)):
                #Return results
                kur = Kurasa(pack, 2)
                page = request.args.get('page', 1, type=int)
                page_items = kur.get_items(page)
                reply = {
                    "Status":"OK",
                    "Delivered Parcels": page_items,
                    "Total Parcels": len(pack),
                    "Total Pages": str(kur.no_of_pages),
                    "Next Page":"https://etomovich-sendit.herokuapp.com/api/v1/parcels/"\
                        +str(user_id)+"/delivered?page="+\
                        str(page+1) if kur.has_next(page) else "END",
                    "Prev Page":"https://etomovich-sendit.herokuapp.com/api/v1/parcels/"\
                        +str(user_id)+"/delivered?page="+\
                        str(page-1) if kur.has_prev(page) else "BEGINNING"
                }
                answer = make_response(jsonify(reply),200)
                answer.content_type='application/json;charset=utf-8'
                return answer 
            else:
                answer = make_response(jsonify(pack),401)
                answer.content_type='application/json;charset=utf-8'
                return answer
        else:
            pack = {"Status":"Bad Request","Errors":result.errors}
            answer = make_response(jsonify(pack),400)
            answer.content_type='application/json;charset=utf-8'
            return answer
