# LITMAP-05 Evidence and Applicability Matrix

## Gate question

Can formal theory plus the local architecture uniquely specify a no-sweep readout of the
actual frozen visual output, with valid asymmetric inference about
`representation-absent` versus `downstream-unabsorbed`?

The answer below is intentionally about the bridge, not about whether frozen visual
representations contain useful information in general.

## Formal foundations and probe-validity sources

### 1. Alain & Bengio (2017), arXiv:1610.01644

- **Source/status**: Guillaume Alain and Yoshua Bengio, *Understanding intermediate
  layers using linear classifier probes*, ICLR 2017.
- **Setting/object**: Inception-v3 and ResNet-50 intermediate activations; a separate
  softmax linear classifier is fit at each inspected layer.
- **Location/pooling/readout**: Layer is chosen by the analyst. Large convolutional
  activations require pooling or dimensionality reduction; the appendix uses random feature
  subsets and explicitly notes unequal advantages across layers.
- **Theory/assumptions/proof**: Convexity of softmax linear-probe fitting supports an
  optimization diagnostic, not completeness of the readout class. There is no theorem that
  selects a layer, pooling, task label, or proves that a failed probe implies signal absence.
- **Controls/external evidence**: Frozen models and held-out classification error make
  probes non-invasive diagnostics. Multiple layers are intentionally inspected.
- **Valid inference**: A successful selected probe demonstrates linear decodability at that
  selected location and preprocessing.
- **Invalid inference**: A failed finite linear probe does not establish information absence
  or downstream impossibility.
- **Local applicability/gate**: General diagnostic motivation only. MiniMind-V would still
  require token aggregation and a task-specific classifier. `FORMAL_ADJACENT`.

### 2. Hewitt & Liang (2019), arXiv:1909.03368

- **Source/status**: John Hewitt and Percy Liang, *Designing and Interpreting Probes with
  Control Tasks*, EMNLP 2019.
- **Setting/object**: Linguistic properties in frozen ELMo representations; linguistic tasks
  are paired with random control tasks.
- **Location/pooling/readout**: Probe architecture, layer, capacity, dropout and other
  regularization are analyst choices. The paper shows that probe accuracy alone confounds
  representation information with probe memorization.
- **Theory/assumptions/proof**: Selectivity is the difference between linguistic-task and
  control-task behavior. It controls one competing explanation—probe memorization—but does
  not provide a complete decoder or a unique probe family.
- **Controls/external evidence**: Control tasks and regularization comparisons show that
  MLP expressivity and hyperparameters materially change interpretation; even which ELMo
  layer is “better” depends on accuracy versus selectivity.
- **Valid inference**: Control tasks can weaken a memorization explanation for a selected
  probe.
- **Invalid inference**: High accuracy is not automatically representation evidence, and
  low accuracy is not information absence.
- **Local applicability/gate**: Strengthens the no-post-hoc-selection constraint; it does not
  specify a MiniMind-V rotation readout. `FORMAL_ADJACENT`.

### 3. Xu et al. (2020), arXiv:2002.10689

- **Source/status**: Yilun Xu, Shengjia Zhao, Jiaming Song, Russell Stewart and Stefano
  Ermon, *A Theory of Usable Information Under Computational Constraints*, ICLR 2020
  talk.
- **Setting/object**: Predictive \(\mathcal V\)-information for arbitrary random variables.
  Definition 1 requires a predictive family \(\mathcal V\) satisfying optional ignorance;
  Definitions 2–3 define \(\mathcal V\)-entropy/information relative to that family.
- **Readout/selection**: \(\mathcal V\) is supplied by the analyst to encode computational
  or statistical constraints. Examples include Gaussian linear predictors, PixelCNN++, and
  other chosen model classes.
- **Theory/assumptions/proof**: Theorem 1 gives PAC estimation bounds using bounded
  log-likelihood and Rademacher complexity of the already chosen family. The proof uses
  McDiarmid/symmetrization arguments; it certifies estimation of
  \(I_{\mathcal V}\), not selection or completeness of \(\mathcal V\).
- **Valid inference**: For a fixed declared family and assumptions, positive
  \(\mathcal V\)-information establishes predictability available to that family.
- **Invalid inference**: The theorem does not make a linear family architecture-native and
  does not let a negative finite estimate prove that no other decoder can recover the signal.
- **Local applicability/gate**: No unique MiniMind-V \(\mathcal V\), pooling, regularization
  or rotation statistic follows. `FORMAL_ADJACENT`.

### 4. Voita & Titov (2020), arXiv:2003.12298

- **Source/status**: Elena Voita and Ivan Titov, *Information-Theoretic Probing with
  Minimum Description Length*, EMNLP 2020.
- **Setting/object**: Frozen ELMo/BERT linguistic representations; MDL replaces bare probe
  accuracy with label codelength.
- **Location/pooling/readout**: Experiments choose representation layer, a projection plus
  self-attention span-pooling architecture, a two-layer MLP, optimizer, dropout, online
  transmission blocks or a variational code.
- **Theory/assumptions/proof**: Online and variational coding account for data/model effort
  and improve comparisons with random/control representations. They do not prove that the
  selected classifier pipeline exhausts all signal in the representation.
- **Controls/external evidence**: Trained versus random encoders, control tasks, layers,
  probe architectures and random seeds are compared.
- **Valid inference**: MDL can distinguish how efficiently a declared learning pipeline
  extracts a declared label.
- **Invalid inference**: A long codelength cannot certify representation absence, and MDL
  does not uniquely define token pooling or the local task.
- **Local applicability/gate**: More principled probe comparison, but it would still create
  a new selectable probe pipeline. `FORMAL_ADJACENT`.

### 5. Dubois et al. (2020), arXiv:2009.12789

- **Source/status**: Yann Dubois, Douwe Kiela, David J. Schwab and Ramakrishna Vedantam,
  *Learning Optimal Representations with the Decodable Information Bottleneck*, NeurIPS
  2020.
- **Setting/object**: A two-player supervised representation game. Alice chooses
  **a priori** a task, loss, and predictive family \(\mathcal V\); Bob learns a representation.
- **Readout/selection**: \(\mathcal V\)-sufficiency and \(\mathcal V\)-minimality are defined
  relative to that preselected family. Experiments explicitly sweep MLP widths to vary family
  complexity.
- **Theory/assumptions/proof**: The main theorem assumes finite \(\mathcal X,\mathcal Y,
  \mathcal Z\), log loss, deterministic labels, at least one sample per class, and functional
  family assumptions. It proves optimal risk for ERMs on a
  \(\mathcal V\)-minimal/\(\mathcal V\)-sufficient representation. PAC estimation further
  assumes bounded log probabilities and controls Rademacher complexity.
- **Certified object**: Expected log-loss/generalization for the selected supervised task and
  family—not existence of a unique decoder for an already frozen LVLM representation.
- **Valid inference**: Once \(\mathcal V\) is fixed and assumptions hold, the framework
  formalizes family-relative decodability.
- **Invalid inference**: It cannot choose a local linear/nonlinear family, token pooling or
  regularization, nor turn probe failure into family-independent absence.
- **Local applicability/gate**: The local held-out rotation label and representation do not
  satisfy an architecture-derived \(\mathcal V\); the theorem is not a unique readout bridge.
  `FORMAL_ADJACENT`.

### 6. Harvey, Lipshutz & Williams (2024), arXiv:2411.08197

- **Source/status**: Sarah E. Harvey, David Lipshutz and Alex H. Williams,
  *What Representational Similarity Measures Imply about Decodable Information*, 2024
  preprint.
- **Setting/object**: Mean-centered response matrices for \(M\) stimulus conditions;
  optimal regularized **linear regression** readouts of a target vector.
- **Readout/selection**: The target distribution \(P_z\) and positive-definite
  regularization \(G(X)\) are inputs. Ridge strength or the CKA/CCA/GULP normalization is a
  chosen property, not selected by architecture.
- **Theory/assumptions/proof**: Propositions 1–2 express best/worst/average decoder
  alignment through normalized kernels; Corollary 1 requires
  \(E[zz^\top]=I\). Procrustes bounds use Bures/kernel identities and participation ratio.
  The paper explicitly leaves linear classification and finite-sample estimator theory open.
- **Valid inference**: Under the selected target distribution and regularization, CKA/CCA
  summarize average optimal linear-readout behavior.
- **Invalid inference**: Rotation invariance of a similarity metric does not establish
  task-specific rotation sufficiency; a rotation-specific readout can change under feature
  rotations that leave CKA unchanged.
- **Local applicability/gate**: No unique task target distribution, pooling or classifier
  follows; CKA/CCA/HSIC remain prohibited. `FORMAL_ADJACENT`.

## Direct and adjacent VLM/LVLM sources

### 7. Rahmanzadehgervi et al. (2024), arXiv:2407.06581

- **Source/status**: Pooyan Rahmanzadehgervi, Logan Bolton, Mohammad Reza Taesiri and
  Anh Totti Nguyen, *Vision language models are blind: Failing to translate detailed visual
  features into words*, 2024 preprint.
- **Setting/object**: Seven generated low-level visual tasks evaluated through GPT-4o,
  Gemini-1.5 Pro and Claude APIs; two prompts and multiple resolutions/rendering settings.
- **Readout/control**: Generated response accuracy only. The paper has no access to the
  commercial encoders, frozen features or projector inputs and trains no feature readout.
- **Evidence**: Mean performance is far below human expectation; late fusion and encoder
  loss are proposed as explanations. Bunny LoRA fine-tuning also fails to generalize.
- **Valid inference**: Current VLM responses are unreliable on the registered low-level
  visual constructions.
- **Invalid inference**: Response failure cannot locate the failure in the frozen encoder,
  projector or decoder.
- **Local applicability/gate**: Provides orientation/spatial motivation but no identifiability
  bridge. `HEURISTIC_ONLY`.

### 8. Theodoridis et al. (2026), arXiv:2603.06054

- **Source/status**: Nikos Theodoridis et al., *Probing Visual Concepts in Lightweight
  Vision-Language Models for Automated Driving*, 2026 preprint.
- **Setting/object**: Ovis2.5, InternVL3.5 and VST-SFT/VST-RL; CARLA counterfactual
  presence, count, spatial-relation and orientation sets.
- **Location/pooling/readout**: Activations from **every** vision-encoder and LLM block plus
  projector output. The paper switches between average pooling and hand-designed left/right
  region pooling; LLM probes concatenate pooled visual tokens and last text token.
- **Training/selection/metric**: Linear classifiers use AdamW. Learning rates
  \(10^{-4}\)–\(5\times10^{-1}\) are searched and the validation-best probe is retained;
  this is repeated ten times. Test and chance-corrected accuracy are reported.
- **Matched controls/external evidence**: Counterfactual images isolate one concept and the
  same held-out images are also scored by each LVLM. Cases with high last-layer probe
  accuracy but low response accuracy directly orient toward downstream non-use.
- **Inference boundary**: The authors explicitly define “absent/not encoded” as “not
  linearly encoded,” not completely absent. They also show that average pooling can miss
  orientation retained in spatial token structure.
- **Valid inference**: A selected positive probe can demonstrate selected-family
  decodability and can refute “no linearly accessible signal at that selected interface.”
- **Invalid inference**: A negative probe cannot prove general absence; the local readout is
  not unique because layer, pooling, learning rate and repetition selection are essential.
- **Local applicability/gate**: Strongest direct orientation evidence and supports keeping
  downstream absorption open, but its protocol violates the frozen no-sweep gate and uses
  different encoders/data/interfaces. `REJECT_FOR_BRIDGE`.

### 9. Kawasaki, Tanaka & Nishida (2026), arXiv:2604.04411

- **Source/status**: *Responses Fall Short of Understanding: Revealing the Gap between
  Internal Representations and Responses in Visual Document Understanding*, CVPR 2026
  MULA workshop.
- **Setting/object**: Qwen2.5-VL-32B, Gemma3-27B and LLaVA-NeXT-13B on four binary
  visual-document tasks. Samples are deliberately filtered to Qwen2.5-VL-3B failures,
  removing 78%.
- **Location/pooling/readout**: For each LLM layer, four separate probes use mean-pooled
  image tokens, mean-pooled text tokens, mean-pooled all tokens, or the last token.
- **Training/selection/metric**: One linear layer with cross-entropy, Adam
  \(10^{-3}\), cosine schedule, batch 256, one epoch. The reported gap is explicitly
  \(\max_l A_{LP}(l)-A_{resp}\); the analysis also compares token types.
- **Controls/external evidence**: Same task data are used for probe and response accuracy.
  Follow-up layer-group fine-tuning improves both quantities but groups are chosen from
  observed probe transitions.
- **Valid inference**: It supplies direct evidence that a selected internal representation can
  be more linearly predictive than the generated response.
- **Invalid inference**: Max-over-layer/token evidence cannot select a unique prospective
  readout and does not inspect the frozen vision encoder output.
- **Local applicability/gate**: Supports the downstream-unabsorbed hypothesis space but
  directly violates unique location/token pooling. `REJECT_FOR_BRIDGE`.

### 10. Zhao et al. (2024), arXiv:2403.09037

- **Source/status**: Qinyu Zhao et al., *The First to Know: How Token Distributions Reveal
  Hidden Knowledge in Large Vision-Language Models?*, ECCV 2024.
- **Setting/object**: Seven LVLMs; unanswerable VQA, jailbreak, deception, answer
  correctness, hallucination and ImageNet classification.
- **Location/readout**: Task-specific logistic regression or LDA on the first generated-token
  logit vector. The study also compares later-token logits, probabilities/log-probabilities,
  hidden states, CLIP image/text/joint embeddings, and three prompt families.
- **Training/selection/metric**: Each task needs labeled probe data; ACC/F1/AUC and
  task-specific attack metrics are used. ImageNet uses 16 shots/class and three repetitions.
- **Controls/external evidence**: On-task decoding can outperform generated responses and
  guide a hand-written template decoder. CLIP performance exposes substantial dataset bias.
- **Valid inference**: First-token logits can contain selected-task information that ordinary
  decoding does not express.
- **Invalid inference**: The output-logit finding does not locate signal in the frozen visual
  output, and task/prompt/readout alternatives are not architecture-unique.
- **Local applicability/gate**: Direct LVLM response-gap evidence, but it occurs downstream
  of the projector/LLM and changes label construction. `REJECT_FOR_BRIDGE`.

### 11. Zhang, Yang & Agrawal (2025), arXiv:2412.04616

- **Source/status**: *Assessing and Learning Alignment of Unimodal Vision and Language
  Models*, CVPR 2025 Highlight.
- **Setting/object**: Multiple frozen unimodal vision and text encoders; linear alignment
  layers trained on 2.2M CC3M pairs and evaluated by zero-shot COCO retrieval.
- **Location/pooling/readout**: The study selects anchor encoders, 224px inputs, paired
  global embeddings, two learned alignment maps, 2048 output dimensions and retrieval
  R@10. The full SAIL method then chooses a nonlinear GLU, refined sigmoid loss, captions
  and 23M pairs.
- **Training/selection**: LION, learning rate \(10^{-5}\), weight decay \(10^{-7}\),
  temperature/bias choices, batch 32768, 100 epochs for alignment probing. Ablations select
  architecture, loss and caption recipe.
- **Controls/external evidence**: Frozen-backbone alignment performance is compared with
  ImageNet kNN/linear probing; a SAIL vision encoder is later integrated into LLaVA-1.5 and
  evaluated on seven MLLM tasks.
- **Valid inference**: A declared alignment family can compare how readily specific
  unimodal encoders align under a large contrastive training protocol.
- **Invalid inference**: This does not identify orientation signal at the local projector
  interface; the paper itself finds kNN clustering more predictive than linear separability.
- **Local applicability/gate**: Different encoder, image resolution, feature interface,
  data, objective and readout; not a checkpoint-only unique test. `REJECT_FOR_BRIDGE`.

### 12. Panos et al. (2024), arXiv:2407.16526

- **Source/status**: Aristeidis Panos, Rahaf Aljundi, Daniel Olmeda Reino and Richard E.
  Turner, *Imperfect Vision Encoders: Efficient and Robust Tuning for Vision-Language
  Models*, 2024 preprint.
- **Setting/object**: OpenAI-CLIP-L/14 and EVA-CLIP-G/14 used in LLaVA and MiniGPTv2;
  TSI/GTS domain shifts, DALL-E controls and VQA/classification transfer.
- **Readout/intervention**: Zero-shot CLIP classifiers and generated VLM responses motivate
  encoder updates. LoRSU selects MLP coordinates and attention heads using task-gradient
  magnitude, plus chosen LoRA rank/top-\(k\) budgets.
- **Theory/assumptions/proof**: A constrained binary optimization shows top-gradient masks
  best preserve local gradient norm. It does not prove frozen-feature sufficiency or decoder
  completeness.
- **Controls/external evidence**: Encoder versus LLM updates, full fine-tuning, LN, LoRA,
  SPU and LoRSU are compared; updated encoders are plugged back into two VLMs.
- **Valid inference**: In its datasets, targeted encoder updates can causally improve both
  encoder classification and downstream VLM performance.
- **Invalid inference**: Baseline failures do not prove the original feature lacked all
  task-relevant signal, and the intervention does not define a fixed diagnostic readout.
- **Local applicability/gate**: Supports an encoder-side repair option if stronger evidence
  later localizes failure, but cannot perform that localization here. `HEURISTIC_ONLY`.

### 13. Tong et al. (2024), arXiv:2406.16860

- **Source/status**: Shengbang Tong et al., *Cambrian-1: A Fully Open, Vision-Centric
  Exploration of Multimodal LLMs*, NeurIPS 2024 Oral.
- **Setting/object**: 23 vision backbones integrated with a matched Vicuna-1.5-7B,
  connector/instruction data and hyperparameters; frozen/unfrozen recipes and vision-centric
  benchmarks including CV-Bench.
- **Location/readout**: Last-layer features are resized/interpolated to specified token
  counts and passed through an MLLM connector. A separate catalog reports standard
  ImageNet linear probing, but the paper explicitly argues that MLLM evaluation should move
  beyond linear probing.
- **Controls/external evidence**: Extensive matched model recipes show that encoder identity,
  adapter data, unfreezing, resolution, connector and mixtures affect downstream results.
- **Valid inference**: Frozen visual representation choice and encoder training can matter
  to generative MLLM behavior under controlled recipes.
- **Invalid inference**: The 23-encoder/recipe comparison does not yield a single local
  rotation readout or distinguish absence from downstream non-use in a frozen checkpoint.
- **Local applicability/gate**: Strong mechanism orientation and external benchmark
  evidence, but not a unique identifiability bridge. `HEURISTIC_ONLY`.

## Exact local-interface audit

| Item | Read-only evidence | Consequence |
|---|---|---|
| Encoder identity | `SiglipVisionModel`, 12 layers, hidden 768, 256px input, 32px patches | Exact local feature producer is known |
| Preprocessing | resize 256×256, bilinear, rescale 1/255, mean/std 0.5 | Input transform is known |
| Frozen output | `outputs.last_hidden_state` | Architecture fixes the feature location |
| Downstream interface | 64 visual-token vectors are passed independently through LayerNorm → Linear → GELU → Linear and inserted into the LM sequence | Architecture preserves token structure; it does not pool to one task label |
| Missing native object | no orientation classifier/head, class prototype, task loss, pooling, regularization or completeness result | A scientific readout still requires analyst choices |

Architecture therefore fixes **where** to inspect, but not **how** to read orientation signal
or how to interpret a negative result.

## Immutable acceptance-gate decision

| Acceptance gate | Result | Evidence |
|---|---|---|
| ≥1 formal source uniquely fixes readout and inference boundary | **FAIL** | Every formal quantity is relative to a supplied family, target distribution or regularization; none selects the local task readout |
| ≥1 independent direct VLM/LVLM source with frozen-output readout/downstream control | **PARTIAL, NOT SUFFICIENT** | Direct response-gap studies exist, but depend on layer/token/pooling/hyperparameter selection or inspect downstream logits |
| Exact location, pooling, family, fit, regularization and metric need no local choice | **FAIL** | Only location is architecture-fixed |
| Exact local encoder/interface is read-only verifiable | **PASS** | SigLIP2 last-hidden-state → 64-token projector interface is explicit |
| Checkpoint-only test distinguishes the competing explanations | **FAIL** | Positive inference is family-relative; negative inference lacks completeness/impossibility |
| No failed proxy or sweep is restored | **PASS only by not testing** | No checkpoint/probe was run |
| Unique unseen readout prediction can be frozen | **FAIL** | No unique readout specification exists |
| Resource/final-confirmation gate | **PASS** | A probe would be locally cheap, but scientific identifiability—not compute—is missing |
| Encoder-side vs downstream-side algorithm split follows | **CONCEPTUAL ONLY** | Literature supports both branches, but the current bridge cannot select one locally |

## Scientific scope

- **Decision**: `NO_CANDIDATE`
- **Failure level**: `BRIDGE_REJECTED`
- **Exactly rejected**: the current formal-probing/direct-LVLM literature plus MiniMind-V
  architecture does not uniquely specify a no-sweep frozen-feature readout with
  family-independent negative evidence.
- **Not rejected**: useful frozen-feature signal; linear or nonlinear decodability under a
  separately justified family; downstream absorption/transfer failure; objective mismatch;
  encoder limitations; encoder-side repair; task-specific representation mechanisms.
- **Search implication**: do not create another probe. Move to an authoritative
  controlled-coverage data gate, where labels/strata and the causal contrast may be fixed by
  source dataset semantics rather than by a post-hoc representation metric.
