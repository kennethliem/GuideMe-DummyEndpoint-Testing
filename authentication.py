from flask import Blueprint, request, Response, jsonify, request_started
from utils import (
    db_read,
    validate_user_input,
    generate_salt,
    generate_hash,
    db_write,
    validate_user,
)

authentication = Blueprint("authentication", __name__)

@authentication.route("/register", methods=["POST"])
def register_user():

    user = request.form

    if validate_user_input(
        "authentication", email=user['email'], password=user['password']
    ):
        password_salt = generate_salt()
        password_hash = generate_hash(user['password'], password_salt)

        if db_write(
            """INSERT INTO users (email, fullname, password_salt, password_hash) VALUES (%s, %s, %s, %s)""",
            (user['email'], user['fullname'], password_salt, password_hash),
        ):
            return jsonify({"error": False, "message": "User Created"})
        else:
            return jsonify({"error": True, "message": "User Not Created"})
    else:
        return jsonify({"error" : True, "message": "Email already taken"})


@authentication.route("/login", methods=["POST"])
def login_user():
    user = request.form

    return validate_user(user['email'], user['password'])

@authentication.route("/getdetail", methods=["GET"])
def getDetailUser():

    json_data = request.args
    user_id = json_data['user_id']

    data = db_read("""SELECT email, fullname, user_id FROM users WHERE user_id = %s""", (user_id,))

    return jsonify(data[0])

