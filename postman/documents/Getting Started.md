# Getting Started with the Vehicle Service API

Welcome to the **Vehicle Service API**. This guide will walk you through everything you need to know to set up your environment and start sending successful requests using the Vehicle Service Collection in Postman.

---

## Prerequisites

Before you begin, make sure you have:

- Access to the **Vehicle Service** workspace in Postman
- The **Vehicle Service Collection** available in your workspace
- Your API key (provided by your team administrator)

---

## Step 1: Select the Environment

All requests in this collection rely on the `{{baseUrl}}` variable to construct endpoint URLs. This variable is defined in the **Mock Environment**.

1. In the top-right corner of Postman, open the **Environment** dropdown.
2. Select **Mock Environment**.

This sets `baseUrl` to:
```
https://29b47815-52f9-493f-abaa-303df6087d3c.mock.pstmn.io
```

> Without an active environment selected, requests will fail because `{{baseUrl}}` will not resolve.

---

## Step 2: Set Up Your API Key

The Vehicle Service API authenticates requests using an **API Key** stored in the Postman **Vault**.

1. Open the Postman **Vault** (click the lock icon in the bottom-right of the Postman app, or go to **Settings > Vault**).
2. Add a new vault secret with the key name: `apiKey`
3. Set the value to the API key provided by your administrator.

> Vault variables are encrypted locally and are never synced to the cloud, keeping your credentials safe.

Once saved, the `vault:apiKey` variable will be available to all requests in this collection automatically.

---

## Step 3: Send Your First Request

The easiest way to verify your setup is to fetch all vehicles.

1. Open the **Vehicle Service Collection** in the sidebar.
2. Click on **Get all vehicles** (`GET /vehicles`).
3. Click **Send**.

A successful response will return a `200 OK` status with a JSON array of vehicle objects:

```json
[
  {
    "id": "abc123",
    "nickName": "The Lisa Marie",
    "vin": "4M2DV11W4RDJ53329",
    "make": "Mercury",
    "model": "Villager",
    "year": "1994",
    "miles": 159864
  }
]
```

---

## Step 4: Create a Vehicle

To add a new vehicle to the system:

1. Open **Create a vehicle** (`POST /vehicles`) from the collection.
2. The request body is pre-populated with an example payload. Modify the fields as needed:

```json
{
  "nickName": "My Car",
  "vin": "1HGBH41JXMN109186",
  "make": "Honda",
  "model": "Civic",
  "year": "2021",
  "miles": 12000
}
```

3. Click **Send**.

A `201 Created` response confirms the vehicle was added successfully.

> **Note:** The `vin` must be unique. If a vehicle with the same VIN already exists, you will receive a `409 - Vehicle already exists` error.

---

## Step 5: Work with a Specific Vehicle

Once you have a vehicle ID (returned in the response body of a create or list request), you can:

| Action | Request | Path |
|--------|---------|------|
| View details | **Retrieve a vehicle** | `GET /vehicles/:id` |
| Update fields | **Update a vehicle** | `PATCH /vehicles/:id` |
| Remove it | **Delete a vehicle** | `DELETE /vehicles/:id` |

Replace the `:id` path variable in Postman with the actual vehicle ID before sending.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `{{baseUrl}}` appears unresolved in the URL | No environment selected | Select **Mock Environment** from the dropdown |
| `401 Unauthorized` | API key missing or incorrect | Check your `apiKey` value in the Postman Vault |
| `404 Not Found` | Invalid vehicle ID in the path | Verify the `:id` path variable is set correctly |
| `409 Conflict` | Duplicate VIN | Use a unique VIN for the new vehicle |
| `400 Bad Request` | Missing required fields | Ensure `vin`, `make`, `model`, `year`, and `miles` are all present |
| `500 Server Error` | Unexpected server issue | Retry the request; contact your API administrator if it persists |

---

## Available Endpoints at a Glance

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/vehicles` | Create a new vehicle |
| `GET` | `/vehicles` | List all vehicles |
| `GET` | `/vehicles/:id` | Get a vehicle by ID |
| `PATCH` | `/vehicles/:id` | Update a vehicle |
| `DELETE` | `/vehicles/:id` | Delete a vehicle |

---

*For full schema details and response examples, refer to the individual request descriptions within the Vehicle Service Collection.*