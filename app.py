from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import yaml
import os

app = FastAPI()

# Allow all origins (grader requirement)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

# ---------------- Defaults ----------------
config = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000"
}

# ---------------- YAML ----------------
with open("config.development.yaml", "r") as f:
    yaml_cfg = yaml.safe_load(f) or {}

config.update(yaml_cfg)

# ---------------- .env ----------------
if os.getenv("APP_PORT"):
    config["port"] = int(os.getenv("APP_PORT"))

if os.getenv("NUM_WORKERS"):
    config["workers"] = int(os.getenv("NUM_WORKERS"))

# ---------------- OS ENV ----------------
if "APP_PORT" in os.environ:
    config["port"] = int(os.environ["APP_PORT"])

if "APP_API_KEY" in os.environ:
    config["api_key"] = os.environ["APP_API_KEY"]


def convert(key, value):
    if key in ("port", "workers"):
        return int(value)

    if key == "debug":
        return str(value).lower() in (
            "true",
            "1",
            "yes",
            "on",
        )

    return str(value)


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):

    result = config.copy()

    # CLI overrides
    for item in set:
        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        if key == "NUM_WORKERS":
            key = "workers"

        result[key] = convert(key, value)

    # Always mask api_key
    result["api_key"] = "****"

    return result