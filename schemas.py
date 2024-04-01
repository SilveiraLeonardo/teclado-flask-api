from marshmallow import Schema, fields

class PlainItemSchema(Schema):
	# id field will never come in a request payload, it is only returned
	# load_only would be the opposite
	id = fields.Int(dump_only=True)
	# this field is required and must be in the payload
	# required fields are required in both ends, receiving and sending data
	name = fields.Str(required=True)
	price = fields.Float(required=True)

class PlainStoreSchema(Schema):
	id = fields.Int(dump_only=True)
	name = fields.Str(required=True)

class PlainTagSchema(Schema):
	id = fields.Int(dump_only=True)
	name = fields.Str(required=True)

class ItemUpdateSchema(Schema):
	# both fields are optional
	name = fields.Str()
	price = fields.Float()	
	store_id = fields.Int()

class ItemSchema(PlainItemSchema):
	store_id = fields.Int(required=True, load_only=True)
	# the store object from the item-store relationship
	store = fields.Nested(PlainStoreSchema(), dump_only=True)
	tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

class StoreSchema(PlainStoreSchema):
	items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
	tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

class StoreUpdateSchema(Schema):
	name = fields.Str(required=True)

class TagSchema(PlainTagSchema):
	store_id = fields.Int(load_only=True)
	store = fields.Nested(PlainStoreSchema(), dump_only=True)
	items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)

class TagAndItemSchema(Schema):
	message = fields.Str()
	item = fields.Nested(TagSchema)
	item = fields.Nested(ItemSchema)

class UserSchema(Schema):
	id = fields.Int(dump_only=True)
	username = fields.Str(required=True)
	password = fields.Str(required=True, load_only=True)



# we need to have the Plain schemas so that we can reference them in the final schemas
# otherwise one of them would not be defined at the point of passing as an argument to the other:
# ItemSchema would reference StoreScheme, but StoreScheme would not be 
# referenced yet