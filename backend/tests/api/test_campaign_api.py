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


def test_request_ad_uses_effective_ranking_score_not_bid_only(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "US", "age": 25, "device": "ios", "interests": "sports"},
    ).json()
    high_bid_low_quality = client.post(
        "/campaigns",
        json={
            "advertiser_name": "High Bid Low Quality",
            "daily_budget": 100,
            "bid_cpc": 5.0,
            "target_country": "US",
            "target_age_min": 18,
            "target_age_max": 35,
        },
    ).json()
    lower_bid_high_quality = client.post(
        "/campaigns",
        json={
            "advertiser_name": "Lower Bid High Quality",
            "daily_budget": 100,
            "bid_cpc": 2.0,
            "target_country": "US",
            "target_age_min": 18,
            "target_age_max": 35,
        },
    ).json()
    client.post(
        f"/campaigns/{high_bid_low_quality['id']}/ads",
        json={
            "campaign_id": high_bid_low_quality["id"],
            "title": "High Bid",
            "landing_url": "https://example.com/high-bid",
            "predicted_ctr": 0.01,
            "quality_score": 0.5,
        },
    )
    client.post(
        f"/campaigns/{lower_bid_high_quality['id']}/ads",
        json={
            "campaign_id": lower_bid_high_quality["id"],
            "title": "Effective Winner",
            "landing_url": "https://example.com/effective",
            "predicted_ctr": 0.1,
            "quality_score": 0.9,
        },
    )

    response = client.post("/ads/request", json={"user_id": user["id"]})

    assert response.status_code == 200
    assert response.json()["campaign_id"] == lower_bid_high_quality["id"]
    assert response.json()["ranking_score"] == 0.18


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


def test_request_ad_rejects_device_targeting_mismatch(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "US", "age": 25, "device": "android", "interests": "sports"},
    ).json()
    campaign = client.post(
        "/campaigns",
        json={
            "advertiser_name": "iOS Brand",
            "daily_budget": 100,
            "bid_cpc": 1.0,
            "target_country": "US",
            "target_age_min": 18,
            "target_age_max": 35,
            "target_device": "ios",
        },
    ).json()
    client.post(
        f"/campaigns/{campaign['id']}/ads",
        json={
            "campaign_id": campaign["id"],
            "title": "iOS Only",
            "landing_url": "https://example.com/ios",
        },
    )

    response = client.post("/ads/request", json={"user_id": user["id"]})

    assert response.status_code == 404
    assert response.json()["detail"] == "no eligible ad found"


def test_request_ad_rejects_interest_targeting_mismatch(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "US", "age": 25, "device": "ios", "interests": "cooking"},
    ).json()
    campaign = client.post(
        "/campaigns",
        json={
            "advertiser_name": "Sports Brand",
            "daily_budget": 100,
            "bid_cpc": 1.0,
            "target_country": "US",
            "target_age_min": 18,
            "target_age_max": 35,
            "target_interests": "sports,fitness",
        },
    ).json()
    client.post(
        f"/campaigns/{campaign['id']}/ads",
        json={
            "campaign_id": campaign["id"],
            "title": "Sports Only",
            "landing_url": "https://example.com/sports",
        },
    )

    response = client.post("/ads/request", json={"user_id": user["id"]})

    assert response.status_code == 404
    assert response.json()["detail"] == "no eligible ad found"


def test_request_ad_rejects_unapproved_ad(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "US", "age": 25, "device": "ios", "interests": "sports"},
    ).json()
    campaign = client.post(
        "/campaigns",
        json={
            "advertiser_name": "Pending Review Brand",
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
            "title": "Pending",
            "landing_url": "https://example.com/pending",
            "review_status": "pending",
        },
    )

    response = client.post("/ads/request", json={"user_id": user["id"]})

    assert response.status_code == 404
    assert response.json()["detail"] == "no eligible ad found"


def test_frequency_cap_blocks_overexposure(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "US", "age": 25, "device": "ios", "interests": "sports"},
    ).json()
    campaign = client.post(
        "/campaigns",
        json={
            "advertiser_name": "Capped Brand",
            "daily_budget": 100,
            "bid_cpc": 1.0,
            "target_country": "US",
            "target_age_min": 18,
            "target_age_max": 35,
            "frequency_cap_per_day": 1,
        },
    ).json()
    client.post(
        f"/campaigns/{campaign['id']}/ads",
        json={
            "campaign_id": campaign["id"],
            "title": "Capped",
            "landing_url": "https://example.com/capped",
        },
    )

    first = client.post("/ads/request", json={"user_id": user["id"]})
    second = client.post("/ads/request", json={"user_id": user["id"]})

    assert first.status_code == 200
    assert second.status_code == 404
    assert second.json()["detail"] == "no eligible ad found"


def test_budget_pacing_blocks_overspend_ahead_of_schedule(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={"country": "US", "age": 25, "device": "ios", "interests": "sports"},
    ).json()
    campaign = client.post(
        "/campaigns",
        json={
            "advertiser_name": "Paced Brand",
            "daily_budget": 100000,
            "bid_cpc": 100000,
            "target_country": "US",
            "target_age_min": 18,
            "target_age_max": 35,
            "pacing_enabled": True,
        },
    ).json()
    client.post(
        f"/campaigns/{campaign['id']}/ads",
        json={
            "campaign_id": campaign["id"],
            "title": "Paced",
            "landing_url": "https://example.com/paced",
        },
    )

    response = client.post("/ads/request", json={"user_id": user["id"]})

    assert response.status_code == 404
    assert response.json()["detail"] == "no eligible ad found"
