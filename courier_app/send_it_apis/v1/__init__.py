from flask import Blueprint
from flask_restful import Resource, Api

from courier_app.send_it_apis.v1.views.user_views import CreateUser,\
    UserLogin, FetchAllUsers, TheUser

from courier_app.send_it_apis.v1.views.parcel_views import AllParcels,\
    AParcels, UserParcels, CancelParcels, ApprovedParcels,\
    NotStartedParcels,InTransitParcels, CancelledParcels, DeliveredParcels

bp = Blueprint("my_api_v1", __name__)

v1_bp = Api(bp)

#User routes
v1_bp.add_resource(CreateUser,"/register")
v1_bp.add_resource(UserLogin,"/login")
v1_bp.add_resource(FetchAllUsers,"/users")
v1_bp.add_resource(TheUser,"/user/<int:user_id>")

#Parcel routes
v1_bp.add_resource(AllParcels,"/parcels")
v1_bp.add_resource(AParcels,"/parcels/<int:parcel_id>")
v1_bp.add_resource(UserParcels,"/users/<int:user_id>/parcels")
v1_bp.add_resource(CancelParcels,"/parcels/<int:parcel_id>/cancel")
v1_bp.add_resource(ApprovedParcels,"/parcels/<int:user_id>/approved")
v1_bp.add_resource(NotStartedParcels,"/parcels/<int:user_id>/not-started")
v1_bp.add_resource(InTransitParcels,"/parcels/<int:user_id>/in-transit")
v1_bp.add_resource(CancelledParcels,"/parcels/<int:user_id>/cancelled")
v1_bp.add_resource(DeliveredParcels,"/parcels/<int:user_id>/delivered")


from courier_app.send_it_apis.v1.models.send_it_users import SystemUsers
from courier_app.send_it_apis.v1.models.parcel_orders import SendItUserOrders
from courier_app.send_it_apis.v1.models.parcels import SendItParcels