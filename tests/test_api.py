"""API smoke tests: verify every endpoint returns valid JSON."""
from fastapi.testclient import TestClient
from backend.main import app

c = TestClient(app)


def test_health():
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_attacks_list():
    r = c.get("/attacks")
    assert r.status_code == 200
    attacks = r.json()
    assert "legitimate" in attacks
    assert "blind_forgery" in attacks


def test_simulate_legitimate():
    r = c.post("/simulate/legitimate")
    assert r.status_code == 200
    data = r.json()
    assert data["verdict"] == "ACCEPT"
    assert data["attack_type"] == "NONE"


def test_simulate_replay():
    r = c.post("/simulate/replay")
    assert r.status_code == 200
    assert r.json()["attack_type"] == "REPLAY_ATTACK"


def test_simulate_invalid():
    assert c.post("/simulate/nope").status_code == 404


def test_history():
    # Ensure at least one event exists
    c.post("/simulate/legitimate")
    r = c.get("/history")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_thresholds():
    r = c.get("/thresholds")
    assert r.status_code == 200
    data = r.json()
    assert data["accept_max"] < data["reject_min"]
    assert "derivation" in data


def test_audit_verify():
    r = c.get("/audit/verify")
    assert r.status_code == 200
    assert r.json()["valid"] is True


def test_shor_toy():
    r = c.get("/shor-toy")
    assert r.status_code == 200
    data = r.json()
    assert data["factors_found"] == [3, 5]
    assert data["N"] == 15


def test_reality_check():
    r = c.get("/reality-check")
    assert r.status_code == 200
    data = r.json()
    assert "real" in data and "simulated" in data and "not_claimed" in data
    assert len(data["real"]) >= 3
    assert len(data["not_claimed"]) >= 3


def test_config():
    r = c.get("/config")
    assert r.status_code == 200
    data = r.json()
    assert data["BLOCK_SIZE"] == 128
    assert data["DIGEST_BITS"] == 8


def test_all_attacks_via_api():
    """Smoke test: every attack type via the API returns a result with expected fields."""
    attacks = c.get("/attacks").json()
    for attack in attacks:
        r = c.post(f"/simulate/{attack}", params={"strength": 0.5})
        assert r.status_code == 200, f"{attack} returned {r.status_code}"
        data = r.json()
        assert "verdict" in data
        assert "attack_type" in data
        assert "threat_score" in data
        assert "forgery_probability" in data
