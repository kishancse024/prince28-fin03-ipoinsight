# Engineering notes: IPOInsight

## D03 · PostgreSQL

### Migrations (upgrade, downgrade, upgrade)

```text
paste the output of:
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running downgrade 7eff8a56024e -> 8dcaa58b7199, add gin index on metadata
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
8dcaa58b7199
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 8dcaa58b7199 -> 7eff8a56024e, add gin index on metadata
8dcaa58b7199 -> 7eff8a56024e (head), add gin index on metadata
<base> -> 8dcaa58b7199, create documents and pages
```

### The loader is idempotent

```text
run 1: records=20 inserted=20 updated=0 unchanged=0

run 2: records=20 inserted=0 updated=0 unchanged=20

run 3 (after editing one record): records=20 inserted=0 updated=1 unchanged=19
```

### EXPLAIN for ?company=VALUE

```text
-- 1) What the planner chooses on its own:
Seq Scan on documents  (cost=0.00..2.25 rows=1 width=36) (actual time=1.409..1.410 rows=1.00 loops=1)
  Filter: (metadata @> '{"company": "Oravel Stays Limited (OYO)"}'::jsonb)
  Rows Removed by Filter: 19
  Buffers: shared read=2 dirtied=2
Planning:
  Buffers: shared hit=118 read=8 dirtied=1
Planning Time: 6.282 ms
Execution Time: 1.445 ms

-- 2) Seq scan switched off, to prove the index can be used:
Bitmap Heap Scan on documents  (cost=8.54..12.56 rows=1 width=36) (actual time=1.155..1.157 rows=1.00 loops=1)
  Recheck Cond: (metadata @> '{"company": "Oravel Stays Limited (OYO)"}'::jsonb)
  Heap Blocks: exact=1
  Buffers: shared hit=2 read=1
  ->  Bitmap Index Scan on ix_documents_metadata_gin  (cost=0.00..8.54 rows=1 width=0) (actual time=1.106..1.106 rows=1.00 loops=1)
        Index Cond: (metadata @> '{"company": "Oravel Stays Limited (OYO)"}'::jsonb)
        Index Searches: 1
        Buffers: shared hit=1 read=1
Planning:
  Buffers: shared hit=1
Planning Time: 0.092 ms
Execution Time: 1.210 ms
```

**Why did the planner choose a Seq Scan on my table? (2 lines, your own words)**

The query planner chose a sequential scan because the table contains very few rows (only 20 records), making a full table scan faster than reading through a GIN index.

Additionally, when a table is extremely small, the overhead of looking up index pages outweighs the cost of reading the entire table sequentially.

**When would it switch to the GIN index? (1 line)**

It will switch to the GIN index once the table grows large enough that filtering out rows sequentially becomes more expensive than index traversal.



## D04 · Docker, Compose and tests

### The image

```text
paste the output of: docker images ipoinsight:dev
IMAGE            ID             DISK USAGE   CONTENT SIZE   EXTRA
ipoinsight:dev   d1df031f07f2        300MB           70MB
paste the output of: docker run --rm ipoinsight:dev id
uid=999(app) gid=999(app) groups=999(app)
```

- Size: 300MB (target: under 400 MB)
- First build: ___ s. After changing one line of code: ___ s.
- Which step said CACHED, and why? (1 line, your own words)

### The stack

```text
paste the output of: docker compose ps -a
NAME                   IMAGE                    COMMAND                  SERVICE   CREATED          STATUS                             PORTS
ipoinsight-api-1       ipoinsight-api           "sh -c 'exec uvicorn…"   api       46 seconds ago   Up 11 seconds (health: starting)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
ipoinsight-db-1        pgvector/pgvector:pg17   "docker-entrypoint.s…"   db        55 seconds ago   Up 41 seconds (healthy)            0.0.0.0:5433->5432/tcp, [::]:5433->5432/tcp
ipoinsight-migrate-1   ipoinsight-migrate       "sh -c 'alembic upgr…"   migrate   48 seconds ago   Exited (0) 14 seconds ago
ipoinsight-redis-1     redis:7-alpine           "docker-entrypoint.s…"   redis     55 seconds ago   Up 42 seconds (healthy)            0.0.0.0:6379->6379/tcp, [::]:6379->6379/tcp
paste the last line of: docker compose logs migrate   (first up, then after down + up)
migrate-1  | records=20 inserted=20 updated=0 unchanged=0
```

### Breaking the database on purpose

```text
db stopped:  /health → {"status":"ok","app":"ipoinsight","env":"local"}
db stopped:  /ready  → {"status":"not_ready","checks":{"database":false}}
db started:  /ready  → {"status":"ready","checks":{"database":true}}
```

Why should a load balancer stop sending traffic here but not restart the app? (2 lines)
The readiness check indicates whether the application can serve requests, including whether its database dependency is available. If the database is down, the load balancer should temporarily stop routing traffic to the application. The application itself should remain running so it can recover when the database becomes available.

### Tests and coverage

```text
uv run poe test              → 16 passed in 6.32s
uv run poe test-integration  → 7 passed in 23.40s
coverage TOTAL, unit only    → 254     36     26      2    83%
coverage TOTAL, with integration tests → TOTAL                                254     36     26      2    83%

9 files skipped due to complete coverage.
16 passed, 7 skipped in 25.80s
```

Two files or lines my coverage report says are never run, and whether they matter: (2 lines)


src/ipoinsight/db/repository.py — 27% coverage. Important because database repository operations may not be tested.

src/ipoinsight/api/deps.py — 64% coverage. Important if the missed lines handle authentication, authorization, or database dependencies.

## D05 · CI/CD and going live

- Live URL: (paste)
- CI run for pull request 1: https://github.com/kishancse024/prince28-fin03-ipoinsight/actions (paste the run link)
- First deploy that ran by itself: (paste the CD run link)
- Merge clicked at __:__ → "Smoke test passed" at __:__ → lead time: ___ min

### Smoke test output from that CD run

```text
ok   /health -> 200, version 532724f37c6631db27e54698faf1fd940867c3f1
ok   /ready -> 200 {'status': 'ready', 'checks': {'database': True}}
ok   /v1/documents?limit=1 -> 200
Smoke test passed
```

### Rollback drill

- Rolled back to sha a15ad7909e4051e8fd92ba8fb7cc6832f0789b44 : started __:__, smoke passed __:__ (___ min)
- Rolled forward to sha 2c082f77d94f27652d393d3f5eb63ffe12d7b1cb  : ___ min
- During the rollback, the database stayed on the newer schema. Why is that safe here? (2 lines)

### Where my secrets live

- Neon string: GitHub Secret DATABASE_URL + Render environment. Not in Git, not in the image.
- Render deploy hook: GitHub Secret RENDER_DEPLOY_HOOK only.

### Monitoring

- UptimeRobot checks /health every 5 minutes; alerts go to my email.
- One thing that would make my live app faster on its first request: (1 line)


## D06 · Collecting the corpus

- Start target: 10 offer documents (about 4,000 pages)
- Collected today: 8 files measured in CAPACITY.md (10 fetched in manifest), 3,360 pages, 78.3 MB (from DATASET.md / CAPACITY.md)
- Doors used: URL list

### Licence check

| Source | Licence or terms, in my words | May I show full text in answers? |
|---|---|---|
| `sebi-gov-in` | Public offer documents and filings hosted by SEBI for public disclosure; cite page numbers and keep source attribution. | Short cited excerpts/summaries are fine for Q&A; avoid reproducing full filings and stick to page-cited snippets per project terms. |
| `bseindia-com` | Public DRHP offer document hosted on BSE's corporate filing portal; cite page numbers. | Same—use cited excerpts/answers rather than reproducing full documents. |
| `bofa-com` | Publicly linked DRHP PDF hosted by a book-running lead manager; cite page numbers. | Same—use cited excerpts/answers rather than reproducing full documents. |

### robots.txt

- Site: `investmentbank.kotak.com`. Its robots.txt says (2 lines): User-agent: *
Allow: /

Sitemap: https://investmentbank.kotak.com/sitemap/sitemap.xml
- Was anything blocked for my bot? Yes—`https://investmentbank.kotak.com/downloads/honasa-consumer-limited-DRHP.pdf` was blocked by `robots.txt`. I respected the block and swapped to a SEBI filing page (`https://www.sebi.gov.in/filings/public-issues/dec-2022/honasa-consumer-limited-drhp_66770.html`) instead of scraping the blocked host.

### Kill and resume

- Run 1: I pressed Ctrl+C after 4 files
- Run 2: downloaded=6 skipped=4
- Run 3: downloaded=0 skipped=10

### Capacity (from docs/CAPACITY.md)

- Tokens per page, measured: 1,006
- Full corpus: 15.09 M tokens, 43,381 chunks, embedding about Rs 247 ($2.60), vectors 133 MB
- The number that surprised me most, and why (2 lines): Embedding the entire 15.09 M-token (43,381-chunk) corpus costs only about Rs 247 ($2.60) once, while vectors take 133 MB and Postgres text takes 72 MB.
  I expected embedding and vector storage across 15,000 pages of offer documents to be much heavier on cost and disk space.

### One thing that went wrong today, and how I fixed it

`dataset_report.py` printed `nothing measurable yet` after downloading because the files on disk weren't sitting at the exact subfolder paths recorded in `data/manifest.jsonl` (`data/raw/<source>/...`) and a stale `.measured.json` cache existed. I verified the files with `pypdf`, moved them into their matching `data/raw/<source>/` folders, removed `.measured.json`, and re-ran `dataset_report.py`.


### Your crawl, in numbers

- **SEBI:** 8 unique files — 56.65 MB; **BSE India:** 1 file — 11.06 MB; **Bank of America:** 1 file — 10.65 MB.
- **Total dataset:** 10 unique documents occupying approximately **78.36 MB** (74.73 MiB).
- **Retries:** 0 files needed more than one attempt; all 10 completed in a single attempt. The manifest does not record individual download durations, so the slowest site cannot be determined from the available data.

## D07 · Parser comparison

<!-- parsers:start -->
| File | Parsers (A / B) | Pages | A found | B found | Time (A / B) | Better, why |
|---|---|---|---|---|---|---|
| 1790743844411-60e4b6b9.pdf | PyMuPDF / pypdf | 444 | 1,487,909 chars, 752 headings, 236 tables | 1,355,925 chars, 6 headings, 0 tables | 321.62 s / 245.85 s | PyMuPDF – Extracts more tables and headings. |
| 1678708849713-63-815583bf.pdf | PyMuPDF / pypdf | 480 | 1,899,579 chars, 2366 headings, 413 tables | 1,737,307 chars, 20 headings, 0 tables | 497.02 s / 103.43 s | PyMuPDF – Preserves more document structure and tables. |
| drhp-20221010162344-587e27fb.pdf | PyMuPDF / pypdf | 505 | 2,146,822 chars, 964 headings, 483 tables | 1,689,505 chars, 7 headings, 0 tables | 415.25 s / 121.10 s | PyMuPDF – Extracts significantly more tables and headings. |
| swiggy-limited-drhp-6e11e7db.pdf | PyMuPDF / pypdf | 532 | 2,400,108 chars, 3020 headings, 313 tables | 1,993,101 chars, 30 headings, 0 tables | 388.92 s / 103.06 s | PyMuPDF – Captures more tables and section headings. |
| 1653979110197-8263105e.pdf | PyMuPDF / pypdf | 399 | 1,710,104 chars, 1618 headings, 340 tables | 1,435,339 chars, 14 headings, 0 tables | 275.50 s / 76.28 s | PyMuPDF – Better extraction of tables and headings. |
| 1729225003827-6df00a71.pdf | PyMuPDF / pypdf | 476 | 2,324,025 chars, 2568 headings, 280 tables | 1,829,476 chars, 16 headings, 0 tables | 268.57 s / 84.87 s | PyMuPDF – Preserves more tables and document structure. |
| 1791286434593-e22dc2c3.pdf | PyMuPDF / pypdf | 511 | 2,360,238 chars, 2103 headings, 461 tables | 1,667,600 chars, 6 headings, 0 tables | 343.10 s / 91.18 s | PyMuPDF – Extracts more tables and meaningful headings. |
| maharashtra-oil-extractions-limited-dap-p-9cc29b | PyMuPDF / pypdf | 13 | 91,688 chars, 20 headings, 14 tables | 49,972 chars, 0 headings, 0 tables | 20.34 s / 3.46 s | PyMuPDF – Finds tables and headings missed by pypdf. |
| honasa-consumer-limited-drhp-66770-bc7b6fc9.html | trafilatura / strip tags | 1 | 219 chars, 0 headings, 0 tables | 301 chars, 0 headings, 0 tables | 1.35 s / 0.00 s | Needs manual inspection – Compare content relevance and HTML boilerplate. |
| ntpc-green-energy-limited-86875-c8bb11f0.html | trafilatura / strip tags | 1 | 209 chars, 0 headings, 0 tables | 286 chars, 0 headings, 0 tables | 0.12 s / 0.00 s | Needs manual inspection – Compare content relevance and HTML boilerplate. |
<!-- parsers:end -->

PyMuPDF was selected for PDF parsing because it extracted significantly more tables and headings than pypdf, preserving useful document structure for IPO analysis. Although pypdf was faster, it missed tables across all tested PDFs. Trafilatura is preferred for HTML when it produces cleaner main-content extraction than simple HTML tag stripping. Manual inspection of representative files is used to validate these results.




### D07 · Parsing my corpus

- Files in the manifest: 10 · parsed: 8 · failed: 0 · pages in Postgres: 3362
- Parsing coverage: 80 % of files

### Failures by reason

| Reason | Files | What I did |
|---|---|---|
| | | |

- The one I fixed: file 1791286434593-e22dc2c3.pdf (database save attempt) , reason database connection closed, fix: committed the read transaction before starting lengthy PDF parsing.
### What I saw when I read my parsed pages

- A page where the heading path is right (document, page, path): swiggy-limited-drhp-6e11e7db.pdf,444,"data/raw/sebi-gov-in/1790743844411-60e4b6b9.pdf"
- Something that came out wrong (document, page, what):nothing
- A table: Markdown grid or loose text? (document, page):nothing

### My parser choice

For PDFs I use PyMuPDF because it found 2,540? tables and substantially more headings than pypdf across the comparison. It found tables in all 8 tested PDFs, while pypdf found zero. PyMuPDF is slower, but preserves more useful structure for IPO analysis.

A kind of document in my corpus that neither parser handles well: HTML pages with very little extracted content

### One thing that went wrong today, and how I fixed it

The PostgreSQL connection closed while saving a parsed PDF after a lengthy parsing operation. I fixed it by committing the initial read transaction before parsing, allowing the database connection to be released and reused when saving the document.



### D08 · LLM gateway

- Primary: gemini-3.8-flash (Gemini) · fallback: openai/gpt-oss-20b (Groq)
- First question on my laptop: first words after 33.38 s, total 33.62 s, tokens in 250 / out 228, cost Rs 0.008279
- Same question on my live URL (second, awake request): first words after ___ s. Day 1 target: under 1.5 s

### Tokens: English against Tamil

| Message | tokens in |
|---|---|
| "Hi" (baseline: mostly my system prompt) | 236 |
|  "Explain in one sentence what a refund is." | 244 |
| "பணத்தைத் திரும்பப் பெறுதல் என்றால் என்ன என்பதை ஒரே வாக்கியத்தில் விளக்கவும்."| 258 |

- The Tamil message needs about 1.0574 times the tokens of the English one.

### What the model does without my documents

- Question 6 ("Will this IPO list at a premium?"): did it admit it can't know? Its exact words: I am not sure. IPO pricing depends on many factors, and the final listing price is determined by the underwriters and market conditions. For accurate information, check the official offer document or consult a financial professional.
- A detail it got wrong or invented (question → what it said → what is true):
- The off-topic question: did it decline in one sentence? Yes, it declined by saying "This question is outside the scope of IPOInsight."

### Fallback and circuit breaker

- With the primary broken: provider groq , fallback YES , first words after 5.18s
- The question at which "llm call gemini … error" stopped appearing in the log: number 4

### The bill

- /v1/usage today: calls 14 , errors 6 , fallbacks 8 , cost Rs 0.575
- Average per answered question: Rs 0.0410  (my Day 1 target: under Rs 0.50)

### One thing that went wrong today, and how I fixed

Fixed the missing database table using an Alembic migration and identified a schema mismatch between the LLM gateway and SQLAlchemy model. Worked on adding the missing fields through another migration.


### Your p95, from your own table

Measured from successful LLM calls in `llm_calls`.

- **p50 latency:** 2,750 ms (2.75 s)
- **p95 latency:** 20,903 ms (20.90 s)
- **Day 1 target:** p95 under 6 seconds
- **Result:** Not met

The p95 latency is approximately 3.48x above the target.

## D09 · Prompt versions compared

<!-- prompts:start -->

| Prompt version | Correct | Accuracy | Invalid replies | Avg tokens in |
|---|---|---|---|---|
| classify_v1 | 12/20 | 60% | 1 | 113 |
| classify_v2 | 20/20 | 100% | 0 | 278 |
| classify_v3 | 20/20 | 100% | 0 | 396 |
| classify_v4 | 20/20 | 100% | 0 | 433 |

<!-- prompts:end -->



### D09 · Prompts and structured output

- My best router prompt: classify_v4 with 20 / 20
- What I changed in v4, and what happened to the score: From 19/20 to 20/20
- The question my best version still gets wrong (line, wanted, got), and why I think so:nothing
- A label in my test set that I changed after seeing the results (or "none"):none
- Input tokens per question: v1 ≈113, best version ≈422 per successful call. Is the extra accuracy worth it? Yes, if avoiding a classification error is important. The best version uses roughly 3.7 times more input tokens but improved accuracy from 95% to 100%.

### My contract (DocMeta)

- Fields I kept from my project card:everything
- Fields I deleted, and why they make no sense per document:nothing
- The field I tightened, and how:

### Extraction run

- Prompt version: `extract_v1` · documents: 10 ok, 2 repaired, 0 failed (of 10 parsed)
- Not finished? Why, and how many are left: Finished. All 10 eligible parsed HTML/PDF documents were processed; 0 left. The 20 manifest records were excluded because they are not parsed documents.
- Most common failure reason, and what I did about it: Two documents needed additional validation attempts. The extraction process retried them and successfully produced valid records. The exact validation error needs to be checked in the extraction logs.
- A record that was valid but wrong (document, field, what it said, what is true): Not yet identified; needs manual verification against the original offer document.
- Cost at list price: Rs 0.59 in total, Rs 0.06 per document.

### One thing that went wrong today, and how I fixed it

The llm_calls usage tracking initially failed because the database schema and SQLAlchemy model were out of sync. I added the missing database migration and verified that the expected columns existed. The /v1/usage endpoint subsequently returned HTTP 200 with usage statistics.


### D10 · Queue and worker

- First run: **7 documents queued**, finished in **1,794 s**. Done **7**, skipped **0**, failed **0**.
- Pace: **256.3 s per document** (INGEST_RPM = **10**, INGEST_CONCURRENCY = **1**).

### Kill test

- Queued: 20. At the kill: queued **15**, running **1**, done **4**, failed **0**.
- After the new worker: done **20** + skipped **0** + failed **0** = **20**.
- Documents in the database: **20**, different IDs: **20** (must be equal).
- The interrupted items came back after **120 s**. Why that long: ARQ retained delayed retry jobs, so the restarted worker waited for their scheduled retry times.
- Why nothing was doubled (one sentence, in my own words): Stable job IDs prevented duplicate active jobs, and document content hashes prevented the same document from being stored twice.

### Dead-letter list

| Stage (parse / extract / download / gave up) | Items | What I did |
|---|---|---|
| None | 0 | No items remained in the dead-letter list; all ingestion jobs completed successfully. |

### Live ingestion

- IPOInsight on Render: **5 of 5 documents done, 0 failed.** The reasons: All five documents were processed successfully without permanent ingestion errors.
- A request without the token gets status **401**.

### Week 2 against Monday's estimate

- docs/CAPACITY.md said: **3,360 pages, 3,379,917 tokens**. docs/INGEST_REPORT.md says: **3,362 pages, 3,604,387 tokens**.
- The difference: **2 additional pages and 224,470 additional tokens (6.64%)**. The actual corpus contained more extracted text than the original estimate because the initial estimate used a limited sample and the 4-characters-per-token approximation.

### One thing that went wrong today, and how I fixed it

The worker encountered `asyncpg.InterfaceError: connection is closed` while inserting a document after lengthy PDF parsing and LLM calls. I changed the processing flow to commit and release database connections before long-running parsing and external LLM operations. I restarted the worker, and all 10 canonical ingestion items eventually completed successfully.
