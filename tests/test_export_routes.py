import json
import csv
import io
import pytest
from hookdraft.app import create_app
from hookdraft.storage import RequestStore


@pytest.fixture()
def client(tmp_path):
    store = RequestStore(storage_dir=str(tmp_path))
    app = create_app(store=store)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hooks(client, n=2):
    for i in range(n):
        client.post(
            "/hooks/test",
            json={"index": i, "msg": f"hello {i}"},
            headers={"X-Custom": "value"},
        )


def test_export_json_empty(client):
    resp = client.get("/requests/export/json")
    assert resp.status_code == 200
    assert resp.mimetype == "application/json"
    data = json.loads(resp.data)
    assert data == []


def test_export_json_with_records(client):
    _post_hooks(client, n=3)
    resp = client.get("/requests/export/json")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert len(data) == 3
    first = data[0]
    assert "id" in first
    assert "timestamp" in first
    assert "method" in first
    assert first["method"] == "POST"


def test_export_json_content_disposition(client):
    resp = client.get("/requests/export/json")
    cd = resp.headers.get("Content-Disposition", "")
    assert "requests.json" in cd


def test_export_csv_empty(client):
    resp = client.get("/requests/export/csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.mimetype
    reader = csv.DictReader(io.StringIO(resp.data.decode()))
    rows = list(reader)
    assert rows == []


def test_export_csv_with_records(client):
    _post_hooks(client, n=2)
    resp = client.get("/requests/export/csv")
    assert resp.status_code == 200
    reader = csv.DictReader(io.StringIO(resp.data.decode()))
    rows = list(reader)
    assert len(rows) == 2
    assert set(rows[0].keys()) >= {"id", "timestamp", "method", "path", "headers", "body"}


def test_export_csv_body_is_json_encoded(client):
    _post_hooks(client, n=1)
    resp = client.get("/requests/export/csv")
    reader = csv.DictReader(io.StringIO(resp.data.decode()))
    row = next(reader)
    body = json.loads(row["body"])
    assert "index" in body


def test_export_csv_content_disposition(client):
    resp = client.get("/requests/export/csv")
    cd = resp.headers.get("Content-Disposition", "")
    assert "requests.csv" in cd
