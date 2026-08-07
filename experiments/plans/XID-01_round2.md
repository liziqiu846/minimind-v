# XID-01 Round 2 — target-risk decomposition with identification diameter

**日期**：2026-08-07
**阶段**：阶段三，`EXPLORATION MODE`
**角色**：`SCIENTIFIC_MECHANISM` 的一般理论桥
**证据上限**：finite-hypothesis theorem 可为 `PROVEN`；对 neural LVLM 的适用性
最多为 `PROOF_SKETCH` / `CONJECTURE`

## 科学问题

能否把 round1 的 finite construction 提升为一个一般 target-risk decomposition，
明确区分：

1. target approximation error；
2. exact source minimizers 与 target optimum 的 alignment error；
3. observed-support interaction-identification diameter；
4. finite-sample estimation 使 near-minimizer set 扩大的额外误差？

该 decomposition 必须说明 round1 diagnostic support 究竟消除了哪一项，而不是把
普通 IID concentration 或 OOD shift 换名为新理论。

## 假设

> 假设 H：对 finite conditional-predictor class 和 bounded next-token loss，source
> ERM 以高概率落入 population source near-minimizer set；其 target excess risk
> 可以分解为 target approximation、source-target alignment、exact
> interaction-identification diameter 与 estimation-induced set expansion。

如果 decomposition 只能通过把待证明的 target risk 原样定义成单个“identification
term”，无法区分 alignment 与 within-equivalence-class variation，或者 round1
redundant/identifying cases不能作为严格特例恢复，则当前理论桥失败。

## VLM 特有性

一般 concentration lemma 本身不是 VLM-specific。VLM-specific 内容必须位于：

- \(\mathcal H\) 中同时存在忽略视觉输入的 language-side shortcut 与使用
  \(V\times L\) interaction 的规则；
- source exact minimizers 在 observed multimodal support 上等价，但 target
  multimodal cells 上风险不同；
- interaction-diagnostic support 缩小 exact minimizer set，从而降低
  within-equivalence target diameter。

若 theorem 删除这些对象后没有任何可区分的 interaction term，则只能标为通用
`THEORY_TOOL`，不能作为机制结论。

## 候选定义

令 loss \(\ell\in[0,B]\)，finite \(\mathcal H\)，source/target risks 为
\(R_S,R_U\)，source exact/near-minimizer sets 为

\[
\mathcal E_\epsilon
=
\{h:R_S(h)\le \inf_{g\in\mathcal H}R_S(g)+\epsilon\}.
\]

定义：

\[
A_U(\mathcal H)
=
\inf_{h\in\mathcal H}R_U(h)-R_U^\star,
\]

\[
B_{S\to U}
=
\inf_{h\in\mathcal E_0}R_U(h)-\inf_{h\in\mathcal H}R_U(h),
\]

\[
I_{S\to U}
=
\sup_{h\in\mathcal E_0}R_U(h)-\inf_{h\in\mathcal E_0}R_U(h),
\]

以及 estimation-induced expansion

\[
G_{S\to U}(\epsilon)
=
\sup_{h\in\mathcal E_\epsilon}R_U(h)
-
\sup_{h\in\mathcal E_0}R_U(h).
\]

这些是理论诊断对象，不是可直接从 held-out/final confirmation 反复估计的 model
selection score。

## 可证伪预测

设 \(\hat h\) 为 source empirical ERM，样本数 \(n\)，置信度
\(\delta\)，且

\[
\alpha_n(\delta)
=
B\sqrt{\frac{\log(2|\mathcal H|/\delta)}{2n}}.
\]

预期以至少 \(1-\delta\) 概率：

\[
R_U(\hat h)-R_U^\star
\le
A_U+B_{S\to U}+I_{S\to U}
+G_{S\to U}(2\alpha_n).
\]

同时：

- round1 redundant support 在 population/infinite-sample limit 应具有
  \(A=B=G=0\)、\(I>0\)；
- round1 identifying support 应具有 \(A=B=I=G=0\)；
- 一般 finite grid 上，只要 uniform-deviation event 成立，所有 empirical ERM 都
  必须满足 bound。

## 最小研究

1. 写 formal theorem、proof 和 assumptions；
2. 写 deterministic verifier，穷举：
   - \(|\mathcal H|=3\)；
   - source、target、empirical risks 取固定 grid
     `{0, 0.25, 0.50, 0.75, 1.0}`；
   - fixed deviation radii `{0, 0.25, 0.50}`；
   - 对所有满足 uniform-deviation event 的 tables 和所有 empirical minimizers
     检查 near-minimizer membership 与 target bound；
3. 解析恢复 round1 三个 eta 的 redundant/identifying decomposition；
4. 保存 theorem、machine-readable verification summary、script/source SHA。

本轮不读取 checkpoint、不运行 GPU、不训练模型、不访问 final confirmation。

## 判定标准

### 支持

必须同时满足：

- 四项定义非负且分别对应 approximation、alignment、exact identification 与
  finite-sample expansion；
- high-probability ERM membership 与 target bound 有完整 proof；
- fixed exhaustive grid 对所有有效 cases 无 violation；
- round1 redundant/identifying specializations精确恢复预期项；
- 明确说明哪些步骤是通用 learning theory，哪些结构才是 VLM-specific。

支持最多建立一个理论 bridge lemma，不证明真实 LVLM mechanism。

### 否定

任一情况触发 `REJECT_IDEA` 或降级为纯 `THEORY_TOOL`：

- 某项并非非负或 decomposition algebra 不成立；
- uniform-convergence event 不足以推出 ERM membership；
- exhaustive grid 存在数学 counterexample；
- round1 不能作为特例恢复；
- 所谓 interaction-identification term 实际混入 approximation/alignment，无法解释
  diagnostic support 改变了什么。

### 无法判断

仅限 theorem 依赖未声明 measurability/boundedness 条件，或 verifier 无法区分数学
与实现错误。定理过于基础或暂不可计算应写进 inference boundary，不自动记为
`INCONCLUSIVE`。

## 可能混杂

- 用 target risk 定义的 decomposition 被误称为可计算 certificate；
- 把 finite \(\mathcal H\) union bound 直接套到神经网络；
- 把 source-target alignment 与 within-source-minimizer ambiguity 混在一起；
- 把 estimation radius 当作独立 additive target error，而没有 shift assumptions；
- 用 round1 supplied correct rule 掩盖 approximation error；
- 因 algebra 正确就宣称论文级新 theorem。

## 所需资源

- GPU / checkpoint / training：`0`；
- CPU：固定 finite grid，预计少于 2 分钟；
- final confirmation：不访问；
- 新数据/网络：无；
- 磁盘：小于 2 MB。

## 冻结声明

本计划必须先 commit，之后才写 theorem/proof 或 verifier。执行后不得更改 risk grid、
deviation radii、term definitions、判定标准或 round1 specialization 来适配结果。
实现 bug 可最小修复；数学 counterexample 必须按否定标准处理。
