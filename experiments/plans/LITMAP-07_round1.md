# LITMAP-07 Round 1 — XID failure-targeted neural factorization search

**日期**：2026-08-07
**阶段**：阶段三，targeted literature/theory search
**角色**：`SCIENTIFIC_MECHANISM_RESELECTION`
**前序证据**：`XID-01_round4` valid empirical instantiation rejection

## 科学问题

`XID-01` 的 population-identifying support 没有在 MiniMind-V 中形成 shared
cross-key rule，且 consistent condition 强烈损害 held-out target。当前最值得推进的
机制是：

1. autoregressive visual credit assignment 使模型 task-specifically 吸收各 key 的
   局部视觉条件；
2. 模型缺少形成 shared cross-modal factorization 的 representation/optimization
   bias；
3. frozen vision representation 或 4,096-coordinate trainability ceiling 使规则本身
   不可实现；

还是权威文献与反例指向一个更好的 fourth mechanism？

## 假设

> 若 round4 失败暴露的是具有论文潜力的 neural mechanism，而不是任意 synthetic
> task artifact，则 primary literature 应能给出至少一条可核查的
> data/objective/architecture → factorized cross-modal representation or
> key-specific absorption → unseen composition risk 链，并产生可区分至少两个竞争
> 解释的 prediction。

如果所有路线都只能通过 layer/probe/metric/hyperparameter 选择事后解释，或 direct
evidence 只显示 benchmark correlation 而没有 mechanism intervention，则这些路线
不得登记为新训练 candidate。

## VLM 特有性

目标对象必须涉及视觉因素与语言/task factor 的联合规则形成。普通单模态
compositionality/implicit-bias theorem 只能作为数学工具；若不能明确映射到
image-conditioned autoregressive prediction，不得独立决定 ACTIVE。

## Targeted search families

### F1 — factorized / modular cross-modal rule formation

- `"vision language" compositional representation factorization systematic generalization`
- `multimodal compositional generalization shared rule modular representation`
- `generative VLM skill composition unseen combinations`
- `cross-modal binding factorized representation theorem`

### F2 — autoregressive visual credit and task-specific absorption

- `autoregressive vision language visual credit assignment shortcut task-specific`
- `LVLM language bias visual token gradient dominance training dynamics`
- `multimodal instruction tuning task-specific visual absorption transfer`
- `vision language optimization modality imbalance theorem`

### F3 — representation/trainability ceiling

- `frozen vision encoder compositional task sufficiency adapter expressivity`
- `vision-language projector expressivity cross-modal composition`
- `parameter efficient multimodal adaptation expressivity theorem`
- `frozen features interaction learning limitation`

### F4 — theorem tools

- `gradient descent compositional generalization factorized rule implicit bias`
- `neural networks systematic generalization modularity theorem`
- `identifiability optimization gap population minimizer neural representation`

## Databases and preservation

Search date is fixed to 2026-08-07.

1. Parallel academic web search and unrestricted supplementary web search;
2. OpenAlex API;
3. arXiv API;
4. Semantic Scholar API if accessible without a new credential.

All raw responses, exact query strings, timestamps and deterministic deduplication outputs
must be saved. No figure will be generated because the user explicitly cancelled it.

## Inclusion criteria

- primary paper or authoritative conference/journal version;
- formal theorem/proposition with inspectable assumptions/proof idea, or direct VLM/LVLM
  controlled intervention that bears on one of F1–F3;
- explicit outcome involving unseen composition, cross-task transfer, rule reuse,
  modality imbalance/credit, or frozen-feature trainability;
- 2018–2026 for empirical work, with older seminal theory allowed;
- English full text or sufficiently complete official appendix available.

## Exclusion criteria

- benchmark-only score without mechanism-relevant control;
- generic compositional generalization with no credible multimodal mapping;
- survey/blog/model card used as decisive evidence;
- method requiring post-hoc layer/token/probe/metric choice to support its claim;
- papers already rejected by LITMAP-04/05 unless a different theorem or experiment is
  directly relevant to the new failure;
- work that only lowers loss or complexity without explaining unseen risk.

## Minimum evidence extraction

For every decisive source record:

- problem setting and model family;
- theorem/proposition and assumptions, or exact intervention/control;
- proof idea when formal;
- train/selection/test protocol;
- whether the outcome distinguishes F1, F2 and F3;
- limitations and local applicability;
- DOI/arXiv/venue verification.

## 支持标准

Select a new `SCIENTIFIC_MECHANISM` as ACTIVE only if:

1. at least two independent primary sources support the mechanism or one formal source plus
   one direct generative-VLM intervention;
2. it explains both round4 mechanism-panel chance behavior and the possibility of primary
   target reversal without treating reversal itself as positive evidence;
3. it yields a directional prediction that distinguishes at least two of F1–F3;
4. it has a realistic MiniMind-V test or theorem construction without proxy/layer/rank/
   ratio/metric search;
5. it has a natural training-algorithm or optimization-principle exit if later supported.

A missing complete LVLM theorem bridge is not rejection if the missing bridge is
well-posed, nontrivial, grounded by direct evidence, and can be constructed as the next
theory problem.

## 否定标准

- route only renames the XID failure or restates generic no-free-lunch;
- decisive evidence cannot distinguish factorization, credit assignment and trainability;
- local test would require a hyperparameter/component/proxy sweep;
- claimed theorem uses incompatible objective/data/independence assumptions and no
  worthwhile new bridge can be stated;
- candidate duplicates a failed VISSUP/PROJALLOC/LITMAP-04/05 instantiation.

Rejected routes must be recorded with exact scope; upper mechanisms remain open unless
directly tested.

## 无法判断标准

Only if decisive primary full texts or theorem appendices are unavailable, databases are
inaccessible, or two mechanisms remain genuinely observationally equivalent after the
full extraction. Inconclusive search does not authorize training.

## 最小执行

1. run and preserve the four search families across the available databases;
2. deterministically deduplicate by DOI/arXiv/title;
3. screen titles/abstracts against the fixed criteria;
4. inspect 8–15 decisive primary sources in full;
5. build a mechanism × evidence × competing-explanation matrix;
6. select exactly one ACTIVE mechanism or record `NO_CANDIDATE`;
7. if selected, define the next unique theory question or minimal falsification plan before
   any new analysis/training.

## 资源与边界

- 0 GPU, 0 checkpoint inference, 0 model training;
- no final confirmation access;
- no AI-generated figure;
- no change to Mission Question or stage label;
- literature absence is evaluated as a possible research gap, not automatically as route
  failure.
