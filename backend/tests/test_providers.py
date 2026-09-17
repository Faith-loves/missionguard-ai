import asyncio

import httpx
import pytest

from services import nasa_service, noaa_service


@pytest.mark.parametrize("payload", [
    [["time_tag", "Kp"], ["2026-09-16 00:00:00", "4.33"]],
    [{"time_tag": "2026-09-16 00:00:00", "Kp": "4.33"}],
])
def test_noaa_normalizes_numeric_strings(monkeypatch, payload):
    class Client:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, url, **kwargs):
            return httpx.Response(200, json=payload, request=httpx.Request("GET", url))

    monkeypatch.setattr(noaa_service.httpx, "AsyncClient", Client)
    result = asyncio.run(noaa_service.get_kp_index())
    assert result["available"]
    assert result["latest"]["Kp"] == 4.33


@pytest.mark.parametrize("value", [None, "bad", "nan", "inf", -1, 10])
def test_invalid_noaa_readings_are_unavailable(monkeypatch, value):
    class Client:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, url, **kwargs):
            return httpx.Response(200, json=[{"time_tag": "today", "Kp": value}],
                                  request=httpx.Request("GET", url))

    monkeypatch.setattr(noaa_service.httpx, "AsyncClient", Client)
    result = asyncio.run(noaa_service.get_kp_index())
    assert not result["available"]
    assert result["latest"] is None


def test_nasa_failures_never_expose_key_or_url(monkeypatch):
    async def fail(url, params):
        request = httpx.Request("GET", url, params={"api_key": "private-test-secret"})
        response = httpx.Response(403, request=request)
        response.raise_for_status()

    async def no_sleep(seconds): pass
    monkeypatch.setattr(nasa_service, "request_endpoint", fail)
    monkeypatch.setattr(nasa_service.asyncio, "sleep", no_sleep)
    result = asyncio.run(nasa_service.get_solar_flares())
    assert not result["available"]
    assert "private-test-secret" not in str(result)
    assert "api_key" not in str(result)
    assert "HTTPStatusError" in result["error"]


def test_nasa_error_object_is_not_a_quiet_sun(monkeypatch):
    async def malformed(url, params): return {"error": "unavailable"}
    async def no_sleep(seconds): pass
    monkeypatch.setattr(nasa_service, "request_endpoint", malformed)
    monkeypatch.setattr(nasa_service.asyncio, "sleep", no_sleep)
    assert not asyncio.run(nasa_service.get_cmes())["available"]
