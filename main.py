import os
from flask import Flask, request, jsonify
from hyundai_kia_connect_api import VehicleManager, ClimateRequestOptions
from hyundai_kia_connect_api.exceptions import AuthenticationError

app = Flask(__name__)

# =========================
# Environment Variables
# =========================
USERNAME = os.environ.get("Cherelle.jarman33@yahoo.com")
PASSWORD = os.environ.get("Jarman4375")
PIN = os.environ.get("4375")
SECRET_KEY = os.environ.get("Y9fYS9GaC5zn0MCoxMOmeYVd9sGYsN3S-13zm87StHk")
VEHICLE_ID = os.environ.get("VEHICLE_ID")

missing = []
if not USERNAME: missing.append("Cherelle.jarman33@yahoo.com")
if not PASSWORD: missing.append("Jarman4375")
if not PIN: missing.append("4375")
if not SECRET_KEY: missing.append("Y9fYS9GaC5zn0MCoxMOmeYVd9sGYsN3S-13zm87StHk")

if missing:
    raise ValueError(f"Missing variables: {', '.join(missing)}")

# =========================
# Vehicle Manager Setup
# =========================
# Reverting to direct, standard initialization parameters to fix the 500 import error
try:
    vehicle_manager = VehicleManager(
        region=3,  
        brand=1,   
        username=Cherelle.jarman33@yahoo.com,
        password=Jarman4375,
        pin=str(4375)
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
        return jsonify({"error": "
