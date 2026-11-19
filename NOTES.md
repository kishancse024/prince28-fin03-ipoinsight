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
