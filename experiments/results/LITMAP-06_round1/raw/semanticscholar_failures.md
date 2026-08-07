# Semantic Scholar search receipts

Date: 2026-08-07

The unauthenticated Semantic Scholar Graph API returned HTTP 429 after retries for:

- `ar_credit_gradient`
- `composition_theory`
- `coverage`
- `coverage_diversity`

The `ar_credit` and `composition` requests completed and their JSON responses are preserved in
`sources/litmap06/`. The failed families remain covered by arXiv and OpenAlex discovery; no
result count or absence claim is inferred from the Semantic Scholar failures.
