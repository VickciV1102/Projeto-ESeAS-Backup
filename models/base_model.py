from peewee import (Model)
from db.database import db_proxy


class BaseModel(Model):
    class Meta:
        database = db_proxy