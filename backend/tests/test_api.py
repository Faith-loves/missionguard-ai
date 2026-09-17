import pytest
from fastapi.testclient import TestClient

from main import app
from routes import mission_risk, space_weather
from services import ai_explainer
from services.firebase_auth import require_firebase_user


@pytest.fixture
def client(monkeypatch):
    async def nasa(days=7):
        return {"available": True, "data": [], "error": None, "provider": "test"}
    async def noaa():
        return {"available": True, "latest": {"Kp": 2.0, "time_tag": "test"},
                "history": [{"Kp": 2.0, "time_tag": "test"}], "error": None}
    for module in (mission_risk, space_weather):
        for name in ("get_solar_flares", "get_cmes", "get_geomagnetic_storms"):
            monkeypatch.setattr(module, name, nasa)
        monkeypatch.setattr(module, "get_kp_index", noaa)
    mission_risk._cache.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    mission_risk._cache.clear()


@pytest.mark.parametrize("path", ["/", "/health", "/space-weather/current",
    "/space-weather/summary", "/space-weather/kp-index", "/space-weather/solar-flares",
    "/space-weather/cmes", "/space-weather/geomagnetic-storms", "/mission-risk"])
def test_public_routes(client, path):
    assert client.get(path).status_code == 200


@pytest.mark.parametrize("header", [None, "Bearer invalid", "Basic invalid"])
def test_ai_requires_authentication(client, header):
    response = client.post("/ai-explanation/explain", json={},
                           headers={"Authorization": header} if header else {})
    assert response.status_code == 401


def test_authenticated_ai_uses_fallback_without_paid_call(client, monkeypatch):
    app.dependency_overrides[require_firebase_user] = lambda: {"sub": "test-user"}
    monkeypatch.setattr(ai_explainer, "watsonx_configured", lambda: False)
    simulation = client.post("/simulator/evaluate", json={}).json()
    response = client.post("/ai-explanation/explain", json={
        "mode": "simulation", "mission": simulation["mission"],
        "risk_factors": simulation["risk_factors"],
        "space_weather": simulation["simulated_space_weather"],
    })
    assert response.status_code == 200
    assert response.json()["provider"] == "fallback"
    assert response.json()["authenticated_user"] == "test-user"


def test_simulator_known_scenario(client):
    response = client.post("/simulator/evaluate", json={
        "kp_index": 4, "flare_class": "X", "flare_magnitude": 1,
        "earth_directed_cmes": 3, "fastest_cme_speed_km_s": 1500, "storm_count": 2,
    })
    assert response.status_code == 200
    assert response.json()["mission"] == {
        "risk_score": 62, "mission_readiness": 38, "risk_level": "HIGH", "recommendation": "DELAY"}
    assert client.post("/simulator/evaluate", json={"kp_index": 10}).status_code == 422


@pytest.mark.parametrize("path", ["/mission-risk", "/space-weather/current",
    "/space-weather/summary", "/space-weather/solar-flares", "/space-weather/cmes",
    "/space-weather/geomagnetic-storms"])
def test_invalid_lookback_rejected(client, path):
    assert client.get(path, params={"days": -1}).status_code == 422
    assert client.get(path, params={"days": 999999999}).status_code == 422


def test_cors(client):
    for origin in ["https://missionguard-ai-one.vercel.app", "http://localhost:3000",
                   "http://127.0.0.1:3000"]:
        response = client.options("/ai-explanation/explain", headers={
            "Origin": origin, "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type"})
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin
    response = client.options("/ai-explanation/explain", headers={
        "Origin": "https://untrusted.example", "Access-Control-Request-Method": "POST"})
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
