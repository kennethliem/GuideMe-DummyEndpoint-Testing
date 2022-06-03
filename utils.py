from functools import wraps
from flask import jsonify, request
import pymysql
from main import db
import os
import jwt
from settings import JWT_SECRET_KEY
from flask_mysqldb import MySQLdb
from hashlib import pbkdf2_hmac

def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       token = None
       if 'x-access-tokens' in request.headers:
           token = request.headers['x-access-tokens']
 
       if not token:
           return jsonify({'message': 'a valid token is missing'})
       try:
            jwt.decode(token, JWT_SECRET_KEY, algorithm="HS256")
       except:
           return jsonify({'message': 'token is invalid'})
 
       return f(*args, **kwargs)
   return decorator

def db_read(query, params=None):
    cursor = db.connection.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    entries = cursor.fetchall()
    cursor.close()
    content = []

    for entry in entries:
        content.append(entry)

    return content

def db_write(query, params):
    cursor = db.connection.cursor()
    try:
        cursor.execute(query, params)
        db.connection.commit()
        cursor.close()

        return True

    except pymysql._exceptions.IntegrityError:
        cursor.close()
        return False

def generate_salt():
    salt = os.urandom(16)
    return salt.hex()

def generate_hash(plain_password, password_salt):
    password_hash = pbkdf2_hmac(
        "sha256",
        b"%b" % bytes(plain_password, "utf-8"),
        b"%b" % bytes(password_salt, "utf-8"),
        10000,
    )
    return password_hash.hex()

def generate_token(content):
    encoded_content = jwt.encode(content, JWT_SECRET_KEY, algorithm="HS256")
    token = str(encoded_content).split("'")[1]
    # token = encoded_content

    return token

def validate_user_input(input_type, **kwargs):
    if input_type == "authentication":
        current_user = db_read("""SELECT * FROM users WHERE email = %s""", (kwargs["email"],))
        if len(kwargs["email"]) <= 255 and len(kwargs["password"]) <= 255:
            if len(current_user) == 0:
                return True
            else:
                return False
        else:
            return False

def validate_user(email, password):
    current_user = db_read("""SELECT * FROM users WHERE email = %s""", (email,))

    if len(current_user) == 1:
        saved_password_hash = current_user[0]["password_hash"]
        saved_password_salt = current_user[0]["password_salt"]
        password_hash = generate_hash(password, saved_password_salt)

        if password_hash == saved_password_hash and current_user[0]["email"] == email:
            user_id = current_user[0]["user_id"]
            user_fullname = current_user[0]["fullname"]
            user_email = current_user[0]["email"]
            token = generate_token({"id": user_id})
            data = {"error": False, "message": "Login Success", "loginResult":{"token": token, "userid": user_id, "email": user_email, "fullname": user_fullname}}

            return jsonify(data)

        elif current_user[0]["email"] == email and password_hash != saved_password_hash:
            return jsonify({"error": True, "message": "Wrong Password"})

        else:
            return jsonify({"error": True, "message": "Login Failed"})

    else:
        return jsonify({"error": True, "message": "Account not found"})
