# IPOInsight
[![CI](https://github.com/kishancse024/prince28-fin03-ipoinsight/actions/workflows/ci.yml/badge.svg)](https://github.com/kishancse024/prince28-fin03-ipoinsight/actions/workflows/ci.yml)
[![Live](https://img.shields.io/website?url=https%3A%2F%2Fipoinsight.onrender.com%2Fhealth&label=live)](https://ipoinsight.onrender.com/docs)
[![Uptime (30 days)](https://img.shields.io/uptimerobot/ratio/m804746237-976e480f019dde8f7bc5e789)](https://ipoinsight.onrender.com/health)

**Live:** https://ipoinsight.onrender.com · [API docs](https://ipoinsight.onrender.com/docs) · [health](https://ipoinsight.onrender.com/health)


Explains an upcoming IPO from its offer document: offer for sale vs fresh issue, use of money, risks and financials, with page citations.

**Status:** Week 1 complete · live at https://ipoinsight.onrender.com

## Who it's for

Retail investor in Trichy who applies for 2-3 IPOs a month and wants to understand the risks first.

## The problem

Retail investors often find it difficult to understand lengthy offer documents that can run 300–500 pages and contain complex information and dense tables. Going through these documents takes a lot of time and can be confusing for beginners. As a result, many investors skip reading them and rely on social media tips or advice from others. This can lead to uninformed investment decisions and unnecessary financial risks.

## Data sources

SEBI draft offer documents (DRHPs) and red herring prospectuses for 40+ recent IPOs, SEBI ICDR Regulations.

- https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=3&ssid=15&smid=10
- https://www.sebi.gov.in/
- Terms: Public SEBI filings. Cite page numbers.

## Hardest problem (my interview story)

Very long documents with financial tables: 'how much of the issue is offer for sale' needs table extraction and calculation, and comparing two IPOs needs cross-document retrieval without mixing companies.

## Signature feature

IPO X-ray: one card per IPO with offer for sale vs fresh issue, use of proceeds, top risk factors and promoter holding before/after, each linked to its page.

## Target metric

Key-number accuracy of 95%+ across 20 IPOs x 8 fields.

## Run it locally

```bash
uv sync
cp .env.example .env   # Windows: copy .env.example .env
uv run uvicorn ipoinsight.api.main:create_app --factory --reload
```

Then open http://localhost:8000/docs

## Checks

```bash
uv run pytest
uv run ruff check .
```

## Why I changed these targets
Speed: "Adjusted full-answer latency target to 6 s to accommodate hybrid search and cross-encoder reranking across 400+ page DRHP documents without sacrificing citation accuracy."

 Cost: "Raised cost ceiling to Rs 1.25 per query to allow passing larger context windows (top-8 chunks) needed to accurately read multi-page financial tables in RHP filings."

## Run locally in one command

You need Docker Desktop running. From a fresh clone:

```bash
docker compose up --build
```

This starts Postgres (with pgvector), Redis, runs the migrations and loads the sample data once, then starts the API.

- API docs: http://localhost:8000/docs
- Liveness: http://localhost:8000/health
- Readiness (checks the database): http://localhost:8000/ready

Stop with `Ctrl+C`, then `docker compose down`. Add `-v` to also delete the database volume.

## Develop and test

| Task | Mac / Linux | Windows |
|---|---|---|
| Run the API with reload | `make dev` | `uv run poe dev` |
| Unit tests (no network) | `make test` | `uv run poe test` |
| Integration tests (needs `docker compose up`) | `make test-integration` | `uv run poe test-integration` |
| Coverage report | `make cov` | `uv run poe cov` |
| Lint and format check | `make lint` | `uv run poe lint` |
