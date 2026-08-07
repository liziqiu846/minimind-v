# XID-01 Round 3 Result

## 当前科学问题

interaction-diagnostic support 的 separation 与占比，能否产生一个排除 target-bad
shortcut 的预声明阈值，并区分 population identification 与 sample-count
estimation？

## 假设

若 diagnostic support 至少以 \(\gamma\) 偏好 intended rule，而 ordinary support
最多以 \(\beta\) 偏好 shortcut，则 mixture identification margin 至少为
\(\lambda\gamma-(1-\lambda)\beta\)；该 margin 超过 \(2\alpha_n\) 时，source ERM
不能是 target-bad rule。

## 本轮实验

证明 diagnostic-mass threshold 与 worst-case sharpness proposition；在冻结的
3×4×3×5 parameter grid 上检查全部 admissible quarter-grid gaps，并解析恢复
round1 三个 eta 与 redundant \(\gamma=0\) limit。0 checkpoint/GPU/training。

## 判定标准

- **支持**：mixture lower bound、ERM exclusion、threshold equivalence、
  worst-case sharpness、fixed grid 与 round1 mapping 全部成立。
- **否定**：任一 algebra/counterexample、sharpness 违反 bounded/uniform-deviation
  条件、redundant support 获得同等 strict guarantee，或 round1 无法恢复。
- **无法判断**：仅限 bounded-risk realization / measurability 条件无法补足。

## 执行结果

- 对 target-bad \(h\)，population mixture gap 满足
  \[
  R_\lambda(h)-R_\lambda(h^\star)
  \ge
  \lambda\gamma-(1-\lambda)\beta.
  \]
- 若
  \[
  \lambda>
  \frac{\beta+2\alpha_n}{\beta+\gamma},
  \]
  则以至少 \(1-\delta\) 概率，source ERM 的 target excess relative to
  \(h^\star\) 不超过预声明 \(\tau\)。
- 当 lower margin \(\le2\alpha\) 时，构造的 bounded population/empirical risks
  满足 uniform-deviation event，同时让 target-bad rule tie 或优于 intended rule；
  因而阈值在仅有 \((\beta,\gamma,\alpha)\) 信息时 worst-case sharp。
- Fixed verifier 检查 180 parameter cases、2,700 admissible gap cases：
  68 个 threshold-positive cases 全通过；112 个 threshold-negative cases 均有
  sharpness construction；violations=`0`。
- Round1 identifying case 精确映射为
  \(\beta=0,\lambda=1/4,\gamma=\log((1-\eta)/\eta),\alpha=0\)，恢复 source gap
  `0.7361097 / 0.5493061 / 0.2746531`。
- Redundant \(\gamma=0,\beta=0\) 在
  `alpha=0,0.125,0.25` 下均无 strict identification guarantee。

## 结论

diagnostic-mass prediction theorem 与 sharpness result 在 finite setting 中
`PROVEN`。它给出 `XID-01` 的首个方向明确、非事后相关的算法预测：训练预算应购买
能区分 shortcut 与 intended interaction 的 separation，而不只是重复样本；当 base
support 偏好 shortcut 时，asymptotic diagnostic-mass threshold 为
\(\beta/(\beta+\gamma)>0\)。真实 LVLM 中 \(\beta,\gamma\) 尚无经验证的 estimator，
因此机制仍不能宣称已确认。

## 下一步

冻结一个 MiniMind-V paired pilot：构造两组总样本数、visual/language/target
marginals、pixels、target format、steps 和 trainable coordinates 完全匹配的
synthetic cross-modal task；只改变 joint support 是 shortcut-equivalent 还是包含
interaction-diagnostic cells，并在两组都未见的 target combination 上评分。该训练
必须明确区分 interaction-identifiability 与 marginal exposure / label-frequency
解释，先 1 个 paired seed。

## 状态

`CONCLUSION_CANDIDATE`
