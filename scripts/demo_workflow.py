import argparse
from pprint import pprint

import httpx


def post(client: httpx.Client, path: str, payload: dict | None = None) -> dict | list:
    response = client.post(path, json=payload)
    response.raise_for_status()
    return response.json()


def get(client: httpx.Client, path: str) -> dict | list:
    response = client.get(path)
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a full ad quality demo workflow against the API.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    with httpx.Client(base_url=args.base_url, timeout=10) as client:
        user = post(
            client,
            "/users",
            {"country": "US", "age": 24, "device": "ios", "interests": "fitness sports"},
        )
        print("\nCreated user")
        pprint(user)

        campaign = post(
            client,
            "/campaigns",
            {
                "advertiser_name": "Nike",
                "daily_budget": 500,
                "bid_cpc": 1.2,
                "target_country": "US",
                "target_age_min": 18,
                "target_age_max": 35,
                "target_device": "ios",
                "target_interests": "fitness,sports",
                "frequency_cap_per_day": 10,
                "pacing_enabled": False,
                "status": "active",
            },
        )
        print("\nCreated campaign")
        pprint(campaign)

        ad = post(
            client,
            f"/campaigns/{campaign['id']}/ads",
            {
                "campaign_id": campaign["id"],
                "title": "Running Shoes",
                "landing_url": "https://example.com/shoes",
                "creative_url": "https://example.com/shoes.png",
                "review_status": "approved",
                "predicted_ctr": 0.08,
                "quality_score": 0.9,
            },
        )
        print("\nCreated ad")
        pprint(ad)

        delivery = post(client, "/ads/request", {"user_id": user["id"]})
        print("\nDelivered ad")
        pprint(delivery)

        click = post(client, "/events/click", {"impression_id": delivery["impression_id"]})
        print("\nRecorded click")
        pprint(click)

        conversion = post(client, "/events/conversion", {"click_id": click["id"], "conversion_value": 79.99})
        print("\nRecorded conversion")
        pprint(conversion)

        delivered_campaign_id = delivery["campaign_id"]
        metrics = get(client, f"/metrics/campaigns/{delivered_campaign_id}")
        print("\nCampaign metrics")
        pprint(metrics)

        alerts = post(client, f"/quality/campaigns/{delivered_campaign_id}/run")
        print("\nQuality alerts")
        pprint(alerts)


if __name__ == "__main__":
    main()
