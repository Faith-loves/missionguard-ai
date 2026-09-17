# MissionGuard AI architecture

## Data ingestion and processing

`backend/main.py` mounts four route groups. `nasa_service.py` queries DONKI FLR, CME, and GST data, trying the NASA Open API and two CCMC endpoints with two attempts per provider. Requests use a bounded lookback; credential-bearing request URLs are never returned in provider errors. Unexpected non-list payloads are treated as unavailable.

`noaa_service.py` accepts dictionary rows or a header-plus-rows Kp feed. It converts valid Kp values to finite numbers in the 0–9 range. Missing or unusable readings do not become quiet-weather zeroes.

`space_weather_processor.py` derives flare counts and strongest flare, Earth-directed CME count from ENLIL flags, fastest CME speed across analyses, storm count, and latest Kp. Its quality flag reflects source availability, not scientific certainty or a full observation-freshness audit.

## Deterministic decisions and caching

`risk_engine.py` is the only production scoring implementation. Its fixed contributions are geomagnetic /35, flare /25, CME /30, and storm /10. Readiness is 100 minus risk. Incomplete summaries return null scores and UNKNOWN/HOLD.

`mission_risk.py` fetches the four feeds concurrently, then caches complete assessments by lookback period for 300 seconds. If a later fetch is incomplete, a complete cached result may be served for up to 1,800 seconds with `cache_status=stale-fallback` and current provider-status metadata. The lock and cache are per process; multiple workers do not share them.

## Simulator

`simulator.py` validates hypothetical inputs, builds the same normalized summary shape, and calls the same risk engine. Its response includes the submitted inputs and a simulation notice. Simulation data does not write back into NASA/NOAA feeds or the live cache.

## Explanation boundary

```mermaid
sequenceDiagram
    participant UI as Next.js browser
    participant API as FastAPI
    participant Engine as Deterministic engine
    participant Google as Google signing certificates
    participant AI as IBM Granite
    UI->>API: GET /mission-risk or POST /simulator/evaluate
    API->>Engine: Normalized live or hypothetical summary
    Engine-->>UI: Score, readiness, factors, classification
    UI->>API: POST /ai-explanation/explain + ID token + snapshot
    API->>Google: Fetch/cache public signing certificates
    API->>API: Verify token claims and signature
    API->>AI: Explanation prompt with assessment
    AI-->>API: Candidate prose
    API->>API: Check grounding; deterministic fallback on failure
    API-->>UI: Explanation, provider, model, warning
    Note over Engine,AI: No AI output is consumed by the scoring engine
```

`ai_explainer.py` uses IBM Granite through the watsonx SDK. Missing configuration, model exceptions, or failed grounding return deterministic prose. Checks cover known score/factor phrases, readiness, classifications, dominant contributors, prohibited operational terms, agency references, and simulation language. They are conservative heuristic checks with known limits, not a semantic proof of truth.

The explanation endpoint validates a typed browser-submitted snapshot. It does not retrieve or cryptographically authenticate the original assessment. A valid Firebase token establishes the caller's identity, not the provenance of every supplied value. Saved history likewise remains user-editable data under the user's UID.

## Frontend and persistence

The Next.js App Router serves `/`, `/auth`, and `/history`. `AppAuthGate` listens for Firebase session changes and redirects signed-out visitors to authentication. Public API access remains independent of this UI gate.

The dashboard refreshes every 60 seconds. The chart can fail independently of the assessment. Explanation component identity follows the assessment snapshot so a changed assessment cannot keep an old explanation. The simulator stores the submitted scenario separately from editable controls and prevents overlapping simulation/explanation actions.

Firestore writes go directly from the authenticated browser to `users/{uid}/assessments` and `users/{uid}/simulations`. Both use server timestamps. Simulation records optionally include the currently generated explanation; live records currently do not persist the separately displayed explanation. History reads both collections and sorts in the browser.

## Security boundary and deployment

Firebase ID tokens are checked against Google's RS256 public certificates, the configured project audience/issuer, expiry and required claims. Missing or invalid tokens return 401; missing backend auth configuration returns 503. There is no service-account private key in this flow.

`firestore.rules` allows users to access only their own two record collections and denies other paths by default. These rules are supplied for review and manual publication; their presence does not establish what is deployed in Firebase. Validate same-UID access, cross-UID rejection, and signed-out rejection before release.

Vercel hosts the frontend; Render hosts FastAPI; Firebase hosts Auth/Firestore; watsonx Frankfurt supplies the explanation service. Frontend Firebase web configuration is public. NASA/IBM credentials remain backend-only. CORS permits the current Vercel origin and local port 3000 origins, without wildcard origins or credential cookies.

Public routes have bounded inputs but no application-level rate limits. The AI route is authenticated but has no per-user quota. Certificate retrieval errors currently return 401, and individual token revocation is not checked. Add operational controls before expanding beyond the prototype audience.

## Experiments

Historical datasets and ML scripts remain available for reproducibility. Their models are not imported by runtime routes or the deterministic engine. The forecasting experiment did not meet the quality gate and must not be described as deployed ML forecasting.
