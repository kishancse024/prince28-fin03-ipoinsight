# Dataset: IPOInsight

Explains an upcoming IPO from its offer document: offer for sale vs fresh issue, use of money, risks and financials, with page citations.

- **Start target:** 10 offer documents (about 4,000 pages)
- **Full target:** 40+ offer documents + ICDR Regulations (15,000+ pages)
- **Collected by:** `scripts/fetch.py` as `examate-student-bot` (https://github.com/kishancse024/prince28-fin03-ipoinsight): robots.txt respected, at most 4 requests at once, 0.5 s between requests to one site.

## Where the documents come from

- https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=3&ssid=15&smid=10
- https://www.sebi.gov.in/

## Terms I follow

Public SEBI filings. Cite page numbers.

- Every answer links to the original document.
- No personal data is collected.

<!-- generated:start -->
## Sources (generated 2026-11-24 04:33 UTC by scripts/dataset_report.py)

| Source | Licence / terms | Files | MB | Pages* | How | Fetched | Example URL |
|---|---|---|---|---|---|---|---|
| bofa-com | Public SEBI filing | 1 | 10.7 | 532 | http | 2026-11-24 | https://business.bofa.com/content/dam/flagship/in/en/investment-banking/Swiggy-Limited-DRHP.pdf |
| bseindia-com | Public SEBI filing | 1 | 11.1 | 505 | http | 2026-11-24 | https://www.bseindia.com/corporates/download/358332/DRHP_20221010162344.pdf |
| sebi-gov-in | Public SEBI filing | 6 | 56.6 | 2,323 | http | 2026-11-24 | https://www.sebi.gov.in/sebi_data/commondocs/sep-2026/Maharashtra%20Oil%20Extractions%20Limited%20-%20DAP_p.pdf |

**Total:** 8 files, 78.3 MB, 3,360 pages. Not downloaded: 0 blocked by robots.txt, 0 failed.

*Pages = PDF pages, plus one page per 3,000 characters of text or HTML.

## Files (first 8 of 8)

The complete list, with a sha256 fingerprint of every file, is `data/manifest.jsonl`.

| # | Title / file | Source | Pages | Fetched | URL |
|---|---|---|---|---|---|
| 1 | Swiggy Limited - DRHP (Sep 26, 2024) | bofa-com | 532 | 2026-11-24 | https://business.bofa.com/content/dam/flagship/in/en/investment-banking/Swiggy-Limited-DRHP.pdf |
| 2 | IKIO Lighting Limited - DRHP (Sep 29, 2022) | bseindia-com | 505 | 2026-11-24 | https://www.bseindia.com/corporates/download/358332/DRHP_20221010162344.pdf |
| 3 | Aether Industries Limited - Prospectus (May 27, 2022) | sebi-gov-in | 399 | 2026-11-24 | https://www.sebi.gov.in/sebi_data/attachdocs/may-2022/1653979110197.pdf |
| 4 | Tata Technologies Limited - DRHP (Mar 9, 2023) | sebi-gov-in | 480 | 2026-11-24 | https://www.sebi.gov.in/sebi_data/attachdocs/mar-2023/1678708849713_63.pdf |
| 5 | Hyundai Motor India Limited - Prospectus | sebi-gov-in | 476 | 2026-11-24 | https://www.sebi.gov.in/sebi_data/attachdocs/oct-2024/1729225003827.pdf |
| 6 | Iris Global Services Limited - DRHP (Sep 21, 2026) | sebi-gov-in | 444 | 2026-11-24 | https://www.sebi.gov.in/sebi_data/attachdocs/sep-2026/1790743844411.pdf |
| 7 | Sarva Foam Industries Limited - DRHP (Sep 30, 2026) | sebi-gov-in | 511 | 2026-11-24 | https://www.sebi.gov.in/sebi_data/attachdocs/oct-2026/1791286434593.pdf |
| 8 | Maharashtra Oil Extractions Limited - DAP (Sep 13, 2026) | sebi-gov-in | 13 | 2026-11-24 | https://www.sebi.gov.in/sebi_data/commondocs/sep-2026/Maharashtra%20Oil%20Extractions%20Limited%20-%20DAP_p.pdf |
<!-- generated:end -->

## Known gaps

- 2 additional offer documents are required to reach the initial target of 10.
- Current collection: 8 documents covering 3,360 pages.
- Target: 10 documents covering approximately 4,000 pages.
- ICDR Regulations and additional offer documents are pending for the full target of 40+ documents and 15,000+ pages.


## Duplicate Detection

Documents were checked using SHA-256 hashes.

- Total documents checked: 10
- Duplicate groups: 0
- Extra downloads: 0
- Detection method: SHA-256 hash comparison across downloaded URLs.

No duplicate files were found.
