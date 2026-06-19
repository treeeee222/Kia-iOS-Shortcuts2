import os
from flask import Flask, request, jsonify
from hyundai_kia_connect_api import VehicleManager, ClimateRequestOptions, Region, Brand
from hyundai_kia_connect_api.exceptions import AuthenticationError

# This MUST be at the top level on line 7 with no indentation
app = Flask(__name__)

# =========================
# Environment Variables
# =========================
USERNAME = os.environ.get("KIA_USERNAME")
PASSWORD = os.environ.get("KIA_PASSWORD")
PIN = os.environ.get("KIA_PIN")
SECRET_KEY = os.environ.get("SECRET_KEY")
VEHICLE_ID = os.environ.get("VEHICLE_ID")

missing = []
if not USERNAME: missing.append("KIA_USERNAME")
if not PASSWORD: missing.append("KIA_PASSWORD")
if not PIN: missing.append("KIA_PIN")
if not SECRET_KEY: missing.append("SECRET_KEY")

if missing:
    raise ValueError(f"Missing variables: {', '.join(missing)}")

# =========================
# Vehicle Manager Setup
# =========================
try:
    vehicle_manager = VehicleManager(
        region=Region.USA,  
        brand=Brand.KIA,   
        username=USERNAME,
        password=PASSWORD,
        pin=str(PIN)
    )
except Exception as init_error:
    print(f"Failed to initialize VehicleManager: {init_error}")

# =========================
# Helper Functions
# =========================
def authorize_request():
    return request.headers.get("Authorization") == SECRET_KEY

def ensure_authenticated():
    try:
        vehicle_manager.check_and_refresh_token()
    except AuthenticationError as e:
        raise AuthenticationError("Kia authentication failed. Check 2FA.") from e

def refresh_and_sync():
    ensure_authenticated()
    vehicle_manager.update_all_vehicles_with_cached_state()

def get_vehicle_id():
    if VEHICLE_ID:
        return VEHICLE_ID
    vehicles = vehicle_manager.vehicles
    if not vehicles:
        raise ValueError("No vehicles found.")
    return next(iter(vehicles.keys()))

@app.before_request
def log_request_info():
    print(f"Incoming request: {request.method} {request.path}")

# =========================
# Routes
# =========================
@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "OK", "service": "Kia Vehicle Control API"}), 200

@app.route("/auth_status", methods=["GET"])
def auth_status():
    if not authorize_request():
        return jsonify({"error": "Unauthorized"}), 403
    try:
        ensure_authenticated()
        return jsonify({"status": "authenticated"}), 200
    except AuthenticationError as e:
        return jsonify({"status": "authentication_failed", "message": str(e)}), 401

@app.route("/list_vehicles", methods=["GET"])
def list_vehicles():
    if not authorize_request():
        return jsonify({"error": "Unauthorized"}), 403
    try:
        refresh_and_sync()
        vehicles = vehicle_manager.vehicles
        if not vehicles:
            return jsonify({"error": "No vehicles found"}), 404
        vehicle_list = [{"name": v.name, "id": v.id, "model": v.model, "year": v.year} for v in vehicles.values()]
        return jsonify({"status": "success", "vehicles": vehicle_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/start_climate", methods=["POST"])
def start_climate():
    if not authorize_request():
        return jsonify({"error": "Unauthorized"}), 403
    try:
        refresh_and_sync()
        vehicle_id = get_vehicle_id()
        climate_options = ClimateRequestOptions(set_temp=72, duration=10)
        result = vehicle_manager.start_climate(vehicle_id, climate_options)
        return jsonify({"status": "climate_started", "result": str(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stop_climate", methods=["POST"])
def stop_climate():
    if not authorize_request():
        return jsonify({"error": "Unauthorized"}), 403
    try:
        refresh_and_sync()
        vehicle_id = get_vehicle_id()
        result = vehicle_manager.stop_climate(vehicle_id)
        return jsonify({"status": "climate_stopped", "result": str(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/unlock_car", methods=["POST"])
def unlock_car():
    if not authorize_request():
        return jsonify({"error": "Unauthorized"}), 403
    try:
        refresh_and_sync()
        vehicle_id = get_vehicle_id()
        result = vehicle_manager.unlock(vehicle_id)
        return jsonify({"status": "car_unlocked", "result": str(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/lock_car", methods=["POST"])
def lock_car():
    if not authorize_request():
        return jsonify({"error": "Unauthorized"}), 403
    try:
        refresh_and_sync()
        vehicle_id = get_vehicle_id()
        result = vehicle_manager.lock(vehicle_id)
        return jsonify({"status": "car_locked", "result": str(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
