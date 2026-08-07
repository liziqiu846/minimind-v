# LITMAP-06 Round 1 Search Log

## Frozen protocol

- Immutable plan: `experiments/plans/LITMAP-06_round1.md`
- Plan commit: `1c63dbf`
- Search date: 2026-08-07
- Scope: failure-informed reselection among scientific mechanisms
- Prohibited: checkpoint inference, GPU work, training, final confirmation access,
  post-hoc proxy construction, and benchmark/schema qualification as the main question

## Backend preflight and limitations

`parallel-cli`, `PARALLEL_API_KEY`, and `OPENROUTER_API_KEY` were unavailable. The
predeclared public fallback was used:

- arXiv API: 24 saved files, 1,101 records;
- OpenAlex API: 22 saved files, 2,178 records;
- Semantic Scholar API: 2 successful files, 200 records.

Semantic Scholar returned HTTP 429 for additional requests; exact failures are preserved
in `raw/semanticscholar_failures.md`. No citation count, venue, DOI, or full-text claim was
invented to fill missing metadata.

The literature-review skill also requires an AI-generated synthesis figure. Two
generation attempts were made after preflight and both failed with a network error from
the image-generation backend. `EVIDENCE_MATRIX.md` contains a clearly labelled
deterministic text fallback; it is not claimed to be AI-generated or quality-reviewed.

## Query-family coverage

The three frozen search starts and a failure-informed fourth family were executed:

| Family | Scientific question | arXiv records | OpenAlex records | Semantic Scholar records |
|---|---|---:|---:|---:|
| `ar_credit_*` | Why can AR multimodal loss fall without transferable visual dependence? | 300 | 600 | 100 |
| `composition_*` | What explains cross-modal composition beyond marginal exposure? | 300 | 600 | 100 |
| `coverage_*` | Does joint support arrangement matter beyond \(N\) and marginals? | 300 | 600 | 0 |
| `xid_*` | Is there an adjacent interaction/conditional identifiability theorem? | 200 | 378 | 0 |
| exact receipts | Exact-title/version retrieval, not discovery | 1 | 0 | 0 |
| **Total** |  | **1,101** | **2,178** | **200** |

The fourth family was permitted by the immutable plan because the first three streams
converged on a stronger scientific mechanism. It did not add a post-hoc selection
criterion.

## Deduplication and reproducibility

`experiments/phase3/build_litmap06_search_index.py` normalizes titles, merges metadata,
marks overlap against prior saved searches, and applies the predeclared relevance
heuristic.

```text
raw_records: 3479
unique_titles: 2395
prior_search_duplicates: 369
score_ge_10: 98
```

A fresh rebuild was byte-identical to the saved index:

```text
SEARCH_INDEX.tsv SHA-256:
bf85b2dfdcd30008d8c8d461b50d940082be0a293950c3fe435b0b6d9dc930c0
```

## Full-text screening

Ten decisive primary sources were checked for problem setting, model/loss family,
controlled variables, uncertainty/seeds, formal statement, assumptions, proof object,
limitations, local applicability and algorithmic implications:

1. Deng et al., *Words or Vision*, CVPR 2025.
2. Fan et al., *PMR*, CVPR 2023.
3. Li et al., *Multi-modal Preference Alignment*, ACL 2024.
4. Li et al., *Unveiling the Compositional Ability Gap*, NeurIPS 2025.
5. Fu et al., *A General Theory for Compositional Generalization*, arXiv:2405.11743.
6. Daunhawer et al., *Identifiability Results for Multimodal Contrastive Learning*,
   ICLR 2023.
7. Jing et al., *In-Context Compositional Generalization*, EMNLP 2024.
8. Li et al., *Multi-Sourced Compositional Generalization in VQA*, IJCAI 2024.
9. Wiedemer et al., *Pretraining Frequency Predicts Compositional Generalization of
   CLIP*, arXiv:2502.18326.
10. Kempf et al., *When and How Does CLIP Enable Domain and Compositional
    Generalization?*, ICML 2025.

The exact evidence and inference limits are in `EVIDENCE_MATRIX.md`.

## Citation verification

Peer-reviewed DOI-bearing sources were verified through the DOI handle service and
Crossref using the literature-review citation checker. Sources without a DOI were
verified against arXiv metadata and official conference proceedings/OpenReview/PMLR
metadata and are not falsely assigned a DOI. Machine-readable output is in
`CITATIONS_citation_report.json`.

## Resource receipt

- GPU / checkpoint / training: 0
- Final confirmation: not accessed
- Large dataset or checkpoint download: none
- Existing failed experiments: not rerun
- New metric/proxy/gate: none
