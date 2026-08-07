# LITMAP-06 Round 1 Evidence Matrix

## Epistemic boundary

This matrix compares candidate scientific mechanisms. It does not treat a benchmark,
proxy, gate, graph statistic, or implementation as the mechanism itself. Unless a row
explicitly cites a formal theorem, its evidence is empirical. The selected mechanism is
at most a `CONJECTURE`.

## Decisive primary sources

| Source | Setting and strongest usable evidence | Formal object / assumptions | What it does not establish | Mechanism implication |
|---|---|---|---|---|
| Deng et al., *Words or Vision: Do Vision-Language Models Have Blind Faith in Text?*, CVPR 2025, arXiv:2503.02199 | Ten VLMs under conflicting image/text evidence; text relevance, order and model scale alter text bias. Matched-size text augmentation reduces bias. | Theorem A.5 bounds multimodal risk for ERM on a pure-text / multimodal mixture under bounded Lipschitz loss and Transformer norm/covering assumptions; the extra term scales as \(N/(N+M)\varepsilon_{\rm cross}\). | It does not model multimodal examples whose target is already predictable from their own language context, nor identify the true interaction rule on unseen image–text combinations. | Strong empirical support for AR visual-credit competition; adjacent but incomplete theory. |
| Fan et al., *PMR: Prototypical Modal Rebalance for Multimodal Learning*, CVPR 2023, arXiv:2211.07089 | Audio-visual and classification experiments show a stronger modality can dominate the fused objective and suppress the weaker one; gradient directions diverge. | No autoregressive generative-risk theorem; prototypes and entropy regularization are method-specific. | It does not cover discrete next-token targets, language shortcuts inside multimodal examples, or held-out cross-modal compositions. | Supports modality competition as a training phenomenon, not the desired LVLM generalization mechanism by itself. |
| Li et al., *Multi-modal Preference Alignment Remedies Degradation of Visual Instruction Tuning on Language Models*, ACL 2024 | VQA instruction tuning can degrade text instruction following; a 6k preference set and DPO improve both text and visual benchmarks. | Empirical alignment study; data, objective and supervision change together. | It cannot isolate interaction-rule identification from catastrophic forgetting, preference quality, or ordinary transfer. | Counterevidence to a one-way “more visual credit always helps” story; objectives can alter both modalities. |
| Li et al., *Unveiling the Compositional Ability Gap in Vision-Language Reasoning Model*, NeurIPS 2025, arXiv:2505.19406 | ComPABench isolates textual/multimodal skills and evaluates cross-modal, cross-task and OOD composition. Individual skills can approach ceiling while multimodal composition remains very low; RL-Ground improves but does not close the gap. | Controlled synthetic geometry/spatial tasks; component ablations. No general theorem and no clear multi-seed uncertainty. | Caption-before-thinking plus progress reward is multi-factor and does not identify which training-support property makes a cross-modal rule learnable. | Strongest direct empirical support that marginal/individual skill exposure does not identify the composition used at test time. |
| Fu et al., *A General Theory for Compositional Generalization*, arXiv:2405.11743 | Definition 3.1 uses disjoint concept supports and a measure-preserving bijective composition rule. Theorem 4.5 gives a CG no-free-lunch result; Theorem 5.4 separates IID and CG terms; Section 6 leaves “generative effects” as a future challenge. | Task-agnostic CG distributions; formal composition-rule random variable and conditional information term. | Assumptions do not directly match natural images, overlapping language concepts, or autoregressive conditional targets. Its information term is not a local proxy. | Useful `THEORY_TOOL`: any positive result needs task-specific assumptions that restrict the interaction-rule equivalence class. |
| Daunhawer et al., *Identifiability Results for Multimodal Contrastive Learning*, ICLR 2023, arXiv:2303.09166 | Theorem 1 block-identifies invariant content factors under a continuous invertible generative process, content invariance, style perturbations and an asymptotic contrastive objective. | Known/estimable content dimension; continuous latents; shared invariant content and modality-specific/style factors. | It certifies representation block-identifiability, not a discrete autoregressive conditional predictor or unseen-cell semantic risk. | Demonstrates that “identifiability” can be formal, while exposing exactly which assumptions are missing for LVLM next-token learning. |
| Jing et al., *In-Context Compositional Generalization for Large Vision-Language Models*, EMNLP 2024 | GQA-ICCG selects demonstrations using content/structure coverage, diversity and visual redundancy; visual/language asymmetry matters. | In-context retrieval/method study on GQA. | It does not prove a training generalization law and the selection score is not a mechanism. | Supports the role of cross-modal structural coverage but cannot serve as the formal object. |
| Li et al., *Multi-Sourced Compositional Generalization in Visual Question Answering*, IJCAI 2024, arXiv:2505.23045 | GQA-MSCG separates linguistic–linguistic, visual–visual and linguistic–visual novel compositions; retrieval-alignment improves results. | Dataset construction and method study; target-specific retrieval and alignment choices. | Co-occurrence difficulty and method search do not identify an autoregressive interaction rule or yield a general theorem. | Supports genuinely multi-sourced composition while warning against turning a retrieval score into the mechanism. |
| Wiedemer et al., *Pretraining Frequency Predicts Compositional Generalization of CLIP on Real-World Tasks*, arXiv:2502.18326 | On CLIP retrieval, performance for unseen object combinations is predicted by constituent-object pretraining frequency. | Corpus filtering and retrieval prediction for tangible object combinations. | It does not cover attribute/relation binding, generative LVLMs or interactions whose whole is not recoverable from the parts. | Important limiting case: joint-cell exposure is not always necessary when marginal factors are sufficiently identifiable and recomposable. |
| Kempf et al., *When and How Does CLIP Enable Domain and Compositional Generalization?*, ICML 2025, arXiv:2502.09507 | Fixed architecture/training and matched class distributions over controlled DomainNet mixtures, three seeds and consecutive epochs. Domain diversity improves generalization; partial exposure to a test domain can be worse than no exposure, while non-overlapping classes can help. | Empirical CLIP contrastive classification; circuit/CKA analysis is explanatory evidence, not a theorem. | It does not establish an autoregressive LVLM bound and is far beyond local replication budget. | Strong support that support arrangement, not just \(N\) or marginal diversity, can change generalization direction. |

## Candidate expected-value comparison

Scores are qualitative consequences of the frozen criteria, not a new metric or gate.

| Candidate mechanism | VLM novelty | Literature gap | Explains local failures without reviving them | New falsifiable prediction | Candidate theory object | Local feasibility | Algorithmic exit | Decision |
|---|---|---|---|---|---|---|---|---|
| AR visual-credit competition | High: image and language can explain the same target | Direct empirical evidence; closest theorem only covers pure-text/multimodal mixture ratio | Explains negative no-pixel proxy and failed “must-look” instruction as operationalization failures, but alone does not explain composition/coverage results | Holding pixels fixed, reducing language-only target predictability should increase transferable visual dependence | Credit/gradient or conditional-risk competition, still underspecified | A clean control would likely require new training and a new target construction | Visual-dependency weighting or balanced objectives | `NEXT`; strong phenomenon but weaker unifying formal object |
| Cross-modal compositional factorization | High: visual entities/relations must combine with language/reasoning skills | Strong controlled evidence; general CG theory leaves task-specific generative effects open | Directly explains why What’sUp NLL was language dominated, but risks looking like `COMP-01` renamed | Seen component skills can remain high while unseen cross-modal composition changes under support interventions | Composition rule and task-specific factorization assumptions | Symbolic/toy theory is cheap; realistic local panel remains difficult | Factorized intermediate supervision or composition-aware training | `NEXT`; central symptom, but not yet the learning-theoretic cause |
| Joint multimodal support coverage | High: joint image × concept × relation × realization × domain support | Strong CLIP evidence; no direct generative theorem | Explains why broad labels and authoritative-cell gates failed: labels are tools, not the relevant support property | Matched \(N\) and marginals but different support connectivity should alter unseen-cell risk | Support geometry / connectivity, currently too many possible statistics | Exact local factorial data are not available; constructing it risks another schema gate | Coverage-aware sampling or targeted generation | `BACKLOG`; important data-side condition, not sufficiently specific alone |
| **Cross-modal interaction identifiability under autoregressive supervision** | **High: the same next-token target admits language-only and image–language interaction explanations** | **No audited theorem covers observed-support equivalence of discrete AR predictors and their divergence on unseen multimodal cells** | **Unifies all three streams while respecting that `COMP-01`/`VISCOND-01` proxies and `VISSUP-01`/`PROJALLOC-01` interventions—not their parent mechanisms—failed** | **With matched factor marginals, target format and sample count, adding support cells that distinguish a shortcut rule from the intended interaction rule should reduce unseen-combination risk; redundant cells should not** | **Equivalence class of low-risk conditional predictors on observed support; target-support diameter / rule-identification error** | **A finite crossed-support proposition and exhaustive toy verification require no checkpoint or training; later local training can be paired and single-factor** | **Interaction-identifying sampling, counterfactual cells, or objectives that discriminate observationally equivalent rules** | **`ACTIVE`; highest scientific expected value** |

## Why the selected mechanism is not a renamed failed route

- `COMP-01` asked whether one frozen caption-NLL margin measured relation binding.
  `XID-01` asks whether the training distribution and objective identify a conditional
  interaction rule at all. It can be studied without that margin or benchmark.
- `VISCOND-01` asked whether correct-image versus no-pixel answer-letter margin measured
  visual use. `XID-01` does not infer rule identification from input ablation.
- `VISSUP-01` changed a rotation instruction but did not create a crossed support in which
  two candidate interaction rules make different observed predictions. Its null result
  therefore rejects that operationalization, not `XID-01`.
- `CROSSFACT-01` sought an authoritative dataset schema. Under `XID-01`, crossed cells are
  one possible experiment tool; the scientific object is the equivalence class of
  conditional rules, not whether a publisher supplied a table.

## Conceptual synthesis

```text
text/visual-credit evidence ─┐
composition-gap evidence ────┼─> multiple AR interaction rules fit observed support
joint-support evidence ───────┘                  │
                                                ├─ formalize predictor equivalence
                                                ├─ prove rule-identification term
                                                ├─ predict unseen-cell divergence
                                                └─ derive interaction-identifying data/objectives
```

The requested AI-generated schematic could not be produced after two attempts because
the image-generation backend returned a network error. This deterministic conceptual
map is a documented fallback and is not represented as an AI-reviewed figure or as
scientific evidence.
