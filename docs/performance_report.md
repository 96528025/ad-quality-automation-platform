# Performance Report

## Latest Local Result

Run date: 2026-05-11

Environment:

- Machine: local MacBook Air development environment
- API: FastAPI + SQLite local database
- Server: `uvicorn app.main:app --host 127.0.0.1 --port 8003`
- Load: 100 Locust users, spawn rate 10 users/sec, 1 minute

Summary:

| Endpoint | Requests | Failures | Avg Latency | p50 | p95 | p99 | Max | RPS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `POST /ads/request` | 7,210 | 0 | 10.31 ms | 7 ms | 21 ms | 62 ms | 408 ms | 126.30 |
| `GET /quality/alerts` | 1,543 | 0 | 4.33 ms | 3 ms | 7 ms | 29 ms | 209 ms | 27.03 |
| `POST /users` | 100 | 0 | 40.77 ms | 30 ms | 120 ms | 200 ms | 203 ms | 1.75 |
| Aggregated | 8,853 | 0 | 9.61 ms | 6 ms | 21 ms | 70 ms | 408 ms | 155.08 |

Result:

- Failure rate: 0.00%
- `/ads/request` p95 latency: 21 ms
- Aggregated p95 latency: 21 ms
- Generated artifacts: `performance/report.html`, `performance/results_stats.csv`

## Test Setup

- Tool: Locust
- Scenario: Synthetic users repeatedly call `/ads/request` and `/quality/alerts`
- Default target: `http://127.0.0.1:8000`
- Default load profile: 100 users, 10 users spawned per second, 1 minute run time

## How to Run

Start the API, then run from the project root:

```bash
cd backend
.venv/bin/locust -f ../performance/locustfile.py --host http://127.0.0.1:8000 --headless -u 100 -r 10 -t 1m --html ../performance/report.html --csv ../performance/results
```

## Metrics to Capture

| Metric | Why It Matters |
| --- | --- |
| RPS | Measures ad request throughput |
| p50 latency | Typical user-facing response time |
| p95 latency | Tail latency under load |
| Failure rate | Stability and correctness under traffic |

## Acceptance Criteria

For this MVP, a reasonable local baseline is:

- Failure rate below 1%
- p95 latency below 300 ms on `/ads/request`
- No server crashes during the run

Record actual results after running Locust on your machine.
