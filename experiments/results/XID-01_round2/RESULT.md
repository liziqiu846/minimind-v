# XID-01 Round 2 Result

## 当前科学问题

能否把 target approximation、source-target alignment、exact interaction
identification 与 finite-sample estimation expansion 分开，并严格恢复 round1？

## 假设

Finite bounded-loss class 的 source ERM 高概率属于 population near-minimizer set；
其 target excess risk由四个非负项上界，其中 exact-source-minimizer target diameter
是 interaction-identification 的理论位置。

## 本轮实验

证明 finite-class target-risk decomposition，并在 3 hypotheses、risk grid
`{0,1/4,1/2,3/4,1}`、deviation radii `{0,1/4,1/2}` 上穷举所有满足 uniform
deviation event 的 source/empirical/target tables 和全部 empirical minimizers。
另解析恢复 round1 的三个固定 eta；0 checkpoint/GPU/training。

## 判定标准

- **支持**：四项非负、proof 完整、fixed grid 无 violation、round1 special case
  精确恢复，并明确通用与 VLM-specific 部分。
- **否定**：algebra、ERM membership、任一 grid case 或 round1 specialization
  失败，或 identification term 不能与 alignment 分离。
- **无法判断**：仅限缺失 boundedness/measurability 条件或数学/实现错误无法区分。

## 执行结果

- 由 Hoeffding + finite-class union bound，以至少 \(1-\delta\) 概率
  \(\widehat h\in\mathcal E_{2\alpha_n}\)，其中
  \[
  \alpha_n=B\sqrt{\frac{\log(2|\mathcal H|/\delta)}{2n}}.
  \]
- 对所有 source ERM：
  \[
  R_U(\widehat h)-R_U^\star
  \le
  A_U+B_{S\to U}+I_{S\to U}+G_{S\to U}(2\alpha_n).
  \]
- `A` 是 target approximation；`B` 是 best exact source minimizer 的 target
  alignment penalty；`I` 是 exact source minimizers 内的 target-risk diameter；
  `G` 是 finite-sample near-minimizer set 相对 exact set 的 target expansion。
- Exhaustive verifier 检查 `1,147,625` 个有效 target-table cases 和
  `1,530,375` 个 empirical-ERM cases，violations=`0`。
- Round1 redundant case 精确恢复
  `A=B=G(0)=0`、`I=log((1-eta)/eta)`；identifying case 恢复四项全为 0。
- 因此 round1 diagnostic support 消除的是 exact identification diameter，不是
  approximation、marginal exposure 或 target leakage。

## 结论

该 finite-hypothesis decomposition 为 `PROVEN`，并使 `XID-01` 从 toy
construction 上升为结构清楚的 theory-bridge candidate；但 algebra 与 uniform
convergence 本身是通用 learning theory，VLM-specific 内容只在 source exact
minimizers 同时包含 visual-ignoring shortcut 与 cross-modal rule 时出现。由于各项
使用 \(R_U\)，它不是可计算的 held-out certificate，也不证明真实 LVLM mechanism。

## 下一步

执行 prediction-theorem validation：预先定义 diagnostic distribution \(Q\) 对
target-bad shortcuts 的 separation \(\gamma\)、base support 对 shortcut 的最大优势
\(\beta\) 与 diagnostic mass \(\lambda\)，证明阈值
\(\lambda(\gamma+\beta)>\beta+2\alpha_n\) 时 source ERM 排除 target-bad rules；
这将直接区分“增加冗余样本只缩小 estimation”与“增加 interaction-diagnostic
support 改变 identification margin”。

## 状态

`CONTINUE`
