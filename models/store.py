from db import db

class StoreModel(db.Model):
	__tablename__ = "stores"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=True, nullable=False)
	# with the relatioship associated with the ItemModel class, StoreModel
	# can easily see the item objects associated with each store object
	# lazy="dynamic" tells the database to not fetch the items before we tell
	# her to do so
	# cascade: if a store is deleted, deletes all its products
	items = db.relationship("ItemModel", back_populates="store", lazy="dynamic", cascade="all, delete")
	tags = db.relationship("TagModel", back_populates="store", lazy="dynamic", cascade="all, delete")
	