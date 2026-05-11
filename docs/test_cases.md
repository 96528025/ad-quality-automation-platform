# Test Cases

| ID | Scenario | Expected Result |
| --- | --- | --- |
| TC-001 | Create campaign with negative daily budget | API returns validation error |
| TC-002 | Request ad for user matching multiple campaigns | Highest bid eligible campaign is selected |
| TC-003 | Request ad for paused campaign | Campaign is not eligible |
| TC-004 | Record click with missing impression | API rejects click |
| TC-005 | Record conversion within 7 days | Conversion is accepted |
| TC-006 | Record conversion after 7 days | API rejects conversion |
| TC-007 | Run quality check with CTR > 30% | High CTR alert is created |
| TC-008 | Run quality check with repeated clicks | Duplicate click pattern alert is created |
| TC-009 | Request ad with country mismatch | No eligible ad is returned |
| TC-010 | Request ad with age mismatch | No eligible ad is returned |
| TC-011 | Record click with invalid impression ID | API rejects click |
| TC-012 | Submit duplicate conversion for one click | API rejects duplicate conversion |
| TC-013 | Check `/health` endpoint | API returns service OK |
| TC-014 | Check `/ready` endpoint | API verifies database connectivity |
| TC-015 | Update quality alert lifecycle fields | Alert status, owner, and note are persisted |
| TC-016 | Load campaign metrics after events | Metrics are read from hourly aggregate data |
| TC-017 | Ingest impression raw event | Event starts as pending and processor materializes impression metrics |
| TC-018 | Ingest click and conversion raw events | Processor materializes click/conversion and updates metrics |
| TC-019 | Ingest invalid click event | Processor marks event as failed with no materialized click |
