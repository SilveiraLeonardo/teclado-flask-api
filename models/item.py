from db import db

class ItemModel(db.Model):
	__tablename__ = "items"

	# by default postgres will make id auto-incrementing
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=False, nullable=False)
	description = db.Column(db.String)
	price = db.Column(db.Float(precision=2), unique=False, nullable=False)
	store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), unique=False, nullable=False)
	# the stores table is used by the StoreModel class
	# we can populate the store variable with the store object matching the id
	store = db.relationship("StoreModel", back_populates="items")
	tags = db.relationship("TagModel", back_populates="items", secondary="items_tags")
