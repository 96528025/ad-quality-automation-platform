# Test Plan

## Scope

This project validates a mini advertising workflow: campaign creation, ad delivery, impression tracking, click tracking, conversion attribution, metrics, and quality alerts.

## Test Layers

- Unit tests validate targeting, campaign eligibility, and rule calculations.
- API tests validate request/response behavior and input validation.
- Integration tests validate end-to-end delivery, click, conversion, metrics, and quality checks.
- Performance tests use Locust to exercise high-volume `/ads/request` traffic.
- CI runs the automated regression suite on every push and pull request.
- Quality gates include Ruff linting, mypy type checking, and pytest coverage.
- Event pipeline tests validate raw event ingestion, processing status transitions, materialization, and failed-event handling.
- Invalid-traffic tests validate risk scoring, event filtering, and alert creation before clicks affect spend or metrics.

## Key Quality Risks

- Paused or over-budget campaigns may still be delivered.
- Targeting rules may deliver ads to the wrong country or age range.
- Clicks may be accepted without a valid impression.
- Conversions may be attributed outside the allowed window.
- Abnormal CTR/CVR patterns may go undetected.
- Repeated click patterns may indicate invalid or suspicious traffic.
- Database schema drift may break staging or production deploys without Alembic migrations.
- Alert ownership/status gaps may make quality issues hard to track through resolution.
- Raw event processing failures may silently drop ad events without pending/processed/failed tracking.
- High-risk click traffic may incorrectly affect billing and CTR/CVR metrics if not filtered before materialization.
