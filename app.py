from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Allow requests from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Helper ----------

def to_bool(value):
    return str(value).strip().lower() in ("true", "1", "yes", "on")


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):

    # ---------------- Layer 1 : Defaults ----------------
    config = {
        "port": 8000,
        "workers": 1,
        "debug": False,
        "log_level": "info",
        "api_key": "default-secret-000",
    }

    # ---------------- Layer 2 : config.development.yaml ----------------
    config.update({
        "workers": 1,
        "debug": False,
        "log_level": "warning",
    })

    # ---------------- Layer 3 : .env ----------------
    config["port"] = 8937
    config["workers"] = 11

    # ---------------- Layer 4 : OS Environment ----------------
    if os.getenv("APP_PORT"):
        config["port"] = int(os.getenv("APP_PORT"))

    if os.getenv("APP_API_KEY"):
        config["api_key"] = os.getenv("APP_API_KEY")

    # ---------------- CLI Overrides ----------------
    for item in set:

        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        # Alias
        if key == "NUM_WORKERS":
            key = "workers"

        if key in ("port", "workers"):
            config[key] = int(value)

        elif key == "debug":
            config[key] = to_bool(value)

        else:
            config[key] = value

    # Never expose secret
    config["api_key"] = "****"

    return config
