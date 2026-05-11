from fastapi.testclient import TestClient


def test_create_campaign_rejects_negative_budget(client: TestClient) -> None:
    response = client.post(
        "/campaigns",
        json={
            "advertiser_name": "Acme",
            "daily_budget": -100,
            "bid_cpc": 1.2,
            "target_country": "US",
            "target_age_min": 18,
            "target_age_max": 35,
        },
    )

    assert response.status_code == 422


def test_request_ad_returns_highest_bid_eligible_campaign(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "US", "age": 25, "device": "ios", "interests": "sports"},
    ).json()
    low_campaign = client.post(
        "/campaigns",
        json={
            "advertiser_name": "Low Bid",
            "daily_budget": 100,
            "bid_cpc": 1.0,
            "target_country": "US",
            "target_age_min": 18,
            "target_age_max": 35,
        },
    ).json()
    high_campaign = client.post(
        "/campaigns",
        json={
            "advertiser_name": "High Bid",
            "daily_budget": 100,
            "bid_cpc": 2.0,
            "target_country": "US",
            "target_age_min": 18,
            "target_age_max": 35,
        },
    ).json()
    client.post(
        f"/campaigns/{low_campaign['id']}/ads",
        json={
            "campaign_id": low_campaign["id"],
            "title": "Low",
            "landing_url": "https://example.com/low",
        },
    )
    client.post(
        f"/campaigns/{high_campaign['id']}/ads",
        json={
            "campaign_id": high_campaign["id"],
            "title": "High",
            "landing_url": "https://example.com/high",
        },
    )

    response = client.post("/ads/request", json={"user_id": user["id"]})

    assert response.status_code == 200
    assert response.json()["campaign_id"] == high_campaign["id"]


def test_request_ad_rejects_country_targeting_mismatch(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "CA", "age": 25, "device": "ios", "interests": "sports"},
    ).json()
    campaign = client.post(
        "/campaigns",
        json={
            "advertiser_name": "US Brand",
            "daily_budget": 100,
            "bid_cpc": 1.0,
            "target_country": "US",
            "target_age_min": 18,
            "target_age_max": 35,
        },
    ).json()
    client.post(
        f"/campaigns/{campaign['id']}/ads",
        json={
            "campaign_id": campaign["id"],
            "title": "US Only",
            "landing_url": "https://example.com/us",
        },
    )

    response = client.post("/ads/request", json={"user_id": user["id"]})

    assert response.status_code == 404
    assert response.json()["detail"] == "no eligible ad found"


def test_request_ad_rejects_age_targeting_mismatch(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "US", "age": 17, "device": "ios", "interests": "sports"},
    ).json()
    campaign = client.post(
        "/campaigns",
        json={
            "advertiser_name": "Adult Brand",
            "daily_budget": 100,
            "bid_cpc": 1.0,
            "target_country": "US",
            "target_age_min": 18,
            "target_age_max": 35,
        },
    ).json()
    client.post(
        f"/campaigns/{campaign['id']}/ads",
        json={
            "campaign_id": campaign["id"],
            "title": "Age Targeted",
            "landing_url": "https://example.com/age",
        },
    )

    response = client.post("/ads/request", json={"user_id": user["id"]})

    assert response.status_code == 404
    assert response.json()["detail"] == "no eligible ad found"
