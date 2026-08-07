# XID-01 Round 1 Result

## 当前科学问题

在样本数、视觉边际、语言边际、target 格式匹配且 target combination 都未观察时，
joint support 是否仍可决定 autoregressive loss 能否识别共享 cross-modal
interaction rule？

## 假设

若 shortcut 与 intended interaction 在 observed support 上等价，则低 NLL 不足以
控制 unseen-cell risk；包含共享参数 diagnostic cell 的 support 应打破等价并把规则
迁移到另一个未见组合。

## 本轮实验

证明一个 \(V\in\{0,1\}\)、\(L\in\{a,b,c\}\)、二元 next-token 与二规则 hypothesis
class 的 finite proposition，并用 deterministic exhaustive verifier 检查
`eta=0.05,0.10,0.25`。本轮 0 checkpoint、0 GPU、0 model training，未访问 final
confirmation。

## 判定标准

- **支持**：样本数、两个 factor marginals、target absence 全匹配；diagnostic 与
  target 共享结构参数；redundant minimax lower bound、identifying unique NLL
  minimizer、解析 gap 与 exhaustive output 全部成立。
- **否定**：任一 matching / target-absence invariant 失败，positive 依赖独立 target
  lookup，lower bound/gap 不成立，或 verifier 与解析式冲突。
- **无法判断**：仅限缺失假设或无法区分数学 construction 与 implementation error。

## 执行结果

- Redundant 与 identifying designs 都有 4 个 observations；
  \(V\) counts 都是 `(0:2,1:2)`，\(L\) counts 都是 `(a:2,b:1,c:1)`。
- Target `(1,c)` 在两者中均不存在，但 `V=1` 与 `L=c` 各自都在两者中出现。
- 同一参数 \(\theta\) 同时控制 diagnostic `(0,b)` 与 target `(1,c)`；不是两个独立
  lookup labels。
- Redundant support 上两个 ground-truth worlds 的完整 labelled training
  distribution 相同，\(\mathcal E_0=\{h_0,h_1\}\)。任何随机 learner 的最优
  worst-case target 0–1 error 为 `0.5`。
- Identifying support 上 ground-truth rule 是唯一 NLL minimizer，错误规则 excess
  NLL 与解析式
  \[
  \frac14\log\frac{1-\eta}{\eta}
  \]
  完全一致：`0.7361097 / 0.5493061 / 0.2746531`。
- Redundant exact-minimizer target-NLL diameter 分别为
  `2.9444390 / 2.1972246 / 1.0986123`；identifying diameter 为 0，且 unique
  minimizer 对 unseen target 的 argmax error 为 0。
- 首次运行只遇到 Python 版本不支持 runtime `tuple[...]` alias 的启动错误；仅修正
  类型注解后通过，support、eta、target、公式和判定标准均未改变。

## 结论

本轮在明确 finite setting 中 `PROVEN`：相同 \(N\) 与单模态 marginals 不保证
cross-modal rule identification；由共享结构参数连接的 diagnostic joint-support
cell 可以在 target combination 仍未见时消除 shortcut 等价类。该命题支持
`XID-01` formal object 的一致性，但其 indistinguishability proof 与普通
no-free-lunch 相邻，尚未证明 neural autoregressive LVLM 中存在同一机制。

## 下一步

建立一般 finite-hypothesis target-risk decomposition：把 target approximation、
source-to-target alignment、finite-sample estimation 与 observed-support
interaction-identification diameter 分开，并检查 toy proposition 是否作为严格
特例恢复。

## 状态

`CONTINUE`
