# IPOInsight

Explains an upcoming IPO from its offer document: offer for sale vs fresh issue, use of money, risks and financials, with page citations.

**Status:** Day 1 foundation (FastAPI skeleton, quality gates). Live URL from Day 5.

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
