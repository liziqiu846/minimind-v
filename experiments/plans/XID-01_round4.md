# XID-01 Round 4 — matched-support MiniMind-V mechanism pilot

**日期**：2026-08-07
**阶段**：阶段三，`MECHANISM-INTERVENTION TRAINING`
**角色**：`SCIENTIFIC_MECHANISM` prediction test
**证据上限**：one paired seed 只判定是否值得补至 total 3；即使三 seed 阳性也最多
为 `CONCLUSION_CANDIDATE`，不自动进入阶段四

## 科学问题

在总样本数、exact pixel multiset、visual/language/target marginals、每个 key 的
target entropy、target-token order、prompt length、训练步数、参数坐标与 paired
seed 全部匹配时，只有 **跨 key 一致的 interaction-diagnostic support** 是否比
**同样必须看图但跨 key interaction rule 相互抵消的 ambiguous support** 更能泛化到
两者都未见的 image-marker × language-key combination？

This training run distinguishes:

> **Explanation A — interaction identifiability**：支持中的 cross-modal cells 必须
> 一致地区分 intended rule 与竞争 rule，才能识别可迁移 interaction；

from

> **Explanation B — visual necessity / conditional target entropy alone**：只要每个
> language key 下都必须看图、视觉/语言/target 边际和训练量相同，joint rule 是否
> 跨 key 一致不应产生额外 held-out advantage。

## 假设

> 假设 H：`interaction-consistent` condition 将在独立 base images 的 held-out
> `(marker=1,key=e)` 上优于 `interaction-ambiguous`，并在 keys `a–d` 的完整
> marker factorial panel 上更稳定地实现同一个 XOR rule。

如果 paired pilot 未同时达到预注册 target 与 mechanism gates，且数据、token、
pixels、training 和 scorer audits 均通过，则当前 synthetic MiniMind-V
instantiation 被否定；不得调 learning rate、marker、ratio、keys、threshold、model
allocation 或 metric rescue。

## VLM 特有性

每个 example 同时含：

- visual factor \(V\in\{0,1\}\)：由图像上高可见、固定规范的两种 border marker
  表示；
- language key \(L\in\{a,b,c,d,e\}\)：由 prompt 中 singleton tokenizer token
  表示；
- binary next-token target \(Y\in\{0,1\}\)。

Intended rule 是

\[
Y=V\oplus s(L),
\]

其中

\[
s(a)=0,\quad s(b)=1,\quad s(c)=1,\quad s(d)=0,\quad s(e)=0.
\]

只看图或只看 language key 都不能在完整 factorial 上达到零风险。两个条件都在
keys `a–d` 下观察到 \(V=0/1\) 与 \(Y=0/1\)，因此都排除 language-only fit；
差异是这些 visual dependencies 是否共享同一跨 key rule。

## Frozen ten-row block

每个 block 含 10 个 injection rows。两个条件使用完全相同的 ordered
`(pixel bytes, V, Y)` rows，只交换 keys `c` 与 `d` 对这些 rows 的配对；每个 key
出现 2 次，每个 `a–d` 都有 \(V=0/1\) 和 \(Y=0/1\)，`e` 只见
`(V=0,Y=0)` 两次。

### `interaction-consistent`

| key | observed rows | relation |
|---|---|---|
| `a` | `(V=0,Y=0)`, `(V=1,Y=1)` | XOR, \(s=0\) |
| `b` | `(V=0,Y=1)`, `(V=1,Y=0)` | XOR, \(s=1\) |
| `c` | `(V=0,Y=1)`, `(V=1,Y=0)` | XOR, \(s=1\) |
| `d` | `(V=0,Y=0)`, `(V=1,Y=1)` | XOR, \(s=0\) |
| `e` | `(V=0,Y=0)` twice | target combination held out |

### `interaction-ambiguous`

| key | observed rows | relation |
|---|---|---|
| `a` | `(V=0,Y=0)`, `(V=1,Y=1)` | XOR |
| `b` | `(V=0,Y=1)`, `(V=1,Y=0)` | XOR |
| `c` | `(V=0,Y=0)`, `(V=1,Y=1)` | XNOR relative to frozen \(s(c)=1\) |
| `d` | `(V=0,Y=1)`, `(V=1,Y=0)` | XNOR relative to frozen \(s(d)=0\) |
| `e` | `(V=0,Y=0)` twice | target combination held out |

Thus global XOR and the competing cross-key rule tie on `a–d` in the ambiguous
condition, while consistent support uniquely favors the frozen rule. Both conditions
have per-block:

- \(N=10\);
- visual counts `V0:6,V1:4`;
- language counts `a:b:c:d:e = 2:2:2:2:2`;
- target counts `Y0:6,Y1:4`;
- for every key `a–d`, conditional target counts `0:1`;
- exact ordered target tokens and exact ordered pixel bytes.

## Data construction

- Common base: exact 10,000-row frozen Stage2 train parquet used by VISSUP-01, SHA-256
  `3c3d90c525f43200d35ebd5b4ac1719c8336d278aecbf7e929997c8401b1d5ce`;
- deterministic unique-pixel ordering reuses domain
  `SHA256("XID01_IMAGE_ORDER_V1\0" || normalized_pixel_sha256)`;
- first 1,040 unique images form 104 training blocks;
- next 1,008 disjoint unique images form the held-out panel;
- injection image for each row adds the frozen visual marker corresponding to its
  ordered block slot; conditions share byte-identical images at every row;
- marker type 0: fixed blue border RGB `(0,114,178)`;
- marker type 1: fixed orange border RGB `(230,159,0)`;
- border width:
  `max(12, floor(min(width,height)/8))`, clipped so the interior remains nonempty;
- deterministic PNG, no augmentation, no marker/ratio search;
- 10,000 common base rows + 1,040 injection rows = 11,040 rows per condition;
- micro-batch 4, accumulation 4, 3 epochs = exactly 2,070 optimizer steps.

Held-out images may occur as unmarked common caption rows in both conditions. The
estimand is new marker × key composition on known base-image support, not new-image
generalization.

## Frozen conversation and target

The prompt is:

```text
<image>
Use the visible border marker together with rule key {KEY}.
Answer with digit 0 or 1 only.
```

Assistant target is the singleton digit `0` or `1` followed by the standard EOS. Before
training, audit keys `a–e` and targets `0/1` as singleton tokens, equal prompt lengths,
equal target intervals/masks, and exact per-row token invariants. No natural-language
description of the XOR mapping is provided.

## Model and paired training

- model: `M2-current` frozen Stage2 base;
- trainable coordinates:
  `vision=582, projector=2327, language=1187`, total 4,096;
- mapping roots: pilot `43301`; positive only then `43302/43303`;
- train seed `2026`, AdamW, learning rate `0.05`, 3 epochs, micro-batch 4,
  accumulation 4, identical cosine schedule and permutation by row index;
- condition order: `interaction-ambiguous` then `interaction-consistent`;
- initial coordinate state exact zero; frozen tensors must have identical initial/final
  hashes; no checkpoint selection, no hyperparameter tuning.

## Held-out prediction panel

Use all 1,008 held-out base-image groups, with deterministic marker variants.

### Primary target

For every image group, score key `e` with marker `V=1`; gold target is `1`. This exact
combination is absent from both training injections, while key `e`, marker `V=1`, and
target `1` each occur separately.

Primary statistic: equal-weight image-group forced-choice accuracy over digit `0/1`.
Direction statistic: gold margin

\[
L(0)-L(1),
\]

where lower NLL is better.

### Mechanism panel

For every image group, score all 8 cells `keys a–d × V0/V1` under the frozen XOR
mapping. Report equal-weight group accuracy and within-group full-rule success
(all 8 correct). This panel checks whether the intervention changes the intended
cross-key interaction rather than only key `e`.

Paired bootstrap: 10,000 resamples of independent base-image groups, seed `20260807`.
No subset, key, marker, prompt or metric selection after scoring.

## Minimum execution order

1. commit this immutable plan;
2. implement deterministic builder, trainer adapter, scorer and analyzer;
3. run preflight only: exact pixel/token/marginal/block/target-absence/permutation/model
   audits and resource check;
4. commit implementation + preflight;
5. run at most 2 injection samples per condition as non-scientific smoke;
6. if smoke passes, train root `43301` in frozen order;
7. only after both runs finish, score once and analyze once;
8. only `PILOT_POSITIVE` permits identical roots `43302/43303`.

## Pilot support criteria

Root `43301` must satisfy all:

1. all paired engineering/data invariants pass; loss/gradients finite; both runs have
   exactly 2,070 steps;
2. primary target:
   `accuracy_consistent - accuracy_ambiguous >= 0.10`, paired-bootstrap 95% CI lower
   `>0`, `accuracy_consistent >=0.65`, and gold-margin difference `>0`;
3. mechanism panel:
   accuracy difference `>=0.05`, paired-bootstrap 95% CI lower `>0`,
   `accuracy_consistent >=0.75`, and full-rule-success difference `>0`.

All must pass to add roots. This is only a pilot direction check.

## Final three-root support criteria

With configuration unchanged:

1. primary accuracy difference `>0` for all 3 roots;
2. at least 2/3 roots have primary difference `>=0.10` and CI lower `>0`;
3. three-root equal mean primary difference `>=0.10` and consistent absolute accuracy
   `>=0.65`;
4. mechanism accuracy difference `>0` for all roots and equal mean `>=0.05`;
5. at least 2/3 roots have mechanism CI lower `>0`;
6. three-root mean primary gold-margin and full-rule-success differences both `>0`.

Passing yields only `CONCLUSION_CANDIDATE` / `REVIEW_QUEUE`.

## Rejection criteria

Any valid pilot failure rejects the current empirical instantiation:

- primary or mechanism direction `<=0`;
- any pilot effect/CI/absolute gate fails, including small positive effects;
- full-rule-success difference `<=0`;
- three-root instability or any final criterion failure.

Effect size, seed direction or unexpected outcome is scientific evidence, not rescue.
Do not change marker, injection ratio, key mapping, prompt, LR, coordinates, epochs,
threshold, panel or metric.

## Inconclusive / rescue boundary

Only:

- exact data/token/pixel/marginal audit fails before training;
- marker is not represented as distinct pixels due implementation error;
- wrong checkpoint/protocol, corrupted data, preprocessing mismatch, metric error,
  OOM/job failure, or proven code bug;
- required local asset is unavailable.

Implementation bugs may be minimally fixed without changing the frozen scientific
construction. Otherwise no rescue budget.

## Possible confounds and inference boundary

- synthetic border/key XOR is not a real task distribution;
- positive results may depend on MiniMind-V's inductive bias for color borders and
  singleton keys;
- common caption rows dilute diagnostic mass and may favor unrelated language behavior;
- forced-choice NLL is not free generation;
- target key `e` has only `V=0` in training, so positive transfer relies on cross-key
  rule sharing exactly as intended;
- frozen encoder/low-dimensional coordinates may cap performance;
- the experiment validates a support-arrangement direction, not a numeric estimator of
  \(\beta\) or \(\gamma\).

These restrict positive conclusions; they do not permit post-hoc task changes.

## Resources

- pilot training: 2 conditions × 1 root, approximately 0.28 GPU-hours total based on
  previous M2-current runs;
- positive-only extension: 4 additional trainings, total candidate maximum 6;
- GPU: one visible A40/A100 per process; no multi-GPU;
- final confirmation: not accessed;
- disk: coordinates, manifests and small synthetic parquets/images only; no large model
  checkpoints.

## Frozen declaration

This plan must be committed before implementation, preflight, smoke, training or
scoring. No scientific field above may be changed after outcome. Any scientifically
necessary revision creates a new idea/round and does not inherit training budget.
