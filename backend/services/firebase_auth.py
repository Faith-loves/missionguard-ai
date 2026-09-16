import os
import re
import time
from typing import Any

import httpx
import jwt

from cryptography import x509
from dotenv import load_dotenv
from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)


load_dotenv()


FIREBASE_PROJECT_ID = os.getenv(
    "FIREBASE_PROJECT_ID",
    "",
).strip()


FIREBASE_CERTS_URL = (
    "https://www.googleapis.com/"
    "robot/v1/metadata/x509/"
    "securetoken@system.gserviceaccount.com"
)


bearer_scheme = HTTPBearer(
    auto_error=False
)


_cert_cache: dict[str, str] = {}
_cert_cache_expires_at = 0.0


def _get_firebase_certificates() -> dict[str, str]:
    global _cert_cache
    global _cert_cache_expires_at

    now = time.time()

    if (
        _cert_cache
        and now < _cert_cache_expires_at
    ):
        return _cert_cache


    response = httpx.get(
        FIREBASE_CERTS_URL,
        timeout=10.0,
    )

    response.raise_for_status()


    certificates = response.json()

    if not isinstance(
        certificates,
        dict,
    ):
        raise ValueError(
            "Firebase signing certificates are invalid."
        )


    cache_control = response.headers.get(
        "cache-control",
        "",
    )

    match = re.search(
        r"max-age=(\d+)",
        cache_control,
    )


    max_age = (
        int(match.group(1))
        if match
        else 300
    )


    _cert_cache = certificates

    _cert_cache_expires_at = (
        now + max_age
    )


    return certificates


def verify_firebase_id_token(
    token: str,
) -> dict[str, Any]:
    if not FIREBASE_PROJECT_ID:
        raise RuntimeError(
            "FIREBASE_PROJECT_ID is not configured."
        )


    header = jwt.get_unverified_header(
        token
    )


    if header.get("alg") != "RS256":
        raise ValueError(
            "Invalid Firebase token algorithm."
        )


    key_id = header.get(
        "kid"
    )

    if (
        not isinstance(
            key_id,
            str,
        )
        or not key_id
    ):
        raise ValueError(
            "Firebase token has no signing key ID."
        )


    certificates = (
        _get_firebase_certificates()
    )


    certificate_pem = certificates.get(
        key_id
    )


    if not certificate_pem:
        # Signing keys may have rotated.
        global _cert_cache_expires_at

        _cert_cache_expires_at = 0

        certificates = (
            _get_firebase_certificates()
        )

        certificate_pem = (
            certificates.get(
                key_id
            )
        )


    if not certificate_pem:
        raise ValueError(
            "Firebase signing key was not found."
        )


    certificate = (
        x509.load_pem_x509_certificate(
            certificate_pem.encode(
                "utf-8"
            )
        )
    )


    public_key = (
        certificate.public_key()
    )


    issuer = (
        "https://securetoken.google.com/"
        f"{FIREBASE_PROJECT_ID}"
    )


    payload = jwt.decode(
        token,
        public_key,
        algorithms=[
            "RS256"
        ],
        audience=
            FIREBASE_PROJECT_ID,
        issuer=
            issuer,
        options={
            "require": [
                "exp",
                "iat",
                "aud",
                "iss",
                "sub",
                "auth_time",
            ],
        },
    )


    user_id = payload.get(
        "sub"
    )


    if (
        not isinstance(
            user_id,
            str,
        )
        or not user_id
    ):
        raise ValueError(
            "Firebase token has no user ID."
        )


    auth_time = payload.get(
        "auth_time"
    )


    if not isinstance(
        auth_time,
        (int, float),
    ):
        raise ValueError(
            "Firebase token has invalid authentication time."
        )


    if auth_time > time.time() + 5:
        raise ValueError(
            "Firebase authentication time is invalid."
        )


    return payload


def require_firebase_user(
    credentials:
        HTTPAuthorizationCredentials
        | None = Depends(
            bearer_scheme
        ),
) -> dict[str, Any]:

    if credentials is None:
        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,
            detail=
                "Authentication required.",
            headers={
                "WWW-Authenticate":
                    "Bearer",
            },
        )


    if (
        credentials.scheme.lower()
        != "bearer"
    ):
        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,
            detail=
                "Invalid authentication scheme.",
            headers={
                "WWW-Authenticate":
                    "Bearer",
            },
        )


    try:
        return verify_firebase_id_token(
            credentials.credentials
        )

    except (
        jwt.PyJWTError,
        httpx.HTTPError,
        ValueError,
    ):
        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,
            detail=
                "Invalid or expired authentication token.",
            headers={
                "WWW-Authenticate":
                    "Bearer",
            },
        )

    except RuntimeError:
        raise HTTPException(
            status_code=
                status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=
                "Authentication service is not configured.",
        )
