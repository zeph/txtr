from flask import Flask
from mongokit import Connection, Document
import json

# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

# create the little application object
app = Flask(__name__)
app.config.from_object(__name__)

# connect to the database
connection = Connection(app.config['MONGODB_HOST'],
						app.config['MONGODB_PORT'])
book = connection['test_reaktor_stg_it'].book
cats = connection['test_reaktor_stg_it'].category

class Book(Document):
	structure = {
		'documentID': unicode,
	}
	use_dot_notation = True
	def __repr__(self):
		return '<Book %r>' % (self.documentID)

# register the Book document with our current connection
connection.register([Book])

@app.route('/')
def index():
	return "Got to /book or /category ..."

@app.route('/book')
def get_book():
	b = book.find_one({},{"_id":0})
	return json.dumps(b, sort_keys=True, indent=4)

@app.route('/category')
def get_category():
	cat = cats.find_one({},{"_id":0})
	return json.dumps(cat, sort_keys=True, indent=4)

if __name__ == "__main__":
	app.debug = True
	app.run()