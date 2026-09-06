# Ad Quality Automation Platform

A testing-focused mini ad platform that simulates campaign creation, ad delivery, event ingestion, conversion attribution, quality alerts, synthetic traffic, and automated regression testing.

It is not intended to be a production ad server. The goal is to model realistic quality risks in advertising systems and validate them through API, integration, and performance tests.

## Tech Stack

- Backend: FastAPI, SQLAlchemy
- Database: SQLite by default, PostgreSQL-compatible SQLAlchemy setup
- Testing: Pytest, FastAPI TestClient
- Performance: Locust
- Data: Synthetic seed and traffic generation scripts
- CI: GitHub Actions

## Core Workflow

1. Create a campaign with budget, bid, status, and targeting rules.
2. Create an ad under the campaign.
3. Configure ad review status, frequency caps, pacing, and ranking inputs.
4. Create synthetic users.
5. Request an ad for a user.
6. Select eligible ads using status, review approval, targeting, budget, pacing, frequency caps, and ranking score.
7. Store an impression when an ad is delivered.
8. Ingest raw ad events into a DB-backed event queue.
9. Process pending events into impressions, clicks, conversions, and hourly metrics.
10. Record clicks against impressions and deduct CPC budget.
11. Record conversions against clicks within a 7-day attribution window.
12. Calculate CTR, CVR, spend, and remaining budget.
13. Run quality checks for abnormal CTR/CVR and repeated click patterns.

## Run Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs are available at:

```text
http://127.0.0.1:8000/docs
```

The guided demo dashboard is available at:

```text
http://127.0.0.1:8000/
```

If file watching is restricted on your machine, run without reload:

```bash
uvicorn app.main:app
```

## Run with Docker and PostgreSQL

```bash
docker compose up --build
```

The dashboard will be available at:

```text
http://127.0.0.1:8000/
```

## Run Tests

```bash
cd backend
pytest
```

The test command also generates a coverage report through `pytest-cov`.

## Code Quality Gates

```bash
cd backend
ruff check .
mypy app
pytest
```

Current local validation covers linting, type checking, 16 automated tests, and coverage reporting.

## Database Migrations

Alembic manages schema migrations for PostgreSQL and SQLite-compatible local development.

```bash
cd backend
alembic upgrade head
```

When using Docker Compose, migrations run automatically before the API starts.

## Generate Synthetic Data

From the project root:

```bash
python scripts/seed_data.py
python scripts/generate_traffic.py
python scripts/inject_anomalies.py
```

Reset the local SQLite database:

```bash
python scripts/reset_data.py
```

## Run One-Command Demo Flow

With the API running:

```bash
python scripts/demo_workflow.py --base-url http://127.0.0.1:8000
```

## Run Event Worker

The project includes a lightweight DB-backed event pipeline to simulate production-style ingestion and asynchronous processing.

```bash
cd backend
python -m app.workers.event_worker
```

Useful event pipeline endpoints:

```text
POST /events/ingest
POST /events/process-pending
GET /events/{event_id}
```

## Run Performance Test

Start the API first, then run:

```bash
locust -f performance/locustfile.py --host http://127.0.0.1:8000
```

Or run the headless baseline:

```bash
cd backend
.venv/bin/locust -f ../performance/locustfile.py --host http://127.0.0.1:8000 --headless -u 100 -r 10 -t 1m --html ../performance/report.html --csv ../performance/results
```

See [docs/performance_report.md](docs/performance_report.md) for the latest recorded local results.

## Production-Readiness Features

- PostgreSQL-ready database configuration with Alembic migrations
- Ruff linting, mypy type checking, and pytest coverage reporting
- `/health` and `/ready` endpoints for service and database readiness checks
- Structured JSON request logs with request IDs and latency
- Alert lifecycle fields: `open`, `acknowledged`, `investigating`, `resolved`, `false_positive`
- Hourly campaign metrics aggregation table for scalable metrics reads
- Delivery decision features: ad review status, frequency capping, device/interest targeting, budget pacing, and effective ranking score
- Simplified ranking model: `score = bid_cpc * predicted_ctr * quality_score`
- DB-backed raw event pipeline with `pending`, `processed`, and `failed` statuses
- Worker-style event processor that materializes raw events into impressions, clicks, conversions, and hourly metrics
- Lightweight invalid-traffic detection using IP, device ID, user-agent, repeated-click signals, and rule-based risk scoring
- High-risk click events are filtered before materialization, so they do not affect spend or CTR/CVR metrics

## Project Structure

```text
backend/
  app/
    routers/
    services/
    main.py
    models.py
    schemas.py
  tests/
    unit/
    api/
    integration/
scripts/
performance/
docs/
.github/workflows/
```

---

# 广告质量自动化测试平台

这是一个以测试开发和质量保障为核心的小型广告系统项目，用于模拟广告活动创建、广告投放、事件采集、转化归因、质量告警、合成流量生成和自动化回归测试。

它不是生产级广告服务器，而是通过一个简化的广告业务系统，模拟工业界广告系统中常见的质量风险，并用 API 测试、集成测试、性能测试和质量规则进行验证。

## 技术栈

- 后端：FastAPI, SQLAlchemy
- 数据库：默认使用 SQLite，同时支持 PostgreSQL 配置
- 测试：Pytest, FastAPI TestClient
- 性能测试：Locust
- 数据：合成种子数据和流量生成脚本
- CI：GitHub Actions

## 核心业务流程

1. 创建带有预算、出价、状态和定向规则的广告活动。
2. 在广告活动下创建广告创意。
3. 配置广告审核状态、频控、预算 pacing 和排序输入。
4. 创建合成用户数据。
5. 用户请求广告。
6. 系统根据状态、审核结果、定向规则、预算、pacing、频控和排序分选择可投放广告。
7. 广告成功投放后记录曝光事件。
8. 将原始广告事件写入 DB-backed event queue。
9. 由 processor 将 pending 事件物化为曝光、点击、转化和小时级 metrics。
10. 根据曝光记录点击事件，并扣减 CPC 预算。
11. 在 7 天归因窗口内记录转化事件。
12. 计算 CTR、CVR、花费和剩余预算。
13. 针对异常 CTR/CVR 和重复点击模式运行质量检测。

## 本地运行

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API 文档地址：

```text
http://127.0.0.1:8000/docs
```

可视化演示页面：

```text
http://127.0.0.1:8000/
```

如果本机文件监听受限，可以不使用 reload：

```bash
uvicorn app.main:app
```

## 使用 Docker 和 PostgreSQL 运行

```bash
docker compose up --build
```

启动后访问：

```text
http://127.0.0.1:8000/
```

## 运行测试

```bash
cd backend
pytest
```

测试命令会通过 `pytest-cov` 生成覆盖率报告。

## 代码质量检查

```bash
cd backend
ruff check .
mypy app
pytest
```

当前本地验证包括代码规范检查、类型检查、16 个自动化测试和测试覆盖率报告。

## 数据库迁移

项目使用 Alembic 管理 PostgreSQL 和本地 SQLite 兼容的数据库 schema 迁移。

```bash
cd backend
alembic upgrade head
```

使用 Docker Compose 启动时，API 服务启动前会自动执行数据库迁移。

## 生成合成数据

在项目根目录执行：

```bash
python scripts/seed_data.py
python scripts/generate_traffic.py
python scripts/inject_anomalies.py
```

重置本地 SQLite 数据库：

```bash
python scripts/reset_data.py
```

## 一键演示完整流程

启动 API 后执行：

```bash
python scripts/demo_workflow.py --base-url http://127.0.0.1:8000
```

该脚本会自动完成用户创建、广告活动创建、广告投放、点击、转化、指标查询和质量告警检测。

## 运行事件处理 Worker

项目包含轻量级 DB-backed event pipeline，用于模拟生产环境中的事件采集和异步处理链路。

```bash
cd backend
python -m app.workers.event_worker
```

相关接口：

```text
POST /events/ingest
POST /events/process-pending
GET /events/{event_id}
```

## 运行性能测试

先启动 API，然后执行：

```bash
locust -f performance/locustfile.py --host http://127.0.0.1:8000
```

也可以运行无界面的基准压测：

```bash
cd backend
.venv/bin/locust -f ../performance/locustfile.py --host http://127.0.0.1:8000 --headless -u 100 -r 10 -t 1m --html ../performance/report.html --csv ../performance/results
```

最新本地性能测试结果见 [docs/performance_report.md](docs/performance_report.md)。

## 工业化能力

- 支持 PostgreSQL 的数据库配置和 Alembic schema 迁移
- Ruff 代码规范检查、mypy 类型检查和 pytest 覆盖率报告
- `/health` 和 `/ready` 服务健康检查与数据库就绪检查
- 带 request ID 和 latency 的结构化 JSON 请求日志
- 告警生命周期字段：`open`, `acknowledged`, `investigating`, `resolved`, `false_positive`
- 小时级广告活动指标聚合表，用于提升 metrics 查询扩展性
- 投放决策能力：广告审核状态、频控、设备/兴趣定向、预算 pacing 和有效排序分
- 简化广告排序模型：`score = bid_cpc * predicted_ctr * quality_score`
- DB-backed 原始事件链路，支持 `pending`、`processed`、`failed` 状态
- Worker-style 事件处理器，将原始事件物化为曝光、点击、转化和小时级聚合指标
- 轻量级反异常流量检测，基于 IP、device ID、user-agent、重复点击等信号计算 rule-based risk score
- 高风险 click 事件会在物化前被过滤，不会影响花费、CTR 或 CVR 指标

## 项目结构

```text
backend/
  app/
    routers/
    services/
    main.py
    models.py
    schemas.py
  tests/
    unit/
    api/
    integration/
scripts/
performance/
docs/
.github/workflows/
```
