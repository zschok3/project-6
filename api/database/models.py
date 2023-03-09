from mongoengine import *


class Checkpoint(EmbeddedDocument):
    """
    A MongoEngine EmbeddedDocument containing:
    miles: MongoEngine float field, optional, (checkpoint distance in miles),
    km: MongoEngine float field, required, (checkpoint distance in kilometers),
		location: MongoEngine string field, optional, (checkpoint location name),
		open_time: MongoEngine string field, required, (checkpoint opening time),
		close_time: MongoEngine string field, required, (checkpoint closing time).
    """
    miles = FloatField()
    km = FloatField(required=True)
    location = StringField()
    open = StringField(required=True)
    close = StringField(required=True)


class Brevet(Document):
    """
    A MongoEngine document containing:
		brev_dist: MongoEngine float field, required
		begin_date: MongoEngine string field, required
		checkpoints: MongoEngine list field of Checkpoints, required
    """
    brev_dist = FloatField(required=True) 
    begin_date = StringField(required=True)
    checkpoints = EmbeddedDocumentListField(Checkpoint)