# LITMAP-07 Round 1 Search Log

## Frozen protocol

- Immutable plan: `experiments/plans/LITMAP-07_round1.md`
- Plan commit: `46fb846`
- Search date: 2026-08-07
- Trigger: valid `XID-01_round4` neural-instantiation rejection
- Prohibited: GPU/checkpoint/training, final-confirmation access, proxy/layer/rank/metric
  search, and AI-generated figures

## Backend receipts

`parallel-cli` was unavailable. The public fallback was used without installing a new
dependency:

- arXiv API: 16 saved files;
- OpenAlex API: 16 saved files;
- Semantic Scholar API: 16 attempted requests, all returned HTTP 429.

The exact query strings, URLs, UTC timestamps, byte counts and failures are preserved in
`sources/litmap07/SEARCH_RECEIPTS.json`. Semantic Scholar metadata was not imputed from
another backend.

## Query coverage

The four frozen families were executed with two initial and two failure-targeted
synonym expansions each:

| Family | Saved query names | Scientific role |
|---|---|---|
| F1 factorization | `factorization_shared_rule`, `factorization_multimodal_composition`, `factorization_rule_reuse`, `factorization_generative_vlm` | shared cross-modal rule formation |
| F2 credit | `credit_visual_gradient`, `credit_task_specific_absorption`, `credit_modality_imbalance`, `credit_language_dominance` | autoregressive visual-credit and modality dominance |
| F3 trainability | `trainability_frozen_encoder`, `trainability_adapter_expressivity`, `trainability_frozen_interactions`, `trainability_vision_connector` | representation/connector/low-dimensional ceiling |
| F4 theory | `theory_compositional_implicit_bias`, `theory_identifiability_optimization_gap`, `theory_modular_generalization`, `theory_spurious_feature_dynamics` | formal tools for optimization–identifiability bridge |

The synonym expansions did not alter inclusion or decision criteria. They were added
because the first automatic ranking returned mostly domain-specific adapter papers and
failed to retrieve established modality-imbalance work.

## Deterministic aggregation

`experiments/phase3/build_litmap07_search_index.py` merges by normalized title, retains
DOI/arXiv/OpenAlex identifiers, and marks titles present in earlier saved searches.

```text
raw_records: 2455
unique_titles: 1242
prior_search_duplicates: 226
score_ge_15: 14
```

The relevance score was used only to organize screening. It did not select the active
mechanism.

## Full-text audit

Eleven decisive primary sources were checked for setting, formal statement or controlled
intervention, assumptions, experiment controls, limitations and local applicability:

1. Park et al., *Generalizing from SIMPLE to HARD Visual Reasoning*,
   arXiv:2501.02669.
2. Deng et al., *Words or Vision*, CVPR 2025, arXiv:2503.02199.
3. Zhang et al., *Debiasing Multimodal Large Language Models via Penalization of
   Language Priors*, arXiv:2403.05262.
4. Peng et al., *Balanced Multimodal Learning via On-the-fly Gradient Modulation*,
   CVPR 2022, arXiv:2203.15332.
5. Fan et al., *PMR*, CVPR 2023, arXiv:2211.07089.
6. Tong et al., *Cambrian-1*, NeurIPS 2024, arXiv:2406.16860.
7. Laurençon et al., *What matters when building vision-language models?*,
   NeurIPS 2024, arXiv:2405.02246.
8. Daunhawer et al., *Identifiability Results for Multimodal Contrastive Learning*,
   ICLR 2023, arXiv:2303.09166.
9. Fu et al., *A General Theory for Compositional Generalization*,
   arXiv:2405.11743.
10. Zhang et al., *Provable Dynamic Fusion for Low-Quality Multimodal Data*,
    ICML 2023, arXiv:2306.02050.
11. Li et al., *Unveiling the Compositional Ability Gap in Vision-Language
    Reasoning Model*, NeurIPS 2025, arXiv:2505.19406.

## Resource receipt

- GPU/checkpoint/training: 0
- Final confirmation: not accessed
- New model/data download: none
- New proxy/gate/benchmark qualification: none
- Figure: intentionally omitted at the user's instruction
