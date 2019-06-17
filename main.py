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
	breed = ndb.StringProperty()
	specie = ndb.StringProperty()
	price = ndb.FloatProperty()
	stock = ndb.IntegerProperty()

class ProductSerializer(Schema):
	class Meta:
		fields = (
			"id","breed","specie","price","stock"
		)

product_schema = ProductSerializer()
products_schema = ProductSerializer(many=True)


@app.route('/products/create',methods = ['POST'])
def create_product():
	if not request.is_json:
		abort(400,"json only please")
	product = Product(
		id=request.json['id'],
		breed=request.json['breed'],
		specie=request.json['specie'],
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
	#if productid == None:
	#	return abort(400,"please provide a product id")
	try:
		query = Product.query(Product.id == productid)
		post = query.get()
		if post == None:
			return not_found("Product was not found")
		return jsonify(product_schema.dump(post).data)
	except Exception, e:
		return abort(500,e)

@app.route('/products/get/breed/<string:productbreed>')# breed
def get_product_by_breed(productbreed):
	# productid = int(request.args.get('id'))
	#if productbreed == None:
	#	return abort(400,"please provide a product breed")
	try:
		query = Product.query(Product.breed == productbreed)
		post = query.fetch()
		if post == None:
			return not_found("Product was not found")
		return jsonify(product_schema.dump(post).data)
	except Exception, e:
		return abort(500,e)

@app.route('/products/get/specie/<string:productspecie>')# specie
def get_product_by_specie(productspecie):
	# productid = int(request.args.get('id'))
	#if productspecie == None:
	#	return abort(400,"please provide a product breed")
	try:
		query = Product.query(Product.specie == productspecie)
		post = query.fetch()
		#print(post,file=sys.stdout)
		if post == None:
			return not_found("Product was not found")
		return jsonify({ productspecie: products_schema.dump(post).data})
#		return jsonify(product_schema.dump(post).data)
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
			if 'breed' in json:
				value.author = json['breed']
			if 'specie' in json:
				value.specie = json['specie']
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