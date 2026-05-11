from app import models
from app.services.delivery import user_matches_campaign


def test_user_matches_active_campaign_with_budget_and_targeting() -> None:
    user = models.User(country="US", age=24, device="ios")
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

    assert user_matches_campaign(user, campaign) is True


def test_paused_campaign_is_not_eligible() -> None:
    user = models.User(country="US", age=24, device="ios")
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

    assert user_matches_campaign(user, campaign) is False


def test_campaign_without_click_budget_is_not_eligible() -> None:
    user = models.User(country="US", age=24, device="ios")
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

    assert user_matches_campaign(user, campaign) is False

