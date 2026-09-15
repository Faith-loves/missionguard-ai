from services.risk_engine import calculate_mission_risk


def make_summary(
    kp=2.0,
    flare=None,
    earth_cmes=0,
    cme_speed=0,
    storms=0,
    quality="complete",
):
    return {
        "solar_activity": {
            "strongest_flare": flare,
        },
        "cme_activity": {
            "earth_directed_cmes": earth_cmes,
            "fastest_speed_km_s": cme_speed,
        },
        "geomagnetic_activity": {
            "latest_kp": kp,
            "storm_count": storms,
        },
        "data_quality": quality,
    }


def test_low_risk():
    summary = make_summary(
        kp=2.0,
        flare="C1.0",
        earth_cmes=0,
        cme_speed=300,
        storms=0,
    )

    result = calculate_mission_risk(summary)

    assert result["risk_level"] == "LOW"
    assert result["recommendation"] == "GO"
    assert result["risk_score"] <= 24


def test_moderate_risk():
    summary = make_summary(
        kp=2.33,
        flare="C3.4",
        earth_cmes=4,
        cme_speed=1586,
        storms=0,
    )

    result = calculate_mission_risk(summary)

    assert result["risk_level"] == "MODERATE"
    assert result["recommendation"] == "CAUTION"
    assert 25 <= result["risk_score"] <= 49


def test_high_risk():
    summary = make_summary(
        kp=6.0,
        flare="M7.0",
        earth_cmes=2,
        cme_speed=1200,
        storms=1,
    )

    result = calculate_mission_risk(summary)

    assert result["risk_level"] == "HIGH"
    assert result["recommendation"] == "DELAY"
    assert 50 <= result["risk_score"] <= 74


def test_critical_risk():
    summary = make_summary(
        kp=9.0,
        flare="X12.0",
        earth_cmes=5,
        cme_speed=2200,
        storms=4,
    )

    result = calculate_mission_risk(summary)

    assert result["risk_level"] == "CRITICAL"
    assert result["recommendation"] == "NO-GO"
    assert result["risk_score"] >= 75


def test_incomplete_data():
    summary = make_summary(
        quality="limited",
    )

    result = calculate_mission_risk(summary)

    assert result["risk_score"] is None
    assert result["mission_readiness"] is None
    assert result["risk_level"] == "UNKNOWN"
    assert result["recommendation"] == "HOLD"

