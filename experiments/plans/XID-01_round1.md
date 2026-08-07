# XID-01 Round 1 — finite autoregressive interaction-identifiability theorem

**日期**：2026-08-07
**阶段**：阶段三，`EXPLORATION MODE`
**角色**：`SCIENTIFIC_MECHANISM` 的理论刻画
**证据上限**：有限 toy setting 中可为 `PROVEN`；对真实 LVLM 最多为
`PROOF_SKETCH` / `CONJECTURE`，不得外推为已验证规律

## 科学问题

能否定义一个不依赖 checkpoint proxy 的 autoregressive interaction-identifiability
对象，并在最小 finite problem 中证明：

> 两个训练设计具有相同样本数、视觉边际、语言边际、target 格式和 hypothesis
> class，且同一个 target combination 在二者中都未出现；但只有包含
> interaction-diagnostic cell 的设计能够区分 language shortcut 与 intended
> cross-modal rule，并正确预测该 unseen target combination？

## 假设

> 假设 H：autoregressive observed-support NLL 只在训练支持上约束条件预测器。
> 若两个规则在该支持上 observationally equivalent，它们可具有相同训练 NLL 而在
> unseen multimodal cells 上产生不同风险；加入一个由同一结构参数控制、能使两规则
> 分歧的 diagnostic cell，可以缩小规则等价类并识别另一个未见组合。

如果在保持样本数、两个 factor marginals、target unseen 和无 label leakage 的条件
下无法构造上述对照，或者 positive 结论只能通过把 target label 作为无结构的独立
lookup 硬编码进 hypothesis class，则当前 `XID-01` formulation 至少在本轮不成立。

## VLM 特有性

输入由视觉 factor \(V\) 与语言/任务 factor \(L\) 组成。竞争规则必须包括：

1. 一个忽略 \(V\) 的 target-prior / language-side shortcut；
2. 一个由共享结构参数控制、只在特定 \(V\times L\) 组合激活的 interaction rule。

两个训练设计都必须暴露 target cell 的每个单独 factor value；差异只能是 joint
support 是否包含另一个由同一 interaction 参数控制的 diagnostic combination。
普通单 token-sequence IID 样本数或单边际覆盖不能表达这个差异。

## 候选正式对象

对 hypothesis class \(\mathcal H\)、observed distribution \(P_S\) 与 tolerance
\(\epsilon\)，定义 near-minimizer equivalence set：

\[
\mathcal E_\epsilon(P_S)
=
\{h\in\mathcal H:
R_S(h)\le \inf_{g\in\mathcal H}R_S(g)+\epsilon\}.
\]

对未见 target distribution \(P_U\)，定义 target interaction diameter：

\[
\operatorname{Diam}_U(\mathcal E_\epsilon)
=
\sup_{h,g\in\mathcal E_\epsilon}
|R_U(h)-R_U(g)|.
\]

本轮只判断该对象能否精确刻画 finite counterexample。不得把它实现成新的 empirical
checkpoint score，也不得称为 mutual information。

## 最小 finite construction

- \(V\in\{0,1\}\)，\(L\in\{a,b,c\}\)，binary next token \(Y\)；
- shared interaction parameter \(\theta\in\{0,1\}\)；
- rule
  \[
  f_\theta(v,l)=
  \begin{cases}
  \theta,&(v,l)\in\{(0,b),(1,c)\},\\
  0,&\text{otherwise};
  \end{cases}
  \]
- \(\theta=0\) 是忽略图像的 constant-token shortcut；\(\theta=1\) 是同一
  cross-modal interaction 在两个组合上的共享规则；
- 为使 NLL 有限，\(h_\theta\) 给 \(f_\theta(v,l)\) 概率 \(1-\eta\)，给另一 token
  概率 \(\eta\)，固定 \(0<\eta<1/2\)；
- redundant design \(P_R\) 使用四个 observations：
  \((0,a),(1,b),(0,c),(1,a)\)；
- identifying design \(P_I\) 使用四个 observations：
  \((0,b),(1,a),(0,c),(1,a)\)；
- 两者的 \(V\) marginals 都是 `(2,2)`，\(L\) marginals 都是 `(a:2,b:1,c:1)`；
- target \(P_U\) 是两者均未观察的 \((1,c)\)。

`P_I` 中 `(1,a)` 的重复是固定样本数与 factor marginals 所需的
observationally-redundant observation，不可事后替换。

## 可证伪预测

1. **Redundant support**：在 \(P_R\) 上，\(\theta=0\) 与 \(\theta=1\) 产生完全相同
   的 training labels 与 NLL；在两种 ground-truth worlds 间，任何 learner 对
   target \((1,c)\) 的 worst-case 0–1 error 至少为 \(1/2\)。
2. **Identifying support**：在 \(P_I\) 上，ground-truth \(\theta\) 是
   \(\{h_0,h_1\}\) 中唯一 NLL minimizer；错误规则的 population/empirical NLL gap
   为
   \[
   \frac14\log\frac{1-\eta}{\eta}.
   \]
   识别出的 \(\theta\) 应在未见 target \((1,c)\) 上给出正确 argmax token。
3. `P_R` 与 `P_I` 必须由独立 exhaustive enumerator 验证样本数、两个 marginals、
   target absence、label tables、NLL gap、equivalence-set diameter 和 minimax
   lower bound。

## 最小研究

1. 写出 definitions、proposition、proof 与 inference boundary；
2. 实现一个只枚举上述 finite state space 的 deterministic verifier；
3. 以至少三个固定 \(\eta\) 值（`0.05, 0.10, 0.25`）核查解析 NLL gap；
4. 保存 machine-readable result 与 source/script SHA。

本轮不读取 checkpoint、不运行 GPU、不训练 MiniMind-V，也不访问 final
confirmation。

## 判定标准

### 支持

必须同时满足：

- 两设计的样本数、\(V\) marginals、\(L\) marginals 和 target absence 完全匹配；
- interaction parameter 在 diagnostic 与 target cells 间共享，而非两个无关 lookup
  labels；
- redundant support 上训练分布对两个 worlds 完全相同，并证明 worst-case target
  error 下界；
- identifying support 上 unique NLL minimizer、解析 gap 与 unseen-target transfer
  同时成立；
- exhaustive output 与解析式对三个 \(\eta\) 全部一致。

支持只建立 toy proposition。真实 LVLM 的 rule class、optimization bias 与
approximation error 仍未验证。

### 否定

以下任一项触发当前 formulation 的 `REJECT_IDEA` 或重写为更弱问题：

- 两训练设计不能同时匹配样本数和两个 factor marginals；
- target 或其完整 combination 实际进入 identifying training support；
- positive result 依赖独立编码 target label，而非共享 interaction parameter；
- redundant minimax lower bound 或 identifying NLL gap 不成立；
- exhaustive verifier 给出反例或与解析结果不一致，且不是 implementation bug。

### 无法判断

仅限：

- proposition 需要尚未写明且无法在本轮审计的假设；
- verifier 无法区分 mathematical construction error 与 implementation error。

“命题太简单”“尚未覆盖真实网络”不是 `INCONCLUSIVE`，而应成为严格 inference
boundary 与下一轮问题。

## 可能混杂

- 把普通 OOD no-free-lunch 换名为 VLM theory；
- 通过任意 lookup table 把 target answer 硬编码进 rule class；
- matching marginals 时意外改变样本数或 factor exposure；
- 把 unique ERM 当成 gradient training 一定找到正确模型；
- 把 finite hypothesis-class identification 外推到 neural LVLM；
- 把 target diameter 当作无需验证构念效度的 empirical proxy。

## 所需资源

- GPU / checkpoint / model training：`0`；
- CPU：有限枚举，预计小于 1 分钟；
- final confirmation：不访问；
- 新数据下载：无；
- 磁盘：小于 1 MB。

## 冻结声明

本计划必须先 commit，之后才写 theorem/proof 或运行 verifier。执行后不得改变
construction、\(\eta\) set、support cells、判定标准或 target cell来适配结果；若
数学 construction 失败且不是 implementation bug，按否定标准处理，而不是搜索新的
cell table。
