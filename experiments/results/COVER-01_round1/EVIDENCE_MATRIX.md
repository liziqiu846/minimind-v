# COVER-01 Evidence and Applicability Matrix

## Gate vocabulary

- `DIRECT_CONTROLLED_COVERAGE`: direct autoregressive/generative VLM evidence that
  also passes source-defined, fixed-budget, unique-contrast, and held-out-target gates.
- `FORMAL_ADJACENT`: controlled or formal evidence for an adjacent model/risk object,
  without a proved bridge to the current autoregressive MiniMind-V risk.
- `SCHEMA_ONLY`: useful authoritative source/task schema, but not a unique causal contrast.
- `HEURISTIC_ONLY`: outcome-, representation-, cluster-, judge-, or search-dependent
  operationalization.
- `REJECT_FOR_BRIDGE`: direct VLM evidence exists, but the exact protocol violates one or
  more immutable bridge gates.

No source below reaches `DIRECT_CONTROLLED_COVERAGE`.

## Compact decision matrix

| ID | Model / risk object | Source-defined coverage? | Unique matched contrast? | Frozen held-out direction? | Formal generative bridge? | Gate |
|---|---|---|---|---|---|---|
| 2304.14108 | CLIP contrastive retrieval/classification | Partial source pool; filtering/embedding selection | No | Evaluation suite fixed, but not source-stratum prediction | No | `FORMAL_ADJACENT` |
| 2402.11684 | Autoregressive ALLaVA | LAION/VFLAN provenance | No; stage, source, caption and task change | No unique target | No | `SCHEMA_ONLY` |
| 2402.11690 | Generative Vision-Flan | 187 publisher-defined tasks | No; task identity/type/difficulty/output change | No unique source target | No | `SCHEMA_ONLY` |
| 2403.09559 | Generative LVLM SFT | No; analyst task grouping | No; selected by gradient/value | Outcome-dependent | No | `HEURISTIC_ONLY` |
| 2403.09611 | Autoregressive MM1 | Broad data types | No; format/source/context change | Benchmark averages | No | `REJECT_FOR_BRIDGE` |
| 2406.10995 | Generative LVLM SFT | No; activation clusters | No; layer/pooling/K/value choices | Cluster loss/benchmarks | No | `HEURISTIC_ONLY` |
| 2409.20566 | Autoregressive MM1.5 | Broad data categories | No; extensive ratios/categories | Benchmark-driven | No | `REJECT_FOR_BRIDGE` |
| 2501.00654 | Generative LVLM SFT | No; target-gradient influence | No | Target validation-dependent | No | `HEURISTIC_ONLY` |
| 2502.09507 | CLIP zero-shot classification | DomainNet domains/classes | Strong adjacent control | Yes for unseen domains/combinations | No autoregressive bridge | `FORMAL_ADJACENT` |
| 2601.10922 | Qwen2.5-VL SFT reasoning | Dataset/challenge sources | No; difficulty/filter/synthetic factors | Known vs challenge-held-out tasks | No | `REJECT_FOR_BRIDGE` |
| 2602.04937 | MLLM SFT mixture ranking | Dataset domains | No; mixture search | Target benchmark outcomes rank mixtures | Local Taylor intuition only | `REJECT_FOR_BRIDGE` |
| 2603.19688 | InternVL3 SFT transfer | Dataset identities | No; perplexity/similarity/clusters | Target-benchmark dependent | No | `HEURISTIC_ONLY` |
| 2604.14198 | Autoregressive MLLM midtraining | Task types only; concepts are CLIP clusters | No; GP-UCB mixture search | Benchmark-targeted | No | `HEURISTIC_ONLY` |
| 2607.24516 | VLM pretraining mixtures | Dataset/capability labels plus judge scores | No; ratio sweep and convex allocation | Evaluation suite, not unique coverage target | No | `REJECT_FOR_BRIDGE` |

## 1. DataComp — arXiv:2304.14108

- **Bibliography/status**: Samir Yitzhak Gadre, Gabriel Ilharco, Alex Fang et al.
  (2023), *DataComp: In search of the next generation of multimodal datasets*,
  NeurIPS 2023 Datasets and Benchmarks / saved arXiv primary version.
- **Model/loss/scale**: CLIP-style dual encoder with contrastive loss. Within each
  registered compute scale, architecture, optimizer/hyperparameters, and samples seen are
  fixed while participants filter a CommonPool or bring data.
- **Data/coverage definition**: Candidate pools are web image-text pairs. Reported
  strategies include language/caption filtering, CLIP similarity, ImageNet-neighbor
  selection using ViT-L/14 embeddings and 100K Faiss groups, and BYOD.
- **Contrast and confounding**: The benchmark cleanly shows that data choice matters under
  fixed compute, but filtering changes quality, source, semantic composition, deduplication,
  and effective coverage together. It does not instantiate baseline + complementary versus
  same-domain redundancy.
- **Target/seeds/uncertainty**: A fixed downstream suite is used, with retrieval and
  zero-shot classification. It is not a single source-defined target stratum tied
  prospectively to a complementary training stratum.
- **Theory/proof object**: No theorem maps source coverage to autoregressive LVLM semantic
  risk.
- **Valid inference**: Fixed-compute CLIP performance is sensitive to data curation.
- **Invalid inference/local gate**: It cannot identify a unique generative-LVLM coverage
  mechanism or local ALLaVA contrast. `FORMAL_ADJACENT`.

## 2. ALLaVA — arXiv:2402.11684

- **Bibliography/status**: Guiming Hardy Chen, Shunian Chen, Ruifei Zhang et al.
  (2024), *ALLaVA: Harnessing GPT4V-synthesized Data for A Lite Vision-Language
  Model*, saved arXiv primary version.
- **Model/loss/scale**: Autoregressive lite LVLM trained with caption alignment and
  instruction tuning; models up to 3B are evaluated on twelve benchmarks.
- **Authoritative schema**: The official data separates LAION web images and
  Vision-Flan-derived images; GPT-4V produces captions and detailed instruction answers.
  IDs, image paths, conversations, captions, and a PPL field are published.
- **Contrast/confounding**: Ablations add caption data and/or instruction data at different
  stages. LAION versus VFLAN also changes acquisition source, natural/document/chart content,
  original task, prompt origin, style, and difficulty. No equal-size complementary versus
  redundancy pair is fixed.
- **Target/seeds/uncertainty**: Aggregate downstream benchmarks; no unique source-defined
  held-out target or directional prediction is frozen.
- **Theory/local gate**: No coverage-to-risk theorem. The paper and card are decisive for
  provenance and source semantics, not for a causal coverage contrast. `SCHEMA_ONLY`.

## 3. Vision-Flan — arXiv:2402.11690

- **Bibliography/status**: Zhiyang Xu, Chao Feng, Rulin Shao et al. (2024),
  *Vision-Flan: Scaling Human-Labeled Tasks in Visual Instruction Tuning*, saved
  arXiv primary version.
- **Model/loss/data**: Generative VLM instruction tuning on 1,664,261 instances from
  187 academic tasks, each with an expert-written instruction; up to 10,000 examples are
  sampled per task.
- **Strongest direct adjacent evidence**: Fixed-total analyses compare 10 or 20 tasks
  against all 187 tasks at 100K/200K examples, and broader task exposure improves evaluated
  capability.
- **Why the contrast is not unique**: Adding tasks changes source dataset, task identity,
  target type, label/output schema, visual domain, difficulty, and task coverage
  simultaneously. Task subsets are not a factorial “same domain, more redundancy” control.
- **Target/seeds/uncertainty**: Benchmark averages and capability analyses, not a unique
  source-defined held-out task selected before choosing the task subset.
- **Theory/local gate**: No formal bridge proves the observed task-diversity effect is a
  coverage term in current autoregressive risk. The 187-task schema is useful for future
  factorial construction, but the published comparisons do not fix one. `SCHEMA_ONLY`.

## 4. TIVE / Less is More — arXiv:2403.09559

- **Bibliography/status**: Zikang Liu, Kun Zhou, Wayne Xin Zhao et al. (2024),
  *Less is More: Data Value Estimation for Visual Instruction Tuning*, saved
  arXiv primary version.
- **Model/object**: Generative visual instruction tuning; task and instance values are
  estimated using gradients and training outcomes.
- **Coverage operationalization**: Vision-Flan tasks are manually consolidated into seven
  groups, then task/instance selection parameters control the subset.
- **Contrast/target**: Selection is explicitly outcome- and gradient-sensitive. It does not
  preserve a publisher-defined coverage factor, and it requires analyst grouping and method
  choices.
- **Theory/local gate**: Useful evidence that redundant instruction data can be removed,
  but no theorem or matched intervention distinguishes complementary coverage from quality
  or transfer value. `HEURISTIC_ONLY`.

## 5. MM1 — arXiv:2403.09611

- **Bibliography/status**: Brandon McKinzie, Zhe Gan, Jean-Philippe Fauconnier et al.
  (2024), *MM1: Methods, Analysis & Insights from Multimodal LLM Pre-training*,
  Apple technical report / saved arXiv primary version.
- **Model/loss/scale**: Fully autoregressive multimodal pretraining, including 200K-step
  fixed-model ablations and larger runs of roughly 100B tokens.
- **Mixture evidence**: Caption, interleaved image-text, and text-only proportions are
  compared under fixed training steps; the paper also records deterministic offline
  mixture snapshots for reproducibility.
- **Why it fails the gate**: The data types change sequence format, source, number/context
  of images, task, caption properties, and text objective together. Several ratios are
  evaluated; the published result is mixture optimization, not a unique
  complementary-versus-redundancy contrast.
- **Target/seeds/theory**: Benchmark averages orient recipe choice. No source-defined
  held-out stratum or coverage-to-autoregressive-risk theorem is supplied.
- **Local gate**: Direct generative evidence, but violates unique/no-sweep and
  single-factor requirements. `REJECT_FOR_BRIDGE`.

## 6. COINCIDE — arXiv:2406.10995

- **Bibliography/status**: Jaewoo Lee, Boyang Li, and Sung Ju Hwang (2024),
  *Concept-skill Transferability-based Data Selection for Large Vision-Language
  Models*, saved arXiv primary version.
- **Model/object**: A small LVLM provides internal activations used to cluster visual
  instruction data; density and cross-cluster transferability allocate samples.
- **Operational choices**: The method observes that the best layer varies and deliberately
  concatenates five chosen layers. It additionally chooses pooling/features, clustering,
  \(K\), density, and transfer proxies.
- **Contrast/target**: Same-number cluster-transfer experiments are informative, but the
  clusters and their scientific meaning are representation-derived rather than
  authoritative source strata.
- **Theory/local gate**: The method is a useful selection algorithm, not a source-defined
  coverage identification result. It directly violates the immutable ban on
  layer/embedding/cluster-defined coverage. `HEURISTIC_ONLY`.

## 7. MM1.5 — arXiv:2409.20566

- **Bibliography/status**: Haotian Zhang, Mingfei Gao, Zhe Gan et al. (2024),
  *MM1.5: Methods, Analysis & Insights from Multimodal LLM Fine-tuning*, Apple
  technical report / saved arXiv primary version.
- **Model/loss/scale**: Autoregressive MLLMs from 1B to 30B; 200K pretraining,
  30K continual-pretraining, and 23K SFT steps under specified recipes.
- **Mixture evidence**: OCR, captions, interleaved data, text, general-domain,
  text-rich, grounding, UI, and video categories are extensively ablated.
- **Why it fails the gate**: Ratios and categories are chosen through broad benchmark
  comparisons. Adding a category also changes task, source, style, resolution/image-token
  structure, and target capability.
- **Target/seeds/theory**: No unique source-defined target tied to a single complementary
  stratum and no formal generative coverage theorem.
- **Local gate**: Strong direct recipe evidence, but not a no-sweep single-factor
  specification. `REJECT_FOR_BRIDGE`.

## 8. ICONS — arXiv:2501.00654

- **Bibliography/status**: Xindi Wu, Mengzhou Xia, Rulin Shao et al. (2025),
  *ICONS: Influence Consensus for Vision-Language Data Selection*, saved arXiv
  primary version.
- **Model/object**: Visual-instruction examples/tasks are ranked using target validation
  gradients and cross-task influence consensus.
- **Coverage/contrast**: Dataset identity is retained, but admission is defined by
  downstream target influence rather than an outcome-independent source coverage schema.
- **Target selection**: The intended target supplies gradients, so the train subset cannot
  support the frozen-target/no-target-feedback gate.
- **Theory/local gate**: Evidence supports task influence as a selection signal, not a
  source-defined complementary-coverage mechanism. `HEURISTIC_ONLY`.

## 9. CLIP domain/compositional generalization — arXiv:2502.09507

- **Bibliography/status**: Elias Kempf, Simon Schrodi, Max Argus, and Thomas Brox
  (2025), *When and How Does CLIP Enable Domain and Compositional
  Generalization?*, saved arXiv primary version.
- **Model/loss/data**: CLIP contrastive training and zero-shot classification on
  source-defined DomainNet domains and classes.
- **Controlled evidence**: For a given test domain, high- and low-diversity mixtures have
  comparable sizes and class distributions; architecture/training are fixed. Three seeds
  and consecutive epochs are reported. Targets are unseen domains or class-domain
  combinations.
- **Remaining choices/confounds**: The class subset includes random sampling plus manual
  rejection to cover super-categories. Some DomainNet domains differ strongly in size, and
  the study fixes sizes within rather than across test domains.
- **Theory/proof object**: Mechanistic representation/circuit analyses explain CLIP
  behavior, but there is no theorem transporting the result to autoregressive token loss
  and generative semantic risk.
- **Valid inference**: This is the cleanest audited causal evidence that source/domain
  diversity affects CLIP domain and compositional generalization.
- **Invalid inference/local gate**: CLIP-only evidence cannot authorize a MiniMind-V
  generative training experiment without a new bridge. `FORMAL_ADJACENT`.

## 10. DCVLR curation — arXiv:2601.10922

- **Bibliography/status**: Yosub Shin, Michael Buriek, Boris Sobolev et al. (2026),
  *What Matters in Data Curation for Multimodal Reasoning? Insights from the DCVLR
  Challenge*, preprint analyzing the NeurIPS 2025 challenge.
- **Model/design**: Up to 10,000 examples fine-tune a fixed Qwen2.5-VL model under a
  shared recipe; known-in-advance and challenge-held-out reasoning tasks are evaluated.
- **Evidence**: Difficulty selection on an aligned base dominates; simply increasing
  size mostly changes variance, while tested diversity/synthetic heuristics add little or
  hurt in this saturation regime.
- **Why it fails the gate**: Diversity uses category/cluster/synthetic constructions and is
  subordinate to difficulty filtering. Source, difficulty, synthetic generation, and
  alignment are not orthogonalized into the registered complementary/redundancy pair.
- **Uncertainty/theory/local gate**: Default challenge results are not a three-seed causal
  coverage test; only selected ablations repeat seeds. No coverage-to-risk theorem.
  `REJECT_FOR_BRIDGE`.

## 11. Linear model-merging DMO — arXiv:2602.04937

- **Bibliography/status**: Davide Berasi, Matteo Farina, Massimiliano Mancini, and
  Elisa Ricci (2026), *Linear Model Merging Unlocks Simple and Scalable Multimodal
  Data Mixture Optimization*, saved arXiv primary version.
- **Model/design**: Qwen2-VL/InternVL variants, LoRA/full fine-tuning, 2–4 domains, and
  10K/50K/100K budgets. Domain experts are merged to rank mixtures.
- **Mixture protocol**: Twenty candidate mixtures are sampled from a uniform Dirichlet
  construction and evaluated against downstream benchmark outcomes.
- **Theory/proof idea**: A second-order Taylor approximation under local convexity/linear
  mode connectivity motivates expert-weight combinations. It is explicitly a local
  intuition for ranking mixtures, not a theorem that source coverage determines
  autoregressive held-out risk.
- **Why it fails the gate**: It searches mixtures and target outcomes; the merged model is
  a ranking proxy. No unique complementary/redundancy/target specification follows.
  `REJECT_FOR_BRIDGE`.

## 12. DataProphet — arXiv:2603.19688

- **Bibliography/status**: Xuan Qi, Luxi He, Dan Roth, and Xingyu Fu (2026),
  *DataProphet: Demystifying Supervision Data Generalization in Multimodal LLMs*,
  saved arXiv primary version.
- **Model/design**: Direct generative InternVL3 cross-dataset transfer under fixed
  20K-example compute for influence analysis; 14 source/target datasets across seven
  broad tasks.
- **Selection object**: Multimodal perplexity, embedding similarity, and k-means diversity
  predict target-specific transfer, followed by target-oriented data selection.
- **Evidence boundary**: Dataset-level transfer asymmetry is important and broad task
  similarity is insufficient. However, the operational signal is a compound heuristic and
  depends on the target benchmark.
- **Theory/local gate**: No authoritative source-stratum factorial contrast or formal
  coverage bridge; directly prohibited embeddings/clusters/proxy selection are essential.
  `HEURISTIC_ONLY`.

## 13. MixAtlas — arXiv:2604.14198

- **Bibliography/status**: Bingbing Wen, Sirajul Salekin, Feiyang Kang et al. (2026),
  *MixAtlas: Uncertainty-aware Data Mixture Optimization for Multimodal LLM
  Midtraining*, saved May 2026 arXiv primary version.
- **Model/loss/design**: Autoregressive token-loss midtraining. Five task-supervision axes
  and ten image-concept axes are optimized using Qwen2-0.5B proxy runs; recipes transfer
  to 7B models.
- **Coverage definition**: Task labels are interpretable, but image concepts are CLIP
  k-means clusters with post-hoc human names.
- **Search/target**: GP-UCB searches 50 task-mixture or 200 concept-mixture proxy runs
  against a ten-benchmark objective. It is explicitly benchmark-targeted.
- **Theory/local gate**: Fixed compute makes the engineering comparison useful, but
  cluster construction, proxy optimization, and target sweep violate source-defined and
  no-sweep gates. `HEURISTIC_ONLY`.

## 14. DecoupleMix — arXiv:2607.24516

- **Bibliography/status**: Jiahao Xie, Zhongbin Guo, Qianle Wang et al. (2026),
  *DecoupleMix: Decoupled Ratio Search and Convex Allocation for Scalable VLM Data
  Recipes*, saved August 2026 arXiv primary version.
- **Model/design**: VLM pretraining recipe construction at 2.5B, 5B, and 10B tokens,
  with a reported transfer to a 32B model.
- **Mixture protocol**: Inter-class capability ratios use single-variable iterative
  search. Intra-class allocation scores each dataset for quality and difficulty using an
  LLM judge and solves a constrained convex diversity objective.
- **Strong adjacent feature**: A new dataset can be admitted or rejected under a frozen
  recipe, providing an attributable engineering admission protocol.
- **Why it fails the gate**: Broad categories and judge scores are not an authoritative
  factorial coverage variable; inter-class ratios are searched, and intra-class allocation
  depends on the chosen weights/objective. The proxy scale alone exceeds the local minimal
  design.
- **Theory/local gate**: No formal source-coverage-to-held-out-risk result and no unique
  complementary/redundancy target. `REJECT_FOR_BRIDGE`.

## Cross-source synthesis

The literature establishes three narrower facts:

1. data composition materially affects fixed-compute CLIP and generative VLM performance;
2. task/domain diversity can improve held-out behavior in some controlled settings;
3. transfer is asymmetric and is entangled with difficulty, quality, task objective,
   source format, and target choice.

It does **not** supply the conjunction required by the immutable gate:

\[
\text{authoritative source strata}
\land
\text{unique single-factor complementary/redundancy contrast}
\land
\text{frozen generative held-out target}
\land
\text{autoregressive LVLM risk bridge}.
\]

Consequently, the exact audited bridge is rejected. The upper-level claim that
coverage/diversity may affect VLM generalization remains open.
