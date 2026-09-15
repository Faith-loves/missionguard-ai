def summarize_space_weather(
    flares,
    cmes,
    storms,
    kp_result,
    flare_available,
    cme_available,
    storm_available,
):
    # -------------------------
    # Solar flare processing
    # -------------------------
    total_flares = None
    x_class_count = None
    m_class_count = None
    c_class_count = None
    strongest_flare = None

    if flare_available:
        total_flares = len(flares)

        x_class_count = 0
        m_class_count = 0
        c_class_count = 0

        strongest_flare_value = -1

        for flare in flares:
            flare_class = flare.get("classType")

            if not flare_class:
                continue

            letter = flare_class[0].upper()

            try:
                number = float(flare_class[1:])
            except (ValueError, TypeError):
                number = 0

            if letter == "X":
                x_class_count += 1
                strength = 300 + number

            elif letter == "M":
                m_class_count += 1
                strength = 200 + number

            elif letter == "C":
                c_class_count += 1
                strength = 100 + number

            else:
                strength = number

            if strength > strongest_flare_value:
                strongest_flare_value = strength
                strongest_flare = flare_class

    # -------------------------
    # CME processing
    # -------------------------
    total_cmes = None
    earth_directed_cmes = None
    fastest_cme_speed = None

    if cme_available:
        total_cmes = len(cmes)
        earth_directed_cmes = 0
        fastest_cme_speed = 0

        for cme in cmes:
            analyses = cme.get("cmeAnalyses") or []

            earth_directed = False

            for analysis in analyses:
                speed = analysis.get("speed")

                if speed is not None:
                    try:
                        speed_value = float(speed)

                        if speed_value > fastest_cme_speed:
                            fastest_cme_speed = speed_value

                    except (ValueError, TypeError):
                        pass

                enlil_list = analysis.get("enlilList") or []

                for enlil in enlil_list:
                    if (
                        enlil.get("isEarthGB") is True
                        or enlil.get("isEarthMinorImpact") is True
                    ):
                        earth_directed = True

            if earth_directed:
                earth_directed_cmes += 1

    # -------------------------
    # Storm processing
    # -------------------------
    storm_count = None

    if storm_available:
        storm_count = len(storms)

    # -------------------------
    # NOAA Kp processing
    # -------------------------
    latest_kp = None
    kp_time = None

    kp_available = kp_result.get(
        "available",
        False,
    )

    if kp_available:
        latest = kp_result.get("latest")

        if latest:
            latest_kp = latest.get("Kp")
            kp_time = latest.get("time_tag")

    # -------------------------
    # Data quality
    # -------------------------
    source_status = [
        bool(flare_available),
        bool(cme_available),
        bool(storm_available),
        bool(kp_available),
    ]

    available_count = sum(source_status)

    if available_count == 4:
        data_quality = "complete"

    elif available_count >= 2:
        data_quality = "partial"

    else:
        data_quality = "limited"

    return {
        "solar_activity": {
            "available": flare_available,
            "total_flares": total_flares,
            "x_class_flares": x_class_count,
            "m_class_flares": m_class_count,
            "c_class_flares": c_class_count,
            "strongest_flare": strongest_flare,
        },

        "cme_activity": {
            "available": cme_available,
            "total_cmes": total_cmes,
            "earth_directed_cmes": earth_directed_cmes,
            "fastest_speed_km_s": fastest_cme_speed,
        },

        "geomagnetic_activity": {
            "storm_data_available": storm_available,
            "storm_count": storm_count,
            "kp_available": kp_available,
            "latest_kp": latest_kp,
            "kp_time": kp_time,
        },

        "data_quality": data_quality,

        "sources": {
            "solar_flares": flare_available,
            "cmes": cme_available,
            "geomagnetic_storms": storm_available,
            "kp_index": kp_available,
        },
    }