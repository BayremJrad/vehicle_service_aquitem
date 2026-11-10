# Running the Vehicle Service API

A Python (Flask) implementation of the Vehicle Service API contract defined by
the Postman **Vehicle Service Collection** and verified by the **Vehicle Service
QA Testing** collection.

## Prerequisites

- Python 3.9+

## Install

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python -m app.main
```

The service listens on `http://localhost:5000`, which matches the `{{baseUrl}}`
variable used by the Postman collections.

Point your Postman environment's `baseUrl` to `http://localhost:5000` and run
the **Vehicle Service QA Testing** collection against it.

## Configuration (environment variables)

No secrets are hardcoded in the repo. Behaviour is controlled by env vars:

| Variable | Default | Description |
| --- | --- | --- |
| `PORT` | `5000` | Port the server listens on. |
| `API_KEY` | `dev-secret-key` | Expected value of the `X-API-Key` header. Set this in your environment; never commit a real key. |
| `REQUIRE_API_KEY` | `false` | When `true`, every request must send a valid `X-API-Key` header or it is rejected with `401`. Left `false` so local QA runs pass without a key. |

Example with auth enforced:

```bash
API_KEY=my-real-key REQUIRE_API_KEY=true python -m app.main
```

## Endpoints

| Method | Path | Success | Errors |
| --- | --- | --- | --- |
| `GET` | `/vehicles` | `200` (array) | `500` |
| `POST` | `/vehicles` | `201` (object) | `400`, `409`, `500` |
| `GET` | `/vehicles/<id>` | `200` (object) | `404`, `500` |
| `PATCH` | `/vehicles/<id>` | `200` (object) | `400`, `404`, `500` |
| `DELETE` | `/vehicles/<id>` | `204` (no content) | `404`, `500` |

The store is in-memory and seeded with one vehicle (`id=1`) on startup, so
`GET/PATCH/DELETE /vehicles/1` work immediately. Restarting the server resets
the data.
