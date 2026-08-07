# XID-01 Round 3 — diagnostic-mass prediction theorem

**日期**：2026-08-07
**阶段**：阶段三，`PREDICTION TEST`（theorem validation）
**角色**：`SCIENTIFIC_MECHANISM` 的预测性充分条件
**证据上限**：finite-class theorem 可为 `PROVEN`；真实 LVLM 仍最多为
`CONJECTURE`

## 科学问题

能否从 interaction-diagnostic support 的质量与占比，预先推出一个排除
target-bad shortcut 的阈值，从而严格区分：

1. 增加 observationally redundant samples，只缩小 finite-sample estimation；
2. 增加 diagnostic cross-modal cells，改变 shortcut 与 intended rule 的 population
   identification margin？

## 假设

> 假设 H：若 diagnostic distribution \(Q\) 对每个 target-bad rule 至少提供
> separation \(\gamma\)，ordinary/base distribution \(P_0\) 对 bad rule 的优势不
> 超过 \(\beta\)，则 mixture
> \(P_\lambda=(1-\lambda)P_0+\lambda Q\) 上的 source gap 至少为
> \(\lambda\gamma-(1-\lambda)\beta\)。当该 gap 大于 empirical estimation tolerance
> \(2\alpha_n\) 时，source ERM 不能选择 target-bad rule。

如果该阈值不成立、不是 sharp under stated assumptions，或 redundant support 在
\(\gamma=0\) 时仍能仅靠重复样本获得同样的 worst-case identification guarantee，
则 round2 的 `I` term 没有产生预期新 prediction。

## VLM 特有性

\(Q\) 必须由 cross-modal diagnostic cells 构成：visual-ignoring shortcut 与
intended image–text interaction 对这些 cells 给出不同 target-token distribution。
若 \(Q\) 只增加普通 IID 样本或 language-only evidence，则 \(\gamma\) 不应被解释为
cross-modal separation。

通用 mixture algebra 不是 VLM-specific；VLM-specific prediction 是：

> 在相同总预算下，能够区分 language shortcut 与 image–text interaction 的样本质量
> 和占比决定 identification margin，非诊断冗余不能由样本量本身替代。

## Formal setup

令 \(h^\star\in\mathcal H\) 为 intended rule，定义 target-bad set

\[
\mathcal B_\tau
=
\{h\in\mathcal H:
R_U(h)-R_U(h^\star)>\tau\}.
\]

对每个 \(h\in\mathcal B_\tau\)，假设

\[
R_0(h)-R_0(h^\star)\ge-\beta
\]

和

\[
R_Q(h)-R_Q(h^\star)\ge\gamma,
\]

其中 \(\beta\ge0,\gamma>0\)。令 loss bounded in \([0,B]\)，source mixture 为
\(P_\lambda\)。

## 可证伪预测

定义

\[
\alpha_n(\delta)
=
B\sqrt{\frac{\log(2|\mathcal H|/\delta)}{2n}}.
\]

预期 theorem：

\[
\lambda\gamma-(1-\lambda)\beta>2\alpha_n
\]

等价于

\[
\lambda>
\frac{\beta+2\alpha_n}{\beta+\gamma},
\]

且该条件蕴含 source ERM \(\widehat h\notin\mathcal B_\tau\)，即

\[
R_U(\widehat h)-R_U(h^\star)\le\tau
\]

with probability at least \(1-\delta\)。

Sharpness prediction：在只知道上述 \((\beta,\gamma)\) bounds 时，若
\(\lambda\gamma-(1-\lambda)\beta\le2\alpha_n\)，应能构造满足 uniform-deviation
event 的 empirical risks，使某个 target-bad rule 与 \(h^\star\) tie 或优于它；
因此阈值不能在无额外假设下普遍放宽。

Round1 specialization：

- identifying support：
  \(\beta=0,\lambda=1/4,\gamma=\log((1-\eta)/\eta),\alpha=0\)，应恢复 positive
  source gap \(\gamma/4\)；
- redundant support：对 bad rule 的 diagnostic separation 为 \(\gamma=0\)，即使
  \(n\to\infty\) 也没有 strict identification guarantee。

## 最小研究

1. 写 theorem、proof、sharpness construction 与 inference boundary；
2. deterministic verifier 穷举固定 rational grid：
   - \(\beta\in\{0,1/4,1/2\}\)；
   - \(\gamma\in\{1/4,1/2,3/4,1\}\)；
   - \(\alpha\in\{0,1/8,1/4\}\)；
   - \(\lambda\in\{0,1/4,1/2,3/4,1\}\)；
   - admissible base/diagnostic bad-rule gaps on quarter grid；
3. 对 theorem-positive cases 检查所有 admissible gaps 均排除 bad ERM；
4. 对 threshold-negative cases 检查 worst-case
   \(\Delta_0=-\beta,\Delta_Q=\gamma\) 与 extremal empirical deviations 可使 bad
   rule remain ERM；
5. 解析恢复 round1 三个 eta 和 redundant \(\gamma=0\) limit。

## 判定标准

### 支持

- population mixture gap lower bound、high-probability ERM exclusion 和 threshold
  equivalence均有完整 proof；
- threshold sharpness construction 在 stated assumptions 下成立；
- fixed grid 全部 theorem-positive 与 threshold-negative cases 无 violation；
- round1 specialization 精确恢复；
- 明确 separation \(\gamma\) 的 cross-modal operational meaning，但不把任一具体
  empirical proxy 声称为 \(\gamma\)。

### 否定

- mixture lower bound 或 ERM exclusion 不成立；
- threshold algebra 有 counterexample；
- sharpness construction 需要违反 bounded loss / uniform deviation event；
- redundant \(\gamma=0\) 在相同 assumptions 下仍得到 strict worst-case guarantee；
- round1 identifying source gap 不能恢复。

### 无法判断

仅限 bounded-risk realization 或 measurability 条件缺失且无法在本轮补足。
Threshold 只是一项充分条件、暂不可在 MiniMind-V 直接估计，属于 inference
boundary，不是 `INCONCLUSIVE`。

## 可能混杂

- 把 sufficient threshold 写成 necessary condition；
- 把 \(\gamma\) 当成无需构念验证的 checkpoint metric；
- 忽略 base support 可能偏好 shortcut 的 \(\beta\)；
- 把增加 \(n\) 降低 \(\alpha_n\) 与增加 \(\lambda\) 提高 population margin 混淆；
- 用 target set 定义 bad rules 后在 final confirmation 上反复选择 intervention；
- theorem 通过后直接启动未隔离 \(\lambda,\gamma,\beta\) 的训练。

## 所需资源

- GPU / checkpoint / training：`0`；
- CPU：固定 finite rational grid，预计小于 1 分钟；
- final confirmation：不访问；
- 网络/数据：无；
- 磁盘：小于 2 MB。

## 冻结声明

本计划提交后才写 theorem/proof 或运行 verifier。执行后不得更改 parameter grids、
strict inequality、sharpness criterion、round1 mapping 或判定标准。实现 bug 可最小
修复；数学 counterexample 必须否定或收窄 theorem，不得搜索另一阈值。
