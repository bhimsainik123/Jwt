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

# MongoDB request logging is optional so a missing Vercel env var cannot crash
# the entire serverless function during import/startup.
MONGO_URI = os.getenv("MONGO_URI")
request_logs = None

if MONGO_URI:
    try:
        mongo_client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            maxPoolSize=50,
            minPoolSize=0,
        )
        logs_db = mongo_client[os.getenv("MONGO_DB", "jwt_api")]
        request_logs = logs_db["api_requests"]
        logger.info("MongoDB request logging configured")
    except Exception as exc:
        logger.warning("MongoDB setup failed; request logging disabled: %s", exc)
else:
    logger.warning("MONGO_URI is not configured; MongoDB request logging is disabled")


@app.before_request
def start_request_timer():
    g.request_started = time.perf_counter()


@app.after_request
def save_request_log(response):
    if request_logs is None:
        return response

    try:
        elapsed_ms = round((time.perf_counter() - getattr(g, "request_started", time.perf_counter())) * 1000, 2)
        args = request.args.to_dict(flat=True)
        # Do not persist passwords or generated/access tokens in request logs.
        args.pop("password", None)
        args.pop("token", None)
        args.pop("access_token", None)

        forwarded_for = request.headers.get("X-Forwarded-For")
        ip = forwarded_for.split(",", 1)[0].strip() if forwarded_for else request.remote_addr

        request_logs.insert_one({
            "timestamp": datetime.now(timezone.utc),
            "method": request.method,
            "path": request.path,
            "query": args,
            "uid": request.args.get("uid"),
            "status_code": response.status_code,
            "response_size": response.calculate_content_length(),
            "duration_ms": elapsed_ms,
            "ip": ip,
            "user_agent": request.headers.get("User-Agent", ""),
        })
    except Exception as exc:
        # Logging must never turn a successful API response into a 500.
        logger.warning("MongoDB request logging failed: %s", exc)
    return response


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "service": "JWT Token Generator API",
        "version": "OB55",
    })


@app.route("/token", methods=["GET"])
def get_responses():
    uid = request.args.get("uid")
    password = request.args.get("password")

    if not uid or not password:
        return jsonify({"message": "uid and password are required"}), 400

    # Stable cache key: repeated requests can actually hit the in-memory cache.
    cache_key = f"token_{uid}_{password}"
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached), int(cached.get("status_code", 200))

    response = process_token(uid, password)
    status_code = int(response.get("status_code", 500))
    cache.set(cache_key, response, timeout=3600)
    return jsonify(response), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5002")), debug=False)
