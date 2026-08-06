# COMP-01 Round 1 Result

## 当前科学问题

在相同训练数据、预算和 seed 的 MiniMind-V M2/M3 模型中，较差的 development-only
总语义风险是否对应更弱的外部组合关系绑定？

## 假设

若组合绑定是码长—性能脱钩的主要解释，则 9 个 M2/M3 pair 应满足
`sign(ΔG) = -sign(ΔR)`，并跨 budget、seed 和 relation family 稳定。

## 本轮实验

在完整 What’sUp controlled panel 的 820 张 annotation 引用图片上构造 410 个
opposing-relation pair；对 18 个冻结 MMS2 checkpoint 计算 caption+EOS teacher-forced
mean NLL 四格和 binding margin。主量为 410 个 pair 的等权均值；95% percentile
bootstrap 以 205 个官方四图对象组为 cluster，每组先平均两个 relation-pair 差，
10,000 次，seed `20260807`。

## 判定标准

- 支持：至少 7/9 符号一致、至少 5 个预测方向 CI 不跨 0、各 budget 至少 2/3
  一致、`ΔR>0` pair 至少 75% 有 `ΔG<0`、至少两个 relation family 支持。
- 否定：任一预注册否定项成立；其中 sign concordance ≤5/9 直接否定。
- 无法判断：仅限 panel、checkpoint、预处理、metric 或运行完整性无法通过审计。

## 执行结果

- panel、checkpoint、deterministic smoke 与 18/18 完整评分均通过；未访问 final
  confirmation set。
- sign concordance 为 `5/9`，触发预注册否定标准。
- 只有 `1/9` pair 的 95% cluster-bootstrap CI 在预测方向不跨 0；支持门槛为 5。
- budget concordance：low `1/3`、current `3/3`、high `1/3`。不能只保留 current
  budget。
- `ΔR>0` 的 4 个 pair 中有 3 个 `ΔG<0`，达到 75%；三个 relation family 的
  prediction-oriented 均值也均为正，但这些局部条件不能覆盖联合支持标准和已触发
  的否定项。
- 18 个模型的 \(G\) 范围仅为 `[-0.002962, 0.002952]` bits/token，image accuracy
  为 `[0.4927, 0.5110]`，group accuracy 为 `[0.0024, 0.0293]`。
- 进一步从同一预声明四格选择审计可见，`95.37%–99.76%` 的 pair 中两张图偏好同一
  caption；这与强加性语言偏好、很弱的图像关系判别一致。它是 planned
  group/image-accuracy 混杂解释，不构成新 proxy。

## 结论

`COMP-01` 在当前冻结模型家族与标准外部 panel 上被否定：生成式关系 binding
margin 不能跨预算/seed 稳定预测已有总语义风险排序。current budget 的局部一致不
得升格为规律，也不允许通过换 panel、换 proxy、挑 budget 或追加 checkpoint 来
rescue。

## 下一步

转向 `XMC-01` model-retention bridge：先做定向权威/前沿文献与理论适用性 gate，
寻找不依赖生成 caption 语言偏好的冻结表示 prediction test；若不能形成严格、未
查看且有区分力的最小实验，则拒绝该 bridge 并转向 `VISCOND-01`。

## 状态

`REJECT_IDEA`
