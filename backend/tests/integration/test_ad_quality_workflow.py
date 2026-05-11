from datetime import datetime, timedelta

from fastapi.testclient import TestClient


def create_deliverable_campaign(client: TestClient) -> tuple[dict, dict]:
    campaign = client.post(
        "/campaigns",
        json={
            "advertiser_name": "Nike",
            "daily_budget": 500,
            "bid_cpc": 1.2,
            "target_country": "US",
            "target_age_min": 18,
            "target_age_max": 35,
        },
    ).json()
    ad = client.post(
        f"/campaigns/{campaign['id']}/ads",
        json={
            "campaign_id": campaign["id"],
            "title": "Running Shoes",
            "landing_url": "https://example.com/shoes",
        },
    ).json()
    return campaign, ad


def test_full_delivery_click_conversion_metrics_workflow(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "US", "age": 24, "device": "ios", "interests": "fitness"},
    ).json()
    campaign, _ = create_deliverable_campaign(client)

    delivery = client.post("/ads/request", json={"user_id": user["id"]}).json()
    click = client.post("/events/click", json={"impression_id": delivery["impression_id"]}).json()
    conversion_response = client.post(
        "/events/conversion",
        json={"click_id": click["id"], "conversion_value": 79.99},
    )
    metrics = client.get(f"/metrics/campaigns/{campaign['id']}").json()

    assert conversion_response.status_code == 201
    assert metrics["impressions"] == 1
    assert metrics["clicks"] == 1
    assert metrics["conversions"] == 1
    assert metrics["ctr"] == 1
    assert metrics["cvr"] == 1
    assert metrics["spend"] == 1.2


def test_health_and_readiness_checks(client: TestClient) -> None:
    health = client.get("/health")
    ready = client.get("/ready")

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready"}


def test_conversion_outside_attribution_window_is_rejected(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "US", "age": 24, "device": "ios", "interests": "fitness"},
    ).json()
    create_deliverable_campaign(client)
    delivery = client.post("/ads/request", json={"user_id": user["id"]}).json()
    click = client.post("/events/click", json={"impression_id": delivery["impression_id"]}).json()

    response = client.post(
        "/events/conversion",
        json={
            "click_id": click["id"],
            "conversion_value": 99,
            "created_at": (datetime.utcnow() + timedelta(days=8)).isoformat(),
        },
    )

    assert response.status_code == 400
    assert "attribution window" in response.json()["detail"]


def test_quality_check_creates_high_ctr_alert(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "US", "age": 24, "device": "ios", "interests": "fitness"},
    ).json()
    campaign, _ = create_deliverable_campaign(client)
    delivery = client.post("/ads/request", json={"user_id": user["id"]}).json()
    client.post("/events/click", json={"impression_id": delivery["impression_id"]})

    response = client.post(f"/quality/campaigns/{campaign['id']}/run")

    assert response.status_code == 200
    alerts = response.json()
    assert alerts[0]["alert_type"] == "high_ctr"
    assert alerts[0]["status"] == "open"


def test_alert_lifecycle_update(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "US", "age": 24, "device": "ios", "interests": "fitness"},
    ).json()
    campaign, _ = create_deliverable_campaign(client)
    delivery = client.post("/ads/request", json={"user_id": user["id"]}).json()
    client.post("/events/click", json={"impression_id": delivery["impression_id"]})
    alert = client.post(f"/quality/campaigns/{campaign['id']}/run").json()[0]

    response = client.patch(
        f"/quality/alerts/{alert['id']}",
        json={
            "status": "investigating",
            "owner": "qa-engineer",
            "resolution_note": "Reviewing suspicious high CTR pattern.",
        },
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == "investigating"
    assert updated["owner"] == "qa-engineer"
    assert updated["resolution_note"] == "Reviewing suspicious high CTR pattern."


def test_invalid_click_is_rejected(client: TestClient) -> None:
    response = client.post("/events/click", json={"impression_id": 999})

    assert response.status_code == 400
    assert response.json()["detail"] == "impression does not exist"


def test_duplicate_conversion_is_rejected(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "US", "age": 24, "device": "ios", "interests": "fitness"},
    ).json()
    create_deliverable_campaign(client)
    delivery = client.post("/ads/request", json={"user_id": user["id"]}).json()
    click = client.post("/events/click", json={"impression_id": delivery["impression_id"]}).json()

    first = client.post(
        "/events/conversion",
        json={"click_id": click["id"], "conversion_value": 79.99},
    )
    second = client.post(
        "/events/conversion",
        json={"click_id": click["id"], "conversion_value": 79.99},
    )

    assert first.status_code == 201
    assert second.status_code == 400
    assert second.json()["detail"] == "duplicate conversion for click"


def test_quality_check_creates_high_cvr_alert(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "US", "age": 24, "device": "ios", "interests": "fitness"},
    ).json()
    campaign, _ = create_deliverable_campaign(client)
    delivery = client.post("/ads/request", json={"user_id": user["id"]}).json()
    click = client.post("/events/click", json={"impression_id": delivery["impression_id"]}).json()
    client.post("/events/conversion", json={"click_id": click["id"], "conversion_value": 79.99})

    response = client.post(f"/quality/campaigns/{campaign['id']}/run")

    alert_types = {alert["alert_type"] for alert in response.json()}
    assert "high_cvr" in alert_types


def test_quality_check_creates_duplicate_click_pattern_alert(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "US", "age": 24, "device": "ios", "interests": "fitness"},
    ).json()
    campaign, _ = create_deliverable_campaign(client)
    delivery = client.post("/ads/request", json={"user_id": user["id"]}).json()

    for _ in range(4):
        client.post("/events/click", json={"impression_id": delivery["impression_id"]})

    response = client.post(f"/quality/campaigns/{campaign['id']}/run")

    alert_types = {alert["alert_type"] for alert in response.json()}
    assert "duplicate_click_pattern" in alert_types
