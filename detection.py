import json
from tkinter import Place
import tensorflow as tf
from PIL import Image
import numpy as np
from flask import Blueprint, request, Response, jsonify, request_started
import io
from utils import db_read, db_write, token_required


def load_model():
	
	global model
	model = tf.keras.applications.ResNet50(weights="imagenet")

def prepare_dataset(image, target):

	if image.mode != "RGB":
		image= image.convert("RGB")

	image = image.resize(target)
	image = tf.keras.preprocessing.image.img_to_array(image)
	image = np.expand_dims(image, axis=0)
	image = tf.keras.applications.imagenet_utils.preprocess_input(image)

	return image

detection = Blueprint("detection", __name__)

@detection.route("/", methods=["POST"])
@token_required
def predict():

	data = {"success":False}

	if request.method == "POST":
		if request.files.get("image"):

			image = request.files["image"].read()
			image = Image.open(io.BytesIO(image))

			image = prepare_dataset(image, target=(224,224))

			preds = model.predict(image)
			results = tf.keras.applications.imagenet_utils.decode_predictions(preds)

			data["predictions"] = []

			for (_, label, prob) in results[0]:
				r = {"label": label, "probablity": float(prob)}
				data["predictions"].append(r)

			data["success"] = True

	return jsonify(data)

@detection.route("/dummy/guideme", methods=["POST"])
@token_required
def dummyEndpointGuideMe():

	data = {"error": True}

	if request.method == "POST":
		user_id = request.args
		if request.files.get("image"):
			data["error"] = False
			data["message"] = "Success"
			data["place_name"] = "Candi Borobudur"
			place = db_read("""SELECT * FROM places WHERE name = %s""", (data["place_name"],))
			place_id = place[0]["place_id"]
			user_id = int(user_id["user_id"])
			db_write("""INSERT INTO users_visit_history (user_id, place_id) VALUES (%s, %s)""",(user_id, place_id),)
		else:
			data["error"] = True
			data["message"] = "Can't get Image"
	else:
		data["error"] = True
		data["message"] = "Wrong Method"
    
	return jsonify(data)

@detection.route("/dummy/chanity", methods=["POST"])
@token_required
def dummyEndpointChanity():

	data = {
		"success":False
		}
	result = {
		"Openness" : 70,
		"Conscientiousness" : 38,
		"Extraversion" : 48,
		"Agreeableness" : 51,
		"Neuroticism" : 60
	}

	if request.method == "POST":
		data["success"] = True
		data["result"] = result
    
	return jsonify(data)
