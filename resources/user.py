from flask.views import MethodView
from flask import current_app
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256 # hashing algorithm
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import or_

from db import db
from models import UserModel
from schemas import UserSchema, UserRegisterSchema
from blocklist import BLOCKLIST
from tasks import send_user_registration_email

blp = Blueprint("users", __name__, description="Operations on users") 


@blp.route("/register")
class UserRegister(MethodView):
	@blp.arguments(UserRegisterSchema)
	def post(self, user_data):
		if UserModel.query.filter(
			or_(
				UserModel.username == user_data["username"],
				UserModel.email == user_data["email"]
			)
		).first():
			abort(409, message="A user with that username or email already exists.")


		# hash the user password before sending it to the database
		user = UserModel(
			username = user_data["username"],
			email = user_data["email"],
			password = pbkdf2_sha256.hash(user_data["password"])
		)

		try:
			db.session.add(user)
			db.session.commit()

			current_app.queue.enqueue(send_user_registration_email, user.email, user.username)

		except IntegrityError:
			abort(400, message="A user with that username already exists")
		except SQLAlchemyError:
			abort(500, message="An error occurred while inserting the item.")

		return {"message": "User created successfully."}, 201

@blp.route("/login")
class UserLogin(MethodView):
	@blp.arguments(UserSchema)
	def post(self, user_data):
		user = UserModel.query.filter(
			UserModel.username == user_data["username"]
		).first()

		if user and pbkdf2_sha256.verify(user_data["password"], user.password):
			# the JWT access token stores an identity, which is the user's ID
			access_token = create_access_token(identity=user.id, fresh=True)
			refresh_token = create_refresh_token(identity=user.id)
			return {"access_token": access_token, "refresh_token": refresh_token}

		abort(401, message="Invalid credentials.")

# you can determine here how many times of for how long a refresh token is valid
# after that you can add the refresh token to the blocklist
@blp.route("/refresh")
class TokenRefresh(MethodView):
	@jwt_required(refresh=True) # needs a refresh token, not an access token
	def post(self):
		# get_jwt_identity is the same as get_jwt().get("sub") 
		# -> grab the subject (user.id in our case) of the jwt
		# returns none if there is no current user
		current_user = get_jwt_identity()
		# create non-fresh token
		new_token = create_access_token(identity=current_user, fresh=False)

		# permit the refresh token to be used only once than blocklist it
		jti = get_jwt()["jti"]
		BLOCKLIST.add(jti)
		
		return {"access_token": new_token}

@blp.route("/logout")
class UserLogout(MethodView):
	@jwt_required()
	def post(self):
		# jti is the jwt id - which is the jwt unique identifier
		# it is stored in the jwt payload
		jti = get_jwt()["jti"]
		BLOCKLIST.add(jti)
		return {"message": "Successfully logged out."}, 200

@blp.route("/user/<int:user_id>")
class User(MethodView):
	@blp.response(200, UserSchema)
	def get(self, user_id):
		user = UserModel.query.get_or_404(user_id)
		return user

	def delete(self, user_id):
		user = UserModel.query.get_or_404(user_id)
		db.session.delete(user)
		db.session.commit()
		return {"message": "User deleted."}, 200		