from flask import Blueprint
from flask_restful import Resource, Api

from courier_app.send_it_apis.v2.views.user_views import (CreateUser,
    UserLogin, FetchAllUsers, TheUser) 

from courier_app.send_it_apis.v2.views.parcel_views import (AllParcels,
    AParcels, UserParcels, CancelParcels, ApprovedParcels,
    NotStartedParcels,InTransitParcels, CancelledParcels, DeliveredParcels,
    DestinationChanger,StatusChanger,LocationChanger)

from courier_app.send_it_apis.v2.views.user_order_views import (AllOrders,
    MyOrderView,AdminOrderView, RemoveSubmission, ProcessOrder,
    AllUnprocessedOrders,MyProcessedOrders,MyUnprocessedOrders)

bp = Blueprint("my_api_v2", __name__)

v2_bp = Api(bp)

#User routes
v2_bp.add_resource(CreateUser,"/register")
v2_bp.add_resource(UserLogin,"/login")
v2_bp.add_resource(FetchAllUsers,"/users")
v2_bp.add_resource(TheUser,"/user/<int:user_id>")

#Parcel routes
v2_bp.add_resource(AllParcels,"/parcels")
v2_bp.add_resource(AParcels,"/parcels/<int:parcel_id>")
v2_bp.add_resource(UserParcels,"/users/<int:user_id>/parcels")
v2_bp.add_resource(CancelParcels,"/parcels/<int:parcel_id>/cancel")
v2_bp.add_resource(ApprovedParcels,"/parcels/<int:user_id>/approved")
v2_bp.add_resource(NotStartedParcels,"/parcels/<int:user_id>/not-started")
v2_bp.add_resource(InTransitParcels,"/parcels/<int:user_id>/in-transit")
v2_bp.add_resource(CancelledParcels,"/parcels/<int:user_id>/cancelled")
v2_bp.add_resource(DeliveredParcels,"/parcels/<int:user_id>/delivered")

v2_bp.add_resource(DestinationChanger,"/parcels/<int:parcel_id>/destination")
v2_bp.add_resource(StatusChanger,"/parcels/<int:parcel_id>/status")
v2_bp.add_resource(LocationChanger,"/parcels/<int:parcel_id>/presentLocation")

#Order routes
v2_bp.add_resource(AllOrders,"/orders")
v2_bp.add_resource(MyOrderView, "/order/<int:order_id>")
v2_bp.add_resource(AdminOrderView, "/admin/order/<int:order_id>")
v2_bp.add_resource(RemoveSubmission, "/order/<int:order_id>/unsubmitted")
v2_bp.add_resource(ProcessOrder, "/order/process/<int:order_id>")
v2_bp.add_resource(AllUnprocessedOrders, "/orders/unprocessed")
v2_bp.add_resource(MyUnprocessedOrders, "/orders/<int:user_id>/unprocessed")
v2_bp.add_resource(MyProcessedOrders, "/orders/<int:user_id>/processed")

from courier_app.send_it_apis.v2.models.send_it_users import SystemUsers
from courier_app.send_it_apis.v2.models.parcels import SendItParcels
from courier_app.send_it_apis.v2.models.parcel_orders import SendItUserOrders