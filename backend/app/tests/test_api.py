import pytest
from fastapi.testclient import TestClient

P = "/api/v1"
BODY = dict(full_name="Alex Smith", date_of_birth="1990-01-01", email="alex.smith1@mail.test", phone="+1-555-1234567",
            address="1 Oak St", device_id="dev-test-1", ip_address="1.2.3.4", employment_status="employed",
            annual_income=70000, requested_credit=10000, application_channel="web")


@pytest.fixture(scope="module")
def client(seeded_app):
    with TestClient(seeded_app) as c:
        yield c


def test_health(client):
    assert client.get(f"{P}/health").json() == {"status": "ok"}
    assert client.get(f"{P}/health/ready").json() == {"status": "ready"}


def test_list_filters_and_pagination(client):
    r = client.get(f"{P}/applications", params={"page_size": 5, "sort": "score"}).json()
    assert len(r["items"]) == 5 and r["total"] > 5
    scores = [i["score"]["score"] for i in r["items"]]
    assert scores == sorted(scores, reverse=True)
    hi = client.get(f"{P}/applications", params={"tier": "High", "page_size": 100}).json()
    assert all(i["score"]["tier"] == "High" for i in hi["items"])
    p2 = client.get(f"{P}/applications", params={"page": 2, "page_size": 5, "sort": "score"}).json()
    assert p2["items"][0]["application_id"] != r["items"][0]["application_id"]
    assert client.get(f"{P}/applications", params={"page_size": 1000}).status_code == 422
    assert client.get(f"{P}/applications", params={"tier": "Bogus"}).status_code == 422


def test_detail_explanation_404(client):
    aid = client.get(f"{P}/applications", params={"page_size": 1}).json()["items"][0]["application_id"]
    d = client.get(f"{P}/applications/{aid}").json()
    assert d["linked_entities"] and d["timeline"]
    e = client.get(f"{P}/applications/{aid}/explanation").json()
    assert e["top_factors"] and "not proof" in e["note"]
    assert client.get(f"{P}/applications/NOPE").status_code == 404
    assert client.get(f"{P}/applications/NOPE/explanation").status_code == 404


def test_score_single_and_validation(client):
    r = client.post(f"{P}/score", json=BODY)
    assert r.status_code == 200
    j = r.json()
    assert j["is_simulated"] and 0 <= j["display_score"] <= 100 and j["tier"] in ("Low", "Medium", "High")
    assert j["top_factors"] and j["model_version"]
    # persisted + retrievable
    assert client.get(f"{P}/applications/{j['application_id']}").status_code == 200
    # labels are rejected, bad input is rejected
    assert client.post(f"{P}/score", json={**BODY, "fraud_label": 1}).status_code == 422
    assert client.post(f"{P}/score", json={**BODY, "annual_income": -5}).status_code == 422
    assert client.post(f"{P}/score", json={**BODY, "ip_address": "nope"}).status_code == 422


def test_score_batch(client):
    apps = [{**BODY, "device_id": f"dev-batch-{i}", "email": f"b{i}@mail.test"} for i in range(3)]
    r = client.post(f"{P}/score/batch", json={"applications": apps})
    assert r.status_code == 200 and len(r.json()) == 3
    assert client.post(f"{P}/score/batch", json={"applications": []}).status_code == 422


def test_shared_device_raises_linked_count(client):
    ids = [client.post(f"{P}/score", json={**BODY, "device_id": "dev-ring-x", "email": f"r{i}@mail.test"}).json() for i in range(3)]
    dev = [e for e in ids[-1]["linked_entities"] if e["kind"] == "device"][0]
    assert dev["shared_with_other_applications"] == 2


def test_entities_network(client):
    hub = client.get(f"{P}/entities").json()["items"][0]
    n = client.get(f"{P}/entities/{hub['entity_id']}/network").json()
    assert n["nodes"] and n["edges"] and "not proof" in n["note"]
    assert client.get(f"{P}/entities/device:does-not-exist/network").status_code == 404
    assert client.get(f"{P}/entities", params={"q": "device:"}).json()["items"]


def test_notes_models_metrics_features(client):
    aid = client.get(f"{P}/applications", params={"page_size": 1}).json()["items"][0]["application_id"]
    assert client.post(f"{P}/applications/{aid}/notes", json={"note": "checked"}).json()["notes"][0]["note"] == "checked"
    assert client.post(f"{P}/applications/{aid}/notes", json={"note": ""}).status_code == 422
    assert client.get(f"{P}/models").json()["items"]
    assert "models" in client.get(f"{P}/metrics/model").json()
    assert "feature_drift" in client.get(f"{P}/metrics/monitoring").json()
    assert client.get(f"{P}/features").json()["groups"]
    assert client.get(f"{P}/overview").json()["total"] > 0
