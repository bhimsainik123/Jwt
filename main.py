from flask import Flask, jsonify, request, g
from flask_caching import Cache
from app.utils.response import process_token
from colorama import init
from urllib3.exceptions import InsecureRequestWarning
import warnings
import time
from dotenv import load_dotenv
import os
import logging
from datetime import datetime, timezone
from pymongo import MongoClient

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=InsecureRequestWarning)
init(autoreset=True)

app = Flask(__name__)
cache = Cache(app, config={"CACHE_TYPE": "simple"})

# Request logs are stored in MongoDB. Passwords and generated tokens are never logged.
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable is required")
mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
logs_db = mongo_client[os.getenv("MONGO_DB", "jwt_api")]
request_logs = logs_db["api_requests"]


@app.before_request
def start_request_timer():
    g.request_started = time.time()


@app.after_request
def save_request_log(response):
    try:
        elapsed_ms = round((time.time() - getattr(g, "request_started", time.time())) * 1000, 2)
        args = request.args.to_dict(flat=True)
        # Never persist credentials or tokens from query parameters.
        args.pop("password", None)
        args.pop("token", None)
        args.pop("access_token", None)

        request_logs.insert_one({
            "timestamp": datetime.now(timezone.utc),
            "method": request.method,
            "path": request.path,
            "query": args,
            "uid": request.args.get("uid"),
            "status_code": response.status_code,
            "response_size": response.calculate_content_length(),
            "duration_ms": elapsed_ms,
            "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
            "user_agent": request.headers.get("User-Agent", ""),
        })
    except Exception as exc:
        logger.error("MongoDB request logging failed: %s", exc)
    return response


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "service": "JWT Token Generator API",
        "version": "OB55"
    })


@app.route("/token", methods=["GET"])
def get_responses():
    uid = request.args.get("uid")
    password = request.args.get("password")

    if uid and password:
        cache_key = f"token_{uid}_{password}_{int(time.time())}"
        response = process_token(uid, password)
        status_code = int(response.get("status_code", 500))
        cache.set(cache_key, response, timeout=3600)
        return jsonify(response), status_code

    return jsonify({"message": "uid and password are required"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5002")), debug=False)
