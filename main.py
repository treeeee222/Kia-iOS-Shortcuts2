import os
from flask import Flask, request, jsonify
from hyundai_kia_connect_api import VehicleManager, ClimateRequestOptions

# This is the line Gunicorn is looking for
app = Flask(__name__)

# Environment Variables
USERNAME = os.environ.get("KIA_USERNAME")
PASSWORD = os.environ.get("KIA_PASSWORD")
PIN = os.environ.get("KIA_PIN")
SECRET_KEY = os.environ.get("SECRET_KEY")
VEHICLE_ID = os.environ.get("VEHICLE_ID")

# Initialize Vehicle Manager
vehicle_manager = VehicleManager(region=3, brand=1, username=USERNAME, password=PASSWORD, pin=str(PIN))

def authorize_request():
    return request.headers.get("Authorization") == SECRET_KEY

@app.route("/start_climate", methods=["POST"])
def start_climate():
    if not authorize_request():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json() or {}
    try:
        user_temp = int(data.get("temp", 72))
    except ValueError:
        user_temp = 72
    safe_temp = max(62, min(82, user_temp))
    try:
        vehicle_manager.check_and_refresh_token()
        vehicle_id = VEHICLE_ID or next(iter(vehicle_manager.vehicles.keys()))
        options = ClimateRequestOptions(set_temp=safe_temp, climate=True, heating=True)
        vehicle_manager.start_climate(vehicle_id, options)
        return jsonify({"status": "Success", "temp": safe_temp}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/unlock_car", methods=["POST"])
def unlock_car():
    if not authorize_request():
        return jsonify({"error": "Unauthorized"}), 401
    try:
        vehicle_manager.check_and_refresh_token()
        vehicle_id = VEHICLE_ID or next(iter(vehicle_manager.vehicles.keys()))
        vehicle_manager.unlock(vehicle_id)
        return jsonify({"status": "Unlocked"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
