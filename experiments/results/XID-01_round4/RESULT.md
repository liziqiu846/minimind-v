# XID-01 Round 4 — matched-support MiniMind-V pilot

## 当前科学问题

在 pixels、visual/language/target marginals、per-key target entropy、target-token
order、steps、coordinates 与 paired seed 全部匹配时，interaction-consistent
support 是否比同样 visual-necessary 但 cross-key rule ambiguous 的 support 更能
泛化到 held-out `(key=e,V=1)`？

## 假设

若 interaction identifiability 是当前 MiniMind-V 泛化的有效机制，则 consistent
条件必须同时提高 primary target 与完整 `a–d × V0/V1` mechanism panel。

## 本轮实验

M2-current、root `43301`，两个条件各 11,040 rows、3 epochs、2,070 optimizer
steps、4,096 trainable coordinates。对 1,008 个独立 held-out base-image groups
评分 primary target 与 8-cell mechanism panel；paired bootstrap 10,000 次。

## 判定标准

- 支持：primary 差至少 `+10 pp` 且 CI lower `>0`、consistent accuracy
  `>=0.65`、margin 差正；mechanism 差至少 `+5 pp` 且 CI lower `>0`、
  consistent accuracy `>=0.75`、full-rule-success 差正。
- 否定：任一门失败，包括小正效应、反向效应或 full-rule-success 差不正。
- 无法判断：仅限实现、数据、checkpoint、preprocessing、metric 或 job failure。

## 执行结果

全部 paired engineering invariants 通过：

- 两条件均完成 `2,070/2,070` steps；
- epoch permutation SHA 完全相同；
- loss 与 gradient norm 全 finite；
- frozen parameter hash 前后不变；
- final confirmation 未访问。

Primary held-out target：

| 条件 | accuracy | mean gold margin (bits/token) |
|---|---:|---:|
| interaction-ambiguous | 0.92460 | +0.15819 |
| interaction-consistent | 0.44246 | -0.01247 |

consistent − ambiguous accuracy=`-0.48214`，paired-bootstrap 95% CI
`[-0.51687,-0.44841]`；gold-margin difference=`-0.17066` bits/token。

Mechanism panel：

| 条件 | group-equal accuracy | full-rule success |
|---|---:|---:|
| interaction-ambiguous | 0.49814 | 0.00000 |
| interaction-consistent | 0.50471 | 0.00000 |

accuracy difference=`+0.00657`，95% CI `[+0.00112,+0.01215]`，但远低于
`+0.05` 门；full-rule-success difference=`0`。

## 结论

`REJECT_IDEA`：当前 synthetic border/key、M2-current、4,096-coordinate、
9.42% injection 的 empirical instantiation 没有学习 intended cross-key XOR rule，
且 primary target 出现强反向结果。禁止追加 roots、改 task/ratio/marker/key/LR/
coordinates/panel 或 metric rescue。

该结果不否定 round1–3 finite theory；它说明“population support 唯一识别规则”
不足以保证当前 neural optimizer/representation 实际选择并实现该 factorized rule。
ambiguous target 的高 accuracy 不能解释为成功 interaction learning，因为其
mechanism panel 仍约为 chance 且 full-rule success 为零。

## 下一步

形成 failure-targeted literature question：当前失败主要指向
“autoregressive model task-specifically 吸收每个 key 的局部视觉条件，而不形成
shared cross-modal factorization”，还是 frozen representation / low-dimensional
trainability ceiling？先检索能区分这两个解释的理论与 direct LVLM evidence，再
选择下一个 `SCIENTIFIC_MECHANISM`；不直接训练新变体。

## 状态

`REJECT_IDEA`

## 证据边界

- 单 paired seed 足以按预注册规则拒绝当前 instantiation，但不能估计普遍 seed
  distribution。
- synthetic marker/key task 不是自然任务分布。
- forced-choice NLL 不是 free generation。
- primary target 反向差异可能来自 key-specific inductive bias、optimization path
  或其他未分解机制；本实验只显示它不能由 successful full XOR rule learning 解释。
