VALID_PAYLOAD = {
    "sensor_id": "sensor-cairo-01",
    "timestamp": "2024-01-15T10:30:00Z",
    "reading": 23.5,
}


def post_reading(client, payload: dict = None):
    return client.post("/api/v1/readings", json=payload or VALID_PAYLOAD)


# POST /readings: happy path

def test_create_reading_returns_201(client):
    response = post_reading(client)
    assert response.status_code == 201


def test_create_reading_returns_correct_fields(client):
    response = post_reading(client)
    data = response.json()
    assert data["sensor_id"] == "sensor-cairo-01"
    assert data["reading"] == 23.5
    assert "id" in data
    assert "received_at" in data


def test_create_reading_persists_to_database(client):
    post_reading(client)
    response = client.get("/api/v1/readings/sensor-cairo-01")
    assert response.status_code == 200
    assert len(response.json()) == 1


# POST /readings: duplicates

def test_create_duplicate_reading_returns_409(client):
    post_reading(client)
    response = post_reading(client)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_create_duplicate_does_not_store_second_entry(client):
    post_reading(client)
    post_reading(client)
    response = client.get("/api/v1/readings/sensor-cairo-01")
    assert len(response.json()) == 1


# POST /readings: validation errors

def test_create_reading_missing_sensor_id_returns_422(client):
    response = post_reading(client, {"timestamp": "2024-01-15T10:30:00Z", "reading": 23.5})
    assert response.status_code == 422


def test_create_reading_blank_sensor_id_returns_422(client):
    response = post_reading(client, {**VALID_PAYLOAD, "sensor_id": "   "})
    assert response.status_code == 422


def test_create_reading_future_timestamp_returns_422(client):
    response = post_reading(client, {**VALID_PAYLOAD, "timestamp": "2099-01-01T00:00:00Z"})
    assert response.status_code == 422

def test_create_reading_missing_timezone_returns_422(client):
    response = post_reading(client, {**VALID_PAYLOAD, "timestamp": "2024-01-15T10:30:00"})
    assert response.status_code == 422


def test_create_reading_missing_reading_field_returns_422(client):
    response = post_reading(client, {"sensor_id": "sensor-01", "timestamp": "2024-01-15T10:30:00Z"})
    assert response.status_code == 422


def test_create_reading_invalid_reading_type_returns_422(client):
    response = post_reading(client, {**VALID_PAYLOAD, "reading": "not-a-number"})
    assert response.status_code == 422


def test_create_reading_validation_error_format(client):
    """Verify the custom flattened error format is used."""
    response = post_reading(client, {**VALID_PAYLOAD, "timestamp": "2099-01-01T00:00:00Z"})
    body = response.json()
    assert body["detail"] == "Request validation failed."
    assert "errors" in body
    assert "field" in body["errors"][0]
    assert "message" in body["errors"][0]


# GET /readings/{sensor_id}

def test_list_readings_returns_200(client):
    post_reading(client)
    response = client.get("/api/v1/readings/sensor-cairo-01")
    assert response.status_code == 200


def test_list_readings_returns_empty_for_unknown_sensor(client):
    response = client.get("/api/v1/readings/sensor-unknown")
    assert response.status_code == 404
    assert response.json()["detail"] == "No readings found for sensor 'sensor-unknown'"

def test_list_readings_respects_limit(client):
    for h in range(5):
        post_reading(client, {**VALID_PAYLOAD, "timestamp": f"2024-01-15T{h:02d}:00:00Z"})

    response = client.get("/api/v1/readings/sensor-cairo-01?limit=2")
    assert len(response.json()) == 2


def test_list_readings_invalid_limit_returns_422(client):
    response = client.get("/api/v1/readings/sensor-cairo-01?limit=0")
    assert response.status_code == 422


def test_list_readings_limit_over_max_returns_422(client):
    response = client.get("/api/v1/readings/sensor-cairo-01?limit=9999")
    assert response.status_code == 422
    
# Health check
def test_health_check_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"