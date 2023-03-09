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
    miles = FloatField(Null=True)
    km = FloatField(required=True,Null=True)
    location = StringField(Null=True)
    open = StringField(required=True,Null=True)
    close = StringField(required=True,Null=True)


class Brevet(Document):
    """
    A MongoEngine document containing:
		brev_dist: MongoEngine float field, required
		begin_date: MongoEngine string field, required
		checkpoints: MongoEngine list field of Checkpoints, required
    """
    brev_dist = FloatField(required=True, Null=True) 
    begin_date = StringField(required=True,Null=True)
    checkpoints = EmbeddedDocumentListField(Checkpoint,Null=True)