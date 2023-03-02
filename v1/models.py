import os
from peewee import Model, SqliteDatabase, AutoField, CharField, IntegerField, BooleanField

def get_db_path():
    return os.environ.get('DATABASE', './dbLaboWeb.sqlite')

class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(get_db_path())

class Product(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField()
    description = CharField()
    price = IntegerField()
    in_stock = BooleanField()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'in_stock': self.in_stock
        }
