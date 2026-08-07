# LITMAP-05 Round 1 Search Log

## Frozen protocol

- Immutable plan: `experiments/plans/LITMAP-05_round1.md`
- Plan commit: `2c4f8bb`
- Search date: 2026-08-07
- Scope: frozen-feature sufficiency / identifiability theory gate
- Prohibited in this round: checkpoint inference, probing, GPU work, training, final
  confirmation access, and any layer/rank/pooling/probe/metric sweep

## Backend preflight

The `research-lookup` backend preflight returned:

```text
parallel-cli: unavailable
PARALLEL_API_KEY: unset
OPENROUTER_API_KEY: unset
```

No paid backend was installed or authenticated. The registered fallback was therefore used:
saved arXiv API, OpenAlex, ar5iv full text, and existing primary-source archives. All raw
discovery responses and decisive full texts are under `sources/`.

## Query-family coverage

The five frozen scientific families were implemented as eleven discovery variants. Expansion
queries refine lexical recall within a registered family; they do not introduce a new scientific
family.

| Frozen family | Saved discovery files | Raw records |
|---|---|---:|
| Formal sufficiency / identifiability | `formal_identifiability_{arxiv,openalex}`, `formal_identifiability_sufficiency_expansion_arxiv`, `formal_identifiability_vinfo_expansion_arxiv` | 231 |
| Frozen vision feature sufficiency | `frozen_sufficiency_{arxiv,openalex}`, `frozen_sufficiency_expansion_arxiv` | 39 |
| Frozen visual interface / downstream decoder | `lvpm_interface_{arxiv,openalex}`, `lvpm_interface_probe_expansion_arxiv` | 134 |
| Rotation / orientation / spatial encoding | `rotation_invariance_{arxiv,openalex}`, `rotation_invariance_probe_expansion_arxiv` | 34 |
| VLM/LVLM probing | `vlm_probe_{arxiv,openalex}`, `vlm_probe_expansion_arxiv` | 115 |
| **Total used by deterministic index** | 16 raw response files | **553** |

`research_litmap05_decisive_arxiv.xml` and
`research_litmap05_exact_formal_titles_arxiv.xml` contain exact-title/version verification
records. They are saved and hashed but are deliberately excluded from discovery counts.

## Deduplication and ranking

`experiments/phase3/build_litmap05_search_index.py` normalizes titles, merges arXiv and
OpenAlex metadata, marks overlap against prior saved searches, and applies the frozen
relevance heuristic.

```text
raw_records: 553
unique_titles: 491
prior_search_duplicates: 58
score_ge_10: 45
```

The deterministic index is
`experiments/results/LITMAP-05_round1/SEARCH_INDEX.tsv`.

Rebuilding the index in a fresh temporary directory produced a byte-identical file:

```text
SHA-256:
2284fa23dfa34ed47030a050f552e7bb36ab22b905f0340d0e239270802e95a4
```

## Decisive primary-source audit

Thirteen primary sources were selected. Twelve new source pairs were saved as
`sources/litmap05_primary_<arxiv-id>.{html,txt}`. Cambrian-1 was not downloaded again:
the already saved and hashed `sources/litmap03_primary_2406_16860.{html,txt}` was reused.

### Formal foundations and probe validity

1. Alain & Bengio, *Understanding intermediate layers using linear classifier probes*,
   ICLR 2017, arXiv:1610.01644.
2. Hewitt & Liang, *Designing and Interpreting Probes with Control Tasks*, EMNLP 2019,
   arXiv:1909.03368.
3. Xu et al., *A Theory of Usable Information Under Computational Constraints*,
   ICLR 2020 talk, arXiv:2002.10689.
4. Voita & Titov, *Information-Theoretic Probing with Minimum Description Length*,
   EMNLP 2020, arXiv:2003.12298.
5. Dubois et al., *Learning Optimal Representations with the Decodable Information
   Bottleneck*, NeurIPS 2020, arXiv:2009.12789.
6. Harvey, Lipshutz & Williams, *What Representational Similarity Measures Imply about
   Decodable Information*, 2024 preprint, arXiv:2411.08197.

### Direct or adjacent VLM/LVLM evidence

7. Rahmanzadehgervi et al., *Vision language models are blind: Failing to translate
   detailed visual features into words*, arXiv:2407.06581.
8. Theodoridis et al., *Probing Visual Concepts in Lightweight Vision-Language Models
   for Automated Driving*, 2026 preprint, arXiv:2603.06054.
9. Kawasaki, Tanaka & Nishida, *Responses Fall Short of Understanding: Revealing the
   Gap between Internal Representations and Responses in Visual Document Understanding*,
   CVPR 2026 MULA workshop, arXiv:2604.04411.
10. Zhao et al., *The First to Know: How Token Distributions Reveal Hidden Knowledge in
    Large Vision-Language Models?*, ECCV 2024, arXiv:2403.09037.
11. Zhang, Yang & Agrawal, *Assessing and Learning Alignment of Unimodal Vision and
    Language Models*, CVPR 2025 Highlight, arXiv:2412.04616.
12. Panos et al., *Imperfect Vision Encoders: Efficient and Robust Tuning for
    Vision-Language Models*, 2024 preprint, arXiv:2407.16526.
13. Tong et al., *Cambrian-1: A Fully Open, Vision-Centric Exploration of Multimodal
    LLMs*, NeurIPS 2024 Oral, arXiv:2406.16860.

For each source, the main text and relevant appendix were checked for the problem setting,
representation location, pooling, readout family, training/regularization, selection, metric,
controls, theorem assumptions, inference boundary, limitations, and local applicability. The
detailed audit is in `EVIDENCE_MATRIX.md`.

## Local read-only interface audit

The local architecture was checked without loading a checkpoint:

- `model/siglip2-base-p32-256-ve/config.json`: `SiglipVisionModel`, 12 layers,
  hidden size 768, image size 256, patch size 32.
- `preprocessor_config.json`: resize to 256×256, bilinear resampling, rescale
  `1/255`, normalize with mean/std `0.5`.
- `MiniMindVLM.get_image_embeddings`: returns `outputs.last_hidden_state`.
- `MiniMindVLM.forward`: passes that token sequence directly through the per-token
  `vision_proj` and inserts 64 projected visual tokens into the language sequence.
- There is no architecture-native rotation head, spatial pooling rule, classifier family,
  regularization rule, or representation-absence test.

Thus architecture uniquely identifies the projector-input tensor but does not uniquely define
a scientific readout from that tensor.

## Resource and safety receipt

- GPU: 0
- Checkpoint inference: 0
- Training: 0
- Final confirmation: not accessed
- Existing failed experiments: not rerun
- New local probe/proxy: not created
