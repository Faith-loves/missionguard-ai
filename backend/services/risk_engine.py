def calculate_mission_risk(summary: dict):
    data_quality = summary.get(
        "data_quality",
        "limited",
    )

    # Never pretend incomplete data is safe.
    if data_quality != "complete":
        return {
            "risk_score": None,
            "risk_level": "UNKNOWN",
            "recommendation": "HOLD",
            "mission_readiness": None,
            "data_quality": data_quality,
            "reason": (
                "Mission risk cannot be calculated "
                "reliably because space-weather "
                "data is incomplete."
            ),
            "factors": {},
        }

    solar = summary.get(
        "solar_activity",
        {},
    )

    cme = summary.get(
        "cme_activity",
        {},
    )

    geomagnetic = summary.get(
        "geomagnetic_activity",
        {},
    )

    total_score = 0

    factors = {
        "geomagnetic": 0,
        "solar_flare": 0,
        "cme": 0,
        "storm": 0,
    }

    # =====================================
    # 1. GEOMAGNETIC / KP RISK
    # Maximum: 35 points
    # =====================================

    kp = geomagnetic.get(
        "latest_kp"
    )

    if kp is not None:
        kp = float(kp)

        if kp < 3:
            kp_score = 2

        elif kp < 4:
            kp_score = 5

        elif kp < 5:
            kp_score = 10

        elif kp < 6:
            kp_score = 18

        elif kp < 7:
            kp_score = 23

        elif kp < 8:
            kp_score = 28

        elif kp < 9:
            kp_score = 32

        else:
            kp_score = 35

        factors["geomagnetic"] = kp_score
        total_score += kp_score

    # =====================================
    # 2. SOLAR FLARE RISK
    # Maximum: 25 points
    # =====================================

    strongest_flare = solar.get(
        "strongest_flare"
    )

    flare_score = 0

    if strongest_flare:
        flare_letter = (
            strongest_flare[0]
            .upper()
        )

        try:
            flare_number = float(
                strongest_flare[1:]
            )
        except (
            ValueError,
            TypeError,
        ):
            flare_number = 0

        if flare_letter == "C":
            flare_score = min(
                5,
                1 + int(
                    flare_number / 3
                ),
            )

        elif flare_letter == "M":
            if flare_number < 5:
                flare_score = 8
            else:
                flare_score = 13

        elif flare_letter == "X":
            if flare_number < 5:
                flare_score = 18

            elif flare_number < 10:
                flare_score = 22

            else:
                flare_score = 25

    factors["solar_flare"] = (
        flare_score
    )

    total_score += flare_score

    # =====================================
    # 3. CME RISK
    # Maximum: 30 points
    # =====================================

    earth_directed = (
        cme.get(
            "earth_directed_cmes"
        )
        or 0
    )

    fastest_speed = (
        cme.get(
            "fastest_speed_km_s"
        )
        or 0
    )

    cme_score = 0

    # Earth-directed CME activity
    if earth_directed == 1:
        cme_score += 5

    elif earth_directed == 2:
        cme_score += 8

    elif earth_directed >= 3:
        cme_score += 12

    # CME velocity contribution
    if fastest_speed >= 2000:
        cme_score += 18

    elif fastest_speed >= 1500:
        cme_score += 15

    elif fastest_speed >= 1000:
        cme_score += 10

    elif fastest_speed >= 750:
        cme_score += 6

    elif fastest_speed >= 500:
        cme_score += 3

    cme_score = min(
        cme_score,
        30,
    )

    factors["cme"] = cme_score

    total_score += cme_score

    # =====================================
    # 4. GEOMAGNETIC STORM HISTORY
    # Maximum: 10 points
    # =====================================

    storm_count = (
        geomagnetic.get(
            "storm_count"
        )
        or 0
    )

    if storm_count == 1:
        storm_score = 4

    elif storm_count == 2:
        storm_score = 7

    elif storm_count >= 3:
        storm_score = 10

    else:
        storm_score = 0

    factors["storm"] = (
        storm_score
    )

    total_score += storm_score

    # Ensure range 0 - 100
    risk_score = min(
        round(total_score),
        100,
    )

    mission_readiness = max(
        0,
        100 - risk_score,
    )

    # =====================================
    # RISK CLASSIFICATION
    # =====================================

    if risk_score <= 24:
        risk_level = "LOW"
        recommendation = "GO"

    elif risk_score <= 49:
        risk_level = "MODERATE"
        recommendation = "CAUTION"

    elif risk_score <= 74:
        risk_level = "HIGH"
        recommendation = "DELAY"

    else:
        risk_level = "CRITICAL"
        recommendation = "NO-GO"

    return {
        "risk_score": risk_score,
        "mission_readiness": (
            mission_readiness
        ),
        "risk_level": risk_level,
        "recommendation": (
            recommendation
        ),
        "data_quality": (
            data_quality
        ),
        "factors": factors,
    }