#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(jsonify(bakeries), 200)

@app.route('/bakeries/<int:id>')
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()
    if bakery:
        bakery_serialized = bakery.to_dict()
        return make_response(jsonify(bakery_serialized), 200)
    else:
        return make_response(jsonify({"error": "Bakery not found"}), 404)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response(jsonify(baked_goods_by_price_serialized), 200)

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    if most_expensive:
        most_expensive_serialized = most_expensive.to_dict()
        return make_response(jsonify(most_expensive_serialized), 200)
    else:
        return make_response(jsonify({"error": "No baked goods found"}), 404)

# POST route to create a new baked good
@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    name = request.form.get('name')
    bakery_id = request.form.get('bakery_id')
    price = request.form.get('price')

    if not name or not bakery_id or not price:
        return make_response(jsonify({"error": "Name, bakery_id, and price are required"}), 400)

    new_baked_good = BakedGood(name=name, bakery_id=bakery_id, price=price)
    db.session.add(new_baked_good)
    db.session.commit()

    return make_response(jsonify(new_baked_good.to_dict()), 201)

# PATCH route to update the name of a bakery
@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery_name(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return make_response(jsonify({"error": "Bakery not found"}), 404)

    name = request.form.get('name')
    if not name:
        return make_response(jsonify({"error": "Name is required"}), 400)

    bakery.name = name
    db.session.commit()

    return make_response(jsonify(bakery.to_dict()), 200)

# DELETE route to delete a baked good
@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get(id)
    if not baked_good:
        return make_response(jsonify({"error": "Baked good not found"}), 404)

    db.session.delete(baked_good)
    db.session.commit()

    return make_response(jsonify({"message": "Baked good successfully deleted"}), 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)