from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("items", __name__, description="Operations on items")

@blp.route("/item/<int:item_id>")
class Item(MethodView):
	@jwt_required()
	@blp.response(200, ItemSchema)
	def get(self, item_id):
		# look for the item by its primary key, and if it 
		# doesnt find it, it automatically aborts
		item = ItemModel.query.get_or_404(item_id)
		return item

	@jwt_required()
	def delete(self, item_id):
		jwt = get_jwt()
		# jwt works like a dictionary
		if not jwt.get("is_admin"):
			abort(401, message="Admin privilege required.")
			
		item = ItemModel.query.get_or_404(item_id)
		db.session.delete(item)
		db.session.commit()
		return {"message": "Item deleted"}

	@blp.arguments(ItemUpdateSchema)
	@blp.response(200, ItemSchema)
	def put(self, item_data, item_id):
		item = ItemModel.query.get(item_id)

		# if the item exists, update it. If not, create it
		if item:
			item.price = item_data["price"]
			item.name = item_data["name"]
		else:
			# for this needs price, name and store_id
			# or will get an error
			item = ItemModel(id=item_id, **item_data)

		db.session.add(item)
		db.session.commit()

		return item

@blp.route("/item")
class ItemList(MethodView):

	# ItemSchema(many=True) because we are returning a list
	@jwt_required()
	@blp.response(200, ItemSchema(many=True))
	def get(self):
		# marschmallow turns this into a list
		return ItemModel.query.all()

	@jwt_required(fresh=True) # tell this method needs a fresh token
	@blp.arguments(ItemSchema)
	@blp.response(201, ItemSchema)
	def post(self, item_data):
		# create an item model
		item = ItemModel(**item_data)

		try:
			db.session.add(item)
			# committing writes to the database
			db.session.commit()
		except IntegrityError:
			abort(400, message="There is not any store with this store_id")
		except SQLAlchemyError:
			abort(500, message="An error occurred while inserting the item.")

		return item