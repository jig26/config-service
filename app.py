from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import yaml
import os
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent

load_dotenv(BASE_DIR / ".env")


def to_bool(value):
    return str(value).lower() in ["true", "1", "yes", "on"]


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):

    config = {
        "port": 8000,
        "workers": 1,
        "debug": False,
        "log_level": "info",
        "api_key": "default-secret-000"
    }

    # YAML
    yaml_file = BASE_DIR / "config.development.yaml"

    if yaml_file.exists():
        with open(yaml_file, "r") as f:
            config.update(yaml.safe_load(f) or {})

    # .env
    if os.getenv("APP_PORT"):
        config["port"] = int(os.getenv("APP_PORT"))

    if os.getenv("NUM_WORKERS"):
        config["workers"] = int(os.getenv("NUM_WORKERS"))

    # OS env
    if os.environ.get("APP_PORT"):
        config["port"] = int(os.environ["APP_PORT"])

    if os.environ.get("APP_API_KEY"):
        config["api_key"] = os.environ["APP_API_KEY"]

    # CLI overrides
    for item in set:

        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        if key == "NUM_WORKERS":
            key = "workers"

        if key in ["port", "workers"]:
            config[key] = int(value)

        elif key == "debug":
            config[key] = to_bool(value)

        else:
            config[key] = value

    config["api_key"] = "****"

    return config
