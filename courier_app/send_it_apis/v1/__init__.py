from flask import Blueprint
from flask_restful import Resource, Api

from courier_app.send_it_apis.v1.views.user_views import CreateUser,\
    UserLogin, FetchAllUsers, TheUser

bp = Blueprint("my_api_v1", __name__)

v1_bp = Api(bp)

#User routes
v1_bp.add_resource(CreateUser,"/register")
v1_bp.add_resource(UserLogin,"/login")
v1_bp.add_resource(FetchAllUsers,"/users")
v1_bp.add_resource(TheUser,"/user/<int:user_id>")


from courier_app.send_it_apis.v1.models.send_it_users import SystemUsers
from courier_app.send_it_apis.v1.models.parcel_orders import SendItUserOrders
from courier_app.send_it_apis.v1.models.parcels import SendItParcels