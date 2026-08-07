# LITMAP-07 Round 1 Evidence Matrix

## Epistemic boundary

The `XID-01_round4` target reversal is a trigger for explanation search, not positive
evidence for any explanation. This matrix selects a mechanism only from independent
primary evidence plus a falsifiable local distinction. A diagnostic gradient, attention
map or benchmark score is not itself the scientific mechanism.

## Decisive sources

| Source | Setting and strongest usable evidence | Formal object / assumptions | Limitation for this project | Implication |
|---|---|---|---|---|
| Park et al., arXiv:2501.02669 | Controlled autoregressive VLM tasks with text- and image-equivalent inputs. Explicit image-to-text supervision improves simple-to-hard image generalization; mixed supervision can internalize conversion. Hard-text examples and an early alignment phase alter image generalization. | Theorems F.1/F.2 identify, in the infinitesimal-step limit under smooth/bounded-gradient assumptions, the ratio between training-update alignment and immediate held-out hard-image loss decrease. | Synthetic tasks, brittle CoT, no theorem that aligned gradients recover a shared rule or improve population compositional risk. Real-world extension is explicitly open. | Direct generative-VLM evidence that target decomposition can change the direction in which image-conditioned updates transfer. |
| Deng et al., CVPR 2025 | Ten VLMs prefer relevant text over conflicting visual evidence. A fixed-size mixture containing text-only and text-augmented multimodal examples reduces text bias. | Transformer-covering risk analysis for a pure-text/multimodal mixture under bounded Lipschitz loss and norm assumptions. | Does not model balanced key-specific visual rules or show that the learned representation is factorized. | Independent evidence that training composition and autoregressive language priors change visual credit; supports, but does not prove, the selected mechanism. |
| Zhang et al., arXiv:2403.05262 | LLaVA/InstructBLIP/Qwen-VL retain confident language-prior answers with absent or meaningless images; image-free contrastive logits reduce some hallucination/reasoning errors. | No training-dynamics theorem. Attention allocation is explanatory evidence only. | Primarily post-hoc decoding/calibration; includes generation-configuration search and cannot decide representation versus optimization. | Corroborates language-prior dominance, but is not an algorithm template for the active route. |
| Peng et al., CVPR 2022 | On four audio-visual datasets, fused objectives can make a stronger modality optimize faster and suppress the weaker one; gradient modulation improves multimodal accuracy. | Theorem 1 characterizes reduced SGD noise under modulation, not VLM compositional generalization. | Non-generative audio-visual classification; even the method does not recover best unimodal performance. | Establishes optimization imbalance as a real training phenomenon, while warning that gradient modulation alone may not solve representation/architecture limits. |
| Fan et al., CVPR 2023 | Prototype-guided stimulation of a slow modality and regularization of a fast one improve multimodal classification across controlled baselines. | Empirical method study; no compatible autoregressive risk theorem. | No discrete next-token rule or held-out image×language composition. | Independent support for under-optimized modalities, not sufficient evidence for the selected LVLM mechanism by itself. |
| Tong et al., NeurIPS 2024 | Matched MLLM studies show visual encoder choice, connector pretraining, adapter data and unfreezing the vision encoder all affect vision-centric performance; unfreezing is widely beneficial. | Large controlled empirical design; no rule-formation theorem. | Components and data scale are much larger than MiniMind-V; aggregate benchmarks do not isolate shared-rule learning. | Keeps representation/trainability ceiling as a serious competing explanation. |
| Laurençon et al., NeurIPS 2024 | Controlled VLM design study: stronger visual backbone improves downstream scores; frozen fully-autoregressive architecture underperforms cross-attention, while adding LoRA degrees of freedom reverses the comparison. | Empirical architecture/training study. | Four aggregate benchmarks and 6k-step ablations do not establish a specific frozen-feature impossibility. | Direct evidence that representational access and trainability can be limiting, so a credit-only conclusion requires an intervention that holds them fixed. |
| Daunhawer et al., ICLR 2023 | Theorem 1 block-identifies shared invariant content under a continuous invertible multimodal generative process and asymptotic contrastive objective; proof shows all global minimizers identify content. | Content invariance, style perturbations, continuous/smooth invertible mixing, known content dimension, global optimum. | It is an identifiability-at-global-optimum theorem, not an optimization result for discrete autoregressive targets. | Formalizes the exact gap exposed by XID: population/global-optimum identification does not show that a neural optimizer reaches a shared factorization. |
| Fu et al., arXiv:2405.11743 | General compositional-generalization no-free-lunch and risk decomposition under a formal composition rule. | Task-agnostic CG distributions and measure-preserving composition assumptions. | Does not specify image-conditioned AR optimization; “generative effects” remain open. | Justifies a task-specific bridge rather than abandoning the route because no complete LVLM theorem exists. |
| Zhang et al., ICML 2023 | Rademacher bound for dynamic late fusion decomposes weighted empirical loss, modality complexity and weight–loss covariance; experiments use RGB-depth and image-text classification. | Binary decision-level late fusion; dynamic weights; negative weight–loss correlation and effective uncertainty assumption. | Incompatible with token-concatenated generative LVLMs and does not address shared rule formation. | A genuine multimodal bound, but not the needed mechanism; route rejected for current ACTIVE. |
| Li et al., NeurIPS 2025 | Individual visual/text skills can be high while cross-modal composition remains poor; caption/reasoning interventions improve but do not close the gap. | Controlled generative VLM tasks; empirical interventions. | Multi-factor algorithm and no general theorem. | Confirms that component skill exposure alone is insufficient; a factorized-training explanation remains scientifically meaningful. |

## Competing-mechanism comparison

| Candidate | Can explain mechanism-panel chance? | Can allow target reversal without treating it as evidence? | Directional discriminator | Local no-sweep test | Algorithmic exit | Decision |
|---|---|---|---|---|---|---|
| Generic shared factorization | Yes, but only by restating the failure | Yes | Underspecified | Would require choosing architecture/factorization measure | Modular architecture | `BACKLOG`: too broad |
| Generic language-prior / modality imbalance | Yes | Yes | Reduce text prior or rebalance gradients | Requires choosing loss weight, module and schedule | Gradient modulation | `NEXT`: real phenomenon, insufficiently specific |
| Frozen representation / 4,096-coordinate ceiling | Yes | Yes | Any fixed-capacity supervision requiring the marker state must fail | Can be retained as the null competing explanation | Encoder unfreezing/capacity | `NEXT`: competing explanation, not selected |
| **Shared visual-state mediation of autoregressive gradients** | **Yes: answer-only gradients may be key-specific and fail to build a reusable visual state** | **Yes: different key-local fits can alter one held-out cell arbitrarily** | **Holding pixels, support, coordinates and answer target fixed, key-invariant visual-state supervision should improve both explicit state prediction and the full cross-key rule; if the state is unrepresentable, both fail** | **Theory-first gradient identity, then one matched auxiliary-target intervention with no layer/rank/ratio search** | **Factorized visual-state supervision, internalized visual conversion or task-decomposition curriculum** | **`ACTIVE_CONJECTURE`** |

## Selected mechanism

`VSTATE-01` is:

> Under answer-only autoregressive supervision, the visual update for a compositional
> target can be multiplied by key-dependent residuals and cancel or specialize across
> language keys. A key-invariant visual-state target supplies a shared gradient component,
> factorizing image-state acquisition from language-conditioned rule application and
> thereby improving transfer to unseen image×key compositions.

This is not a claim that intermediate text is universally beneficial. It predicts a
specific interaction:

1. the relevant visual state must be representable under the fixed model/coordinate
   class;
2. the auxiliary state must be invariant across language keys;
3. the state-supervised update must align with held-out compositional risk;
4. improvement must occur on the complete rule panel, not only one target cell.

The missing theorem bridge is well-posed: Park et al. relate update alignment to
immediate held-out loss change, while Daunhawer et al. characterize shared-factor
identification only at a global optimum. Neither proves when autoregressive auxiliary
state supervision prevents key-wise gradient cancellation and recovers a compositional
rule. Establishing that bridge is the next theory problem.

## What is rejected

- Dynamic late-fusion uncertainty weighting is incompatible with the local generative
  architecture and would revive a weighting/proxy route.
- Generic connector or encoder allocation is not re-opened after `PROJALLOC-01`; the
  representation ceiling remains a competing explanation rather than a license for an
  allocation sweep.
- Attention, gradient-alignment scores and image-ablation margins will not become
  checkpoint-selection proxies.
- The `XID-01` border/key/ratio/LR/support result will not be rescued or rerun.
