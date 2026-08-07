# COVER-01 Round 1 Search Log

## Frozen protocol

- Immutable plan: `experiments/plans/COVER-01_round1.md`
- Plan commit: `cc88cd3`
- Search date: 2026-08-07
- Scope: authoritative controlled-coverage literature, official dataset lineage, and
  local feasibility gate
- Prohibited in this round: checkpoint inference, GPU work, training, final confirmation
  access, proxy construction, and domain/mixture/target/metric sweep

## Backend preflight

The `research-lookup` preflight returned:

```text
parallel-cli: unavailable
PARALLEL_API_KEY: unset
OPENROUTER_API_KEY: unset
```

No paid backend was installed or authenticated. The registered fallback was used:
saved arXiv API, OpenAlex, ar5iv full text, and official Hugging Face dataset API/card/tree
responses. All discovery responses and decisive primary-source texts are under `sources/`.

## Query-family coverage

The five frozen scientific families were executed without adding a post-hoc family.
`research_cover01_exact_decisive_arxiv.xml` is an exact-title/version receipt and is not
included in the discovery counts.

| Frozen family | Saved discovery responses | arXiv | OpenAlex | Raw |
|---|---|---:|---:|---:|
| Current ALLaVA / Vision-Flan source lineage | `allava_vflan_{arxiv,openalex}` | 11 | 2 | 13 |
| Direct generative LVLM controlled mixture | `direct_mixture_{arxiv,openalex}` | 9 | 60 | 69 |
| Multimodal diversity / coverage | `diversity_coverage_{arxiv,openalex}` | 60 | 60 | 120 |
| Multimodal mixture optimization | `mixture_optimization_{arxiv,openalex}` | 60 | 60 | 120 |
| Provenance / source schema | `provenance_schema_{arxiv,openalex}` | 60 | 60 | 120 |
| **Total** | 10 discovery responses | **200** | **242** | **442** |

## Deduplication, ranking, and reproducibility

`experiments/phase3/build_cover01_search_index.py` normalizes titles, merges arXiv and
OpenAlex metadata, marks overlap against prior saved searches, and applies the frozen
relevance heuristic:

```text
raw_records: 442
unique_titles: 380
prior_search_duplicates: 69
score_ge_10: 75
```

The deterministic index is
`experiments/results/COVER-01_round1/SEARCH_INDEX.tsv`. Rebuilding it with
`python -m experiments.phase3.build_cover01_search_index` in a fresh temporary directory
and comparing with `cmp` produced a byte-identical file:

```text
SHA-256:
064cfe8d4fb61545fd864bc4da35bc9f2a1bdd2f6dcf9d86bafbf3af26b05cc0
```

## Decisive primary-source audit

Fourteen full texts were checked for model/loss family, data units, source schema,
mixture construction, fixed-budget controls, target selection, seeds/uncertainty,
theorem assumptions/proof object, algorithmic exit, limitations, and local
applicability:

1. Gadre et al., *DataComp: In search of the next generation of multimodal
   datasets*, arXiv:2304.14108.
2. Chen et al., *ALLaVA: Harnessing GPT4V-synthesized Data for A Lite
   Vision-Language Model*, arXiv:2402.11684.
3. Xu et al., *Vision-Flan: Scaling Human-Labeled Tasks in Visual Instruction
   Tuning*, arXiv:2402.11690.
4. Liu et al., *Less is More: Data Value Estimation for Visual Instruction
   Tuning*, arXiv:2403.09559.
5. McKinzie et al., *MM1: Methods, Analysis & Insights from Multimodal LLM
   Pre-training*, arXiv:2403.09611.
6. Lee et al., *Concept-skill Transferability-based Data Selection for Large
   Vision-Language Models*, arXiv:2406.10995.
7. Zhang et al., *MM1.5: Methods, Analysis & Insights from Multimodal LLM
   Fine-tuning*, arXiv:2409.20566.
8. Wu et al., *ICONS: Influence Consensus for Vision-Language Data Selection*,
   arXiv:2501.00654.
9. Kempf et al., *When and How Does CLIP Enable Domain and Compositional
   Generalization?*, arXiv:2502.09507.
10. Shin et al., *What Matters in Data Curation for Multimodal Reasoning? Insights
    from the DCVLR Challenge*, arXiv:2601.10922.
11. Berasi et al., *Linear Model Merging Unlocks Simple and Scalable Multimodal
    Data Mixture Optimization*, arXiv:2602.04937.
12. Qi et al., *DataProphet: Demystifying Supervision Data Generalization in
    Multimodal LLMs*, arXiv:2603.19688.
13. Wen et al., *MixAtlas: Uncertainty-aware Data Mixture Optimization for
    Multimodal LLM Midtraining*, arXiv:2604.14198.
14. Xie et al., *DecoupleMix: Decoupled Ratio Search and Convex Allocation for
    Scalable VLM Data Recipes*, arXiv:2607.24516.

The detailed audit and inference limits are in `EVIDENCE_MATRIX.md`.

## Official source and local-lineage audit

Saved official receipts identify:

- MiniMind dataset revision
  `1e279a8b665cb10383451a6af6fd62b9f35bdd79`;
- upstream ALLaVA revision
  `0fd42fce5c047d387a4bb5318d588eae9a9797f0`;
- the exact local `pretrain_i2t.parquet` LFS object;
- ALLaVA LAION/VFLAN configs, source files, field schemas, cards, and license notes.

`experiments/phase3/audit_cover01_local_lineage.py` read the local parquet without
modification and matched 169 saved official caption rows against local assistant text.
The machine-readable receipt is `LINEAGE_AUDIT.json`; interpretation is in
`DATA_LINEAGE_RECEIPT.md`.

A full upstream metadata download was started outside the repository but stopped after
the LAION transfer projected several hours. No partial file was used as evidence. This did
not cause `INCONCLUSIVE`: the saved official rows already refuted the earlier claim that
lineage was wholly unrecoverable, while the unique single-factor contrast independently
failed on source/task/style/quality confounding and analyst choice.

## Resource and safety receipt

- GPU: 0
- Checkpoint inference: 0
- Training: 0
- Final confirmation: not accessed
- Existing failed experiments: not rerun
- New checkpoint proxy: not created
- Resource preflight: `RESOURCE_PREFLIGHT.json`
- Result status: all required decisive full texts and official receipts were available;
  therefore the decision is not `INCONCLUSIVE`
