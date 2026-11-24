# Capacity plan: IPOInsight

Full corpus target: 40+ offer documents + ICDR Regulations (15,000+ pages)

<!-- generated:start -->
## Measured on my start corpus (2026-11-24 04:33 UTC)

| What | Value |
|---|---|
| Files | 8 |
| Size on disk | 78.3 MB |
| Pages (PDF pages + 1 per 3,000 characters of text/HTML) | 3,360 |
| Characters of text | 13,519,667 |
| Estimated tokens (characters / 4) | 3,379,917 |
| Tokens per page | 1,006 |
| PDFs with almost no text (scanned? OCR is Day 7) | 0 |
| Files not measured (zip, xlsx, unreadable) | 0 |

## Estimate for the full corpus (target: 15,000 pages)

| What | How | Value |
|---|---|---|
| Scale factor | target / measured | x 4.5 |
| Tokens | measured tokens x scale | 15.09 M |
| Raw files | measured MB x scale | 350 MB |
| Chunks | tokens / 400 x 1.15 overlap | 43,381 |
| Embedding cost, one time | tokens x 1.15 x $0.15 per 1M | $2.60 = Rs 247 |
| Vector storage | chunks x 768 numbers x 4 bytes | 133 MB |
| Text in Postgres | characters x scale x 1.2 | 72 MB |

Assumptions: 4 characters per token, 400-token chunks, 768-dimension embeddings at $0.15 per 1M tokens, Rs 95 per US dollar.
<!-- generated:end -->

## What I conclude

1. Is embedding cost a problem for this product? No—one-time embedding for the estimated 15.09 M tokens (43,381 chunks) is only $2.60 (about Rs 247)
2. Do the vectors and text fit in my free Postgres? Yes, Estimated vector storage is 133 MB plus 72 MB for text (~205 MB combined before indexes/overhead)
3. Which number above am I least sure about, and how will I measure it better? The 1,006 tokens/page (and 15.09 M full-corpus token) estimate because it uses a 4-character-per-token rule of thumb and samples only 5 pages per PDF; I will measure it better on Day 8 using a real tokenizer across more pages/documents.
4. What changes if the corpus grows 10 times? Tokens (~150.9 M), chunks (~433,810), one-time embedding cost (~$26 / ~Rs 2,470), raw files (~3.5 GB), vector storage (~1.33 GB), and Postgres text (~720 MB) all scale roughly 10x—pushing storage past typical free-tier Postgres limits and making batching/index tuning more important
