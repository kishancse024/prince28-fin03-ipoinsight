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
