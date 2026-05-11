# Sample Bug Reports

## BUG-001: Paused Campaign Delivered

- Severity: High
- Area: Ad delivery
- Steps: Create a paused campaign, create an eligible user, request an ad.
- Expected: No ad should be returned.
- Actual: Paused campaign was returned.
- Root cause: Delivery eligibility did not check campaign status.
- Fix validation: Added unit test for paused campaign and API regression coverage.

## BUG-002: Conversion Accepted Outside Attribution Window

- Severity: Medium
- Area: Conversion attribution
- Steps: Create click event, submit conversion with timestamp 8 days later.
- Expected: Conversion should be rejected.
- Actual: Conversion was accepted.
- Root cause: Attribution service did not compare conversion time against click time.
- Fix validation: Added integration test for 7-day attribution window.

## BUG-003: Demo Flow Metrics Read Wrong Campaign

- Severity: Medium
- Area: Ad delivery and test data isolation
- Steps: Run the demo script against a database that already contains older active campaigns with the same bid.
- Expected: The newly created campaign should receive the demo impression and click.
- Actual: Delivery selected an older matching campaign, so the newly created campaign showed zero metrics.
- Root cause: Delivery tie-breaking only considered bid and did not provide deterministic selection among equal bids.
- Fix validation: Added deterministic tie-breaking by bid and campaign ID; demo reads metrics from the delivered campaign.

## BUG-004: Raw Event Silently Dropped

- Severity: High
- Area: Event ingestion pipeline
- Steps: Submit a click event with an invalid `impression_id`.
- Expected: The event should be retained and marked failed with a clear error.
- Actual: Without event status tracking, invalid events could be lost after API rejection.
- Root cause: Direct API-to-table writes do not preserve failed raw event attempts.
- Fix validation: Added `ad_events` table with `pending`, `processed`, and `failed` states plus processor tests.
