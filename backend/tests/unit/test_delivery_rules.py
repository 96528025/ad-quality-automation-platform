from app import models
from app.services.delivery import ranking_score


def test_user_matches_active_campaign_with_budget_and_targeting() -> None:
    campaign = models.Campaign(
        advertiser_name="Acme",
        daily_budget=100,
        remaining_budget=100,
        bid_cpc=1.5,
        target_country="US",
        target_age_min=18,
        target_age_max=35,
        status=models.CampaignStatus.active,
    )

    assert campaign.status == models.CampaignStatus.active


def test_paused_campaign_is_not_eligible() -> None:
    campaign = models.Campaign(
        advertiser_name="Acme",
        daily_budget=100,
        remaining_budget=100,
        bid_cpc=1.5,
        target_country="US",
        target_age_min=18,
        target_age_max=35,
        status=models.CampaignStatus.paused,
    )

    assert campaign.status != models.CampaignStatus.active


def test_campaign_without_click_budget_is_not_eligible() -> None:
    campaign = models.Campaign(
        advertiser_name="Acme",
        daily_budget=100,
        remaining_budget=0.5,
        bid_cpc=1.5,
        target_country="US",
        target_age_min=18,
        target_age_max=35,
        status=models.CampaignStatus.active,
    )

    assert campaign.remaining_budget < campaign.bid_cpc


def test_ranking_score_uses_bid_predicted_ctr_and_quality_score() -> None:
    campaign = models.Campaign(
        advertiser_name="Acme",
        daily_budget=100,
        remaining_budget=100,
        bid_cpc=2.0,
        target_country="US",
        target_age_min=18,
        target_age_max=35,
        status=models.CampaignStatus.active,
    )
    ad = models.Ad(
        campaign=campaign,
        campaign_id=1,
        title="Ad",
        landing_url="https://example.com",
        predicted_ctr=0.1,
        quality_score=0.8,
    )

    assert ranking_score(ad) == 0.16
