# =========================
# Environment Variables
# =========================
# This code now looks for "Keys" (labels) on your server, 
# not your personal information.
USERNAME = os.environ.get("KIA_USERNAME")
PASSWORD = os.environ.get("KIA_PASSWORD")
PIN = os.environ.get("KIA_PIN")
SECRET_KEY = os.environ.get("SECRET_KEY")
VEHICLE_ID = os.environ.get("VEHICLE_ID")

# This ensures the code stops if you forgot to add the keys on Render
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
