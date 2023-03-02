from flask import Flask, jsonify, request
from flask.cli import with_appcontext
from models import Product, get_db_path
from peewee import SqliteDatabase
import click

app = Flask(__name__)
app.config.from_mapping(
    DATABASE=get_db_path()
)

@click.command("init-db")
@with_appcontext
def init_db_command():
    database = SqliteDatabase(get_db_path())
    database.create_tables([Product])
    click.echo("Initialized the database.")

def init_app(app):
    app.cli.add_command(init_db_command)

init_app(app)

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.select()
    product_list = [product.to_dict() for product in products]
    return jsonify(product_list)

@app.route('/products', methods=['POST'])
def create_product():
    product_data = request.get_json()
    product = Product.create(
        name=product_data['name'],
        description=product_data['description'],
        price=product_data['price'],
        in_stock=product_data['in_stock']
    )
    return jsonify(product.to_dict())

if __name__ == '__main__':
    app.run(debug=True)
