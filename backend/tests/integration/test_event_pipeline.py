from fastapi.testclient import TestClient


def create_campaign_ad_user(client: TestClient) -> tuple[dict, dict, dict]:
    user = client.post(
        "/users",
        json={"country": "US", "age": 24, "device": "ios", "interests": "fitness"},
    ).json()
    campaign = client.post(
        "/campaigns",
        json={
            "advertiser_name": "Nike",
            "daily_budget": 500,
            "bid_cpc": 1.2,
            "target_country": "US",
            "target_age_min": 18,
            "target_age_max": 35,
            "target_device": "ios",
            "target_interests": "fitness",
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
    return campaign, ad, user


def test_ingested_impression_event_is_processed_into_metrics(client: TestClient) -> None:
    campaign, ad, user = create_campaign_ad_user(client)
    event = client.post(
        "/events/ingest",
        json={
            "event_type": "impression",
            "campaign_id": campaign["id"],
            "ad_id": ad["id"],
            "user_id": user["id"],
        },
    ).json()

    result = client.post("/events/process-pending").json()
    metrics = client.get(f"/metrics/campaigns/{campaign['id']}").json()

    assert event["status"] == "pending"
    assert result == {"processed": 1, "failed": 0}
    assert metrics["impressions"] == 1
    assert metrics["clicks"] == 0


def test_ingested_click_and_conversion_events_are_materialized(client: TestClient) -> None:
    campaign, ad, user = create_campaign_ad_user(client)
    impression_event = client.post(
        "/events/ingest",
        json={
            "event_type": "impression",
            "campaign_id": campaign["id"],
            "ad_id": ad["id"],
            "user_id": user["id"],
        },
    ).json()
    client.post("/events/process-pending")
    processed_impression_event = client.get(f"/events/{impression_event['id']}").json()

    click_event = client.post(
        "/events/ingest",
        json={"event_type": "click", "impression_id": processed_impression_event["materialized_id"]},
    ).json()
    client.post("/events/process-pending")
    processed_click_event = client.get(f"/events/{click_event['id']}").json()

    client.post(
        "/events/ingest",
        json={
            "event_type": "conversion",
            "click_id": processed_click_event["materialized_id"],
            "conversion_value": 79.99,
        },
    )
    result = client.post("/events/process-pending").json()
    metrics = client.get(f"/metrics/campaigns/{campaign['id']}").json()

    assert result == {"processed": 1, "failed": 0}
    assert processed_impression_event["status"] == "processed"
    assert processed_click_event["status"] == "processed"
    assert metrics["impressions"] == 1
    assert metrics["clicks"] == 1
    assert metrics["conversions"] == 1
    assert metrics["spend"] == 1.2


def test_invalid_ingested_click_event_is_marked_failed(client: TestClient) -> None:
    event = client.post(
        "/events/ingest",
        json={"event_type": "click", "impression_id": 999},
    ).json()

    result = client.post("/events/process-pending").json()

    assert event["status"] == "pending"
    assert result == {"processed": 0, "failed": 1}


def test_high_risk_click_event_is_filtered_and_alerted(client: TestClient) -> None:
    campaign, _, user = create_campaign_ad_user(client)
    delivery = client.post("/ads/request", json={"user_id": user["id"]}).json()
    for _ in range(3):
        client.post("/events/click", json={"impression_id": delivery["impression_id"]})

    for _ in range(20):
        client.post(
            "/events/ingest",
            json={"event_type": "click", "impression_id": 999, "ip_address": "10.0.0.1"},
        )
    warmup_result = client.post("/events/process-pending").json()

    risky_event = client.post(
        "/events/ingest",
        json={
            "event_type": "click",
            "impression_id": delivery["impression_id"],
            "ip_address": "10.0.0.1",
        },
    ).json()
    result = client.post("/events/process-pending").json()
    processed_event = client.get(f"/events/{risky_event['id']}").json()
    metrics = client.get(f"/metrics/campaigns/{campaign['id']}").json()
    alerts = client.get("/quality/alerts").json()

    assert warmup_result == {"processed": 0, "failed": 20}
    assert result == {"processed": 0, "failed": 1}
    assert processed_event["status"] == "failed"
    assert processed_event["is_invalid"] is True
    assert processed_event["risk_score"] >= 70
    assert "high_ip_click_volume" in processed_event["invalid_reason"]
    assert metrics["clicks"] == 3
    assert any(alert["alert_type"] == "invalid_traffic_risk" for alert in alerts)
