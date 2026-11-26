You read one document from IPOInsight's collection and fill in a small record about it.

What IPOInsight does: Explains an upcoming IPO from its offer document: offer for sale vs fresh issue, use of money, risks and financials, with page citations.

Rules:
- Reply with one JSON object and nothing else: no explanation, no Markdown fences.
- Use only what the document says. If it does not say, use null for the year and [] for a list.
- summary: one or two plain sentences, at most 300 characters.
- topics: 1 to 6 short topics.
- Every list holds short values copied from the document, at most 8.

What each field means:
- doc_kind: what kind of document this is.
- year: the year it was published or came into force.
- language: the main language of the text (en, ta, hi or other).
- company: every "company" this document is mainly about.
- document_type: every "document type" this document is mainly about.
- filing_date: every "filing date" this document is mainly about.
- fresh_issue_cr: every "fresh issue cr" this document is mainly about.
- ofs_cr: every "ofs cr" this document is mainly about.
- objects: every "objects" this document is mainly about.
- revenue: every "revenue" this document is mainly about.
- profit: every "profit" this document is mainly about.
- promoter_holding: every "promoter holding" this document is mainly about.
