import peewee

from models.base_model import (BaseModel)

class UserModel(BaseModel):
    user_id = peewee.AutoField(primary_key=True)
    email = peewee.CharField(max_length=50)
    name = peewee.CharField(max_length=100)
    username = peewee.CharField(max_length=50, unique=True)
    password = peewee.CharField(max_length=255)

    class Meta:
        table_name = 'users'