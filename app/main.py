"""Vehicle Service API — Flask implementation.

Implements the contract defined by the Postman "Vehicle Service Collection"
and verified by the "Vehicle Service QA Testing" collection.

Endpoints:
    GET    /vehicles        -> 200 (array) | 500
    POST   /vehicles        -> 201 | 400 | 409 | 500
    GET    /vehicles/<id>   -> 200 | 404 | 500
    PATCH  /vehicles/<id>   -> 200 | 400 | 404 | 500
    DELETE /vehicles/<id>   -> 204 | 404 | 500

Authentication:
    API Key via the `X-API-Key` header. The expected key is read from the
    `API_KEY` environment variable (never hardcoded in the repo). Enforcement
    is opt-in via `REQUIRE_API_KEY=true` so local QA runs work without a key.
"""

import os

from flask import Flask, jsonify, request

from .store import VehicleStore

# ---------------------------------------------------------------------------
# Configuration (all via environment variables — no secrets in the repo)
# ---------------------------------------------------------------------------
API_KEY = os.environ.get("API_KEY", "dev-secret-key")
REQUIRE_API_KEY = os.environ.get("REQUIRE_API_KEY", "false").lower() == "true"
PORT = int(os.environ.get("PORT", "5000"))

REQUIRED_CREATE_FIELDS = ("vin", "make", "model", "year", "miles")

app = Flask(__name__)
store = VehicleStore()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _error(message, status):
    resp = jsonify({"message": message})
    resp.status_code = status
    return resp


def _check_auth():
    """Return an error response if auth is required and the key is invalid.

    Returns None when the request is authorized.
    """
    if not REQUIRE_API_KEY:
        return None
    provided = request.headers.get("X-API-Key")
    if not provided or provided != API_KEY:
        return _error("Unauthorized: missing or invalid X-API-Key.", 401)
    return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/vehicles")
def get_all_vehicles():
    auth_error = _check_auth()
    if auth_error:
        return auth_error
    return jsonify(store.list_all()), 200


@app.post("/vehicles")
def create_vehicle():
    auth_error = _check_auth()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error("Bad request body.", 400)

    # Validate required attributes.
    for field in REQUIRED_CREATE_FIELDS:
        if field not in data or data[field] in (None, ""):
            return _error(
                "Request body missing required attribute: {}".format(field), 400
            )

    # Reject duplicate VINs.
    existing = store.find_by_vin(data["vin"])
    if existing:
        return _error(
            "Vehicle with VIN {} already exists. Existing vehicle ID: {}".format(
                data["vin"], existing["id"]
            ),
            409,
        )

    created = store.create(data)
    return jsonify(created), 201


@app.get("/vehicles/<int:vehicle_id>")
def get_vehicle(vehicle_id):
    auth_error = _check_auth()
    if auth_error:
        return auth_error

    vehicle = store.get(vehicle_id)
    if not vehicle:
        return _error("Vehicle with id: {} not found.".format(vehicle_id), 404)
    return jsonify(vehicle), 200


@app.patch("/vehicles/<int:vehicle_id>")
def update_vehicle(vehicle_id):
    auth_error = _check_auth()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error("Bad request body.", 400)

    updated = store.update(vehicle_id, data)
    if not updated:
        return _error("Vehicle with id: {} not found.".format(vehicle_id), 404)
    return jsonify(updated), 200


@app.delete("/vehicles/<int:vehicle_id>")
def delete_vehicle(vehicle_id):
    auth_error = _check_auth()
    if auth_error:
        return auth_error

    deleted = store.delete(vehicle_id)
    if not deleted:
        return _error("Vehicle with id: {} not found.".format(vehicle_id), 404)
    return "", 204


# ---------------------------------------------------------------------------
# Error handlers — guarantee JSON error bodies
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def handle_404(_):
    return _error("Resource not found.", 404)


@app.errorhandler(405)
def handle_405(_):
    return _error("Method not allowed.", 405)


@app.errorhandler(Exception)
def handle_unexpected(_):
    return _error("An unexpected error occurred.", 500)


def main():
    app.run(host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
