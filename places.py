from flask import Blueprint, request, Response, jsonify, request_started
from utils import db_read, db_write, token_required
from flask_jwt import JWT, jwt_required, current_identity

places = Blueprint("places", __name__)

@places.route("/allplaces", methods=["GET"])
def getAllPlaces():
    data = db_read("""SELECT name, photo_url FROM places""")
    
    return jsonify({"error": False, "message": "Places fetched successfully", "listPlaces": data})

@places.route("/place", methods=["GET"])
@token_required
def getDetailPlaces():

    json_data = request.args
    place_name = json_data['name']

    data = db_read("""SELECT * FROM places WHERE name = %s""", (place_name,))

    return jsonify(data[0])

@places.route("/albums", methods=["GET"])
def getPlacesAlbums():

    json_data = request.args
    place_id = json_data['place_id']

    data = db_read("""SELECT * FROM places_album WHERE place_id = %s""", (place_id,))

    return jsonify({"error": False, "message": "Photo fetched successfully", "listPhoto": data})

@places.route("/articles", methods=["GET"])
def getPlacesArticle():

    json_data = request.args
    place_id = json_data['place_id']

    data = db_read("""SELECT * FROM article WHERE place_id = %s""", (place_id,))

    return jsonify({"error": False, "message": "Article fetched successfully", "listArticle": data})

@places.route("/visithistory", methods=["GET"])
@token_required
def getUserVisitHistory():

    json_data = request.args
    user_id = json_data["user_id"]

    data = db_read("""SELECT * FROM users_visit_history INNER JOIN places ON users_visit_history.place_id = places.place_id WHERE user_id = %s""", (user_id,))

    return jsonify({"error": False, "message": "History fetched successfully", "listHistory": data})

@places.route("/deletehistory", methods=["DELETE"])
@token_required
def deleteUserVisitHistory():

    json_data = request.args
    user_id = json_data["user_id"]

    state = db_write("""DELETE FROM users_visit_history WHERE user_id = %s""", (user_id,))

    if state:
        return jsonify({"error": False, "message": "Success"})
    else:
        return jsonify({"error": True, "message": "Error deleting history"})
