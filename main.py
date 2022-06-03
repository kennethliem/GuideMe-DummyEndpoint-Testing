# app.py
from flask import Flask, Blueprint, request, Response, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL

app = Flask(__name__)

# app.config['MYSQL_HOST'] = "10.11.208.3"
# app.config['MYSQL_UNIX_SOCKET'] = "/cloudsql/guideme-capstoneproject:asia-southeast2:guideme-bangkitcapstone"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "guideme"
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

db = MySQL(app)

from authentication import authentication
from places import places
from detection import detection

#TEST
@app.route('/')
def hello():
    return 'Hello World!'

app.register_blueprint(authentication, url_prefix="/api/auth")

app.register_blueprint(places, url_prefix="/api/get")

app.register_blueprint(detection, url_prefix="/api/detection")

