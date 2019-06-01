from __future__ import print_function
from flask import Flask, request, jsonify, abort, render_template
from google.appengine.ext import ndb
from marshmallow import Schema, fields
import werkzeug
import logging
import sys

app = Flask(__name__)
app.debug = True

class Product(ndb.Model):
	id = ndb.IntegerProperty()
	name = ndb.StringProperty()
	category = ndb.StringProperty()
	price = ndb.FloatProperty()
	stock = ndb.IntegerProperty()

class ProductSerializer(Schema):
	class Meta:
		fields = (
			"id","name","category","price","stock"
		)

product_schema = ProductSerializer()
products_schema = ProductSerializer(many=True)


@app.route('/products/create',methods = ['POST'])
def create_product():
	if not request.is_json:
		abort(400,"json only please")
	product = Product(
		id=request.json['id'],
		name=request.json['name'],
		category=request.json['category'],
		price=request.json['price'],
		stock=request.json['stock'])
	product.put()
	return jsonify(product_schema.dump(product).data)

@app.route('/products/fetch')
def fetch_products():
	products = Product.query().fetch()
	return jsonify({ 'products': products_schema.dump(products).data})

@app.route('/products/get/id/<int:productid>')
def get_product_by_id(productid):
	# productid = int(request.args.get('id'))
	if productid == None:
		return abort(400,"please provide a product id")
	try:
		query = Product.query(Product.id == productid)
		post = query.get()
		if post == None:
			return not_found("Product was not found")
		return jsonify(product_schema.dump(post).data)
	except Exception, e:
		return abort(500,e)

@app.route('/products/get/name/<string:productname>')
def get_product_by_name(productname):
	# productid = int(request.args.get('id'))
	if productname == None:
		return abort(400,"please provide a product name")
	try:
		query = Product.query(Product.name == productname)
		post = query.get()
		if post == None:
			return not_found("Product was not found")
		return jsonify(product_schema.dump(post).data)
	except Exception, e:
		return abort(500,e)

@app.route('/products/get/category/<string:productcategory>')
def get_product_by_category(productcategory):
	# productid = int(request.args.get('id'))
	if productcategory == None:
		return abort(400,"please provide a product name")
	try:
		query = Product.query(Product.category == productcategory)
		post = query.get()
		if post == None:
			return not_found("Product was not found")
		return jsonify(product_schema.dump(post).data)
	except Exception, e:
		return abort(500,e)

@app.route('/products/delete', methods = ['POST'])
def delete_product():
	try:
		query = Product.query(Product.id == request.json['id'])
		for q in query:
			q.key.delete()
		return jsonify({'status':'ok'}), 200
	except Exception, e:
		return abort(500, e)

@app.route('/products/update', methods = ['POST'])
def update_product():
	if not request.is_json:
		abort(400,"json only please")
	try:
		query = Product.query(Product.id == request.json['id'])
		for q in query:
			value = q.key.get()
			if value == None:
				return not_found("Product was not found")
			json = request.json or {}
			if 'name' in json:
				value.author = json['name']
			if 'category' in json:
				value.category = json['category']
			if 'price' in json:
				value.price = json['price']
			if 'stock' in json:
				value.stock = json['stock']
			value.put()
			return jsonify(product_schema.dump(value).data)
	except Exception, e:
		return abort(400,e)

@app.route('/')
def index():
	products = Product.query().fetch()
	return render_template('index.html',products=products)


def not_found(message='resource was not found'):
    return jsonify({
        'http_status': 404,
        'code': 'not_found',
        'message': message
    }), 404

@app.errorhandler(werkzeug.exceptions.BadRequest)
def bad_request(e):
    return jsonify({
        'http_status': 400,
        'code': 'bad_request',
        'message': '{}'.format(e)
    }), 400

@app.errorhandler(werkzeug.exceptions.InternalServerError)
def application_error(e):
    logging.exception(e)
    return jsonify({
        'http_status': 500,
        'code': 'internal_server_error',
        'message': '{}'.format(e.description)
    }), 500