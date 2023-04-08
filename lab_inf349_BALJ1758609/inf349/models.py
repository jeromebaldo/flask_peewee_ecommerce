import os
import click
from flask.cli import with_appcontext
from peewee import Model, SqliteDatabase, AutoField, CharField, IntegerField, BooleanField, FloatField
from playhouse.sqlite_ext import *

def get_db_path():
    return os.environ.get('DATABASE', './db.sqlite')

class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(get_db_path())

class Product(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField()
    description = CharField()
    image = CharField()
    weight = IntegerField()
    price = FloatField()
    in_stock = BooleanField()

class Order(BaseModel):
    id = AutoField(primary_key=True)
    total_price = IntegerField(default=0.0)
    email = CharField(null=True)
    credit_card = JSONField(default={})
    shipping_information = JSONField(default={})
    paid = BooleanField(default=False)
    transaction = JSONField(default={})
    product = JSONField(default={})
    shipping_price= FloatField(default=0)
    
    
    #CALCUL DU total_price 
    def to_totalPrice(self, price, quantity):
        self.total_price = price*quantity
        
    #CALCUL DU shipping_price multiplie le poid du produit avec quantite 
    #selon la fourchette ajoute les frais d'expédition 
    def to_shippingPrice(self,weight,quantity):
        poids_total = weight*quantity
        if poids_total < 500:
            self.shipping_price = 5
        if poids_total >= 500 and poids_total < 2000:
            self.shipping_price = 10
        if poids_total >= 2000:
            self.shipping_price = 25
        self.shipping_price = self.shipping_price + self.total_price

@click.command("init-db")
@with_appcontext
def init_db_command():
    database = SqliteDatabase(get_db_path())
    database.create_tables([Product, Order])
    click.echo("Initialized the database.")

def init_app(app):
    app.cli.add_command(init_db_command)