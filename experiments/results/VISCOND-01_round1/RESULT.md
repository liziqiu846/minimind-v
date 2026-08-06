# VISCOND-01 Round 1 Result

## 当前科学问题

在相同训练数据、坐标预算和 seed 的 MiniMind-V M2/M3 模型中，已有
development-only 总语义风险更高的模型，是否系统性地从任务相关正确图像获得更少
的条件判别增量，而更多依赖同一模型的 no-pixel language prior？

## 假设

若“较差模型更少利用任务相关图像条件”是码长—性能脱钩的主要机制，则在未用于形成
该假设的 MMStar 完整 eligible panel 上，9 个 M2/M3 pair 应稳定满足
`sign(ΔV) = -sign(ΔR)`，且当前模型家族整体应从正确图像像素获得正的答案判别增量。

## 本轮实验

官方 MMStar revision、parquet hash、schema、图片与答案 token gate 均通过。排除 3 个
超过冻结 450-token 上限的题目和 1 个官方缺少 D 选项的题目后，对 1,496 题、1,426
个独立 normalized-pixel groups，以 18 个冻结 MMS2 checkpoint 计算正确图像相对
no-pixel 的 gold-vs-distractor teacher-forced margin 增量 \(V\)。图片组 bootstrap
固定为 10,000 次、seed `20260807`；未训练，未访问 final confirmation set。

## 判定标准

- 支持：pooled \(V\) 的 95% CI 下界大于 0 且至少 12/18 模型为正；同时至少
  7/9 pair 符号一致、至少 5 个预测方向 CI 不跨 0，并满足预注册的预算、正
  `ΔR` pair 与类别门。
- 否定：任一预注册否定项成立；其中 pooled \(V\) 不为正或少于 9/18 模型为正
  直接否定。
- 无法判断：仅限 panel、独立图片组、checkpoint、预处理、metric 或完整运行无法
  通过审计，或恰为 6/9 且没有触发其他否定项。

## 执行结果

- 18/18 模型完成，逐题 raw score 的 SHA-256、checkpoint、panel 与 scoring commit
  均由 analysis receipt 绑定；一次性预注册聚合成功。
- pooled \(V=-0.221182\) bits/token，图片组 bootstrap 95% CI
  `[-0.306740, -0.134830]`；仅 `2/18` 模型的 \(V\) 点估计为正，触发预注册否定。
- pair sign concordance 为 `6/9`，但仅 `4/9` pair 的 CI 在预测方向不跨 0；low、
  current、high 各为 `2/3`，不足以覆盖已触发的构念否定。
- `ΔR>0` 的 4 个 pair 中 `3/4` 有 `ΔV<0`；6 个类别中 5 个的
  prediction-oriented 平均效应为正。这些局部排序信号不能证明 \(V\) 是有效机制，
  因为当前家族总体上正确图像反而降低该操作性答案 margin。
- correct-image forced-choice accuracy 为 `0.2099–0.2934`，no-pixel accuracy 为
  `0.2025–0.3135`，accuracy gain 为 `-0.0869–0.0261`；这与 pooled 负增量一致。
- 18 个 receipt 的评分时间合计 1,929.725 秒，即 0.536 GPU-hour；raw scores 保留
  在 runtime，仓库归档 gate、smoke、日志、summary、decision 与完整 hash receipt。

## 结论

`VISCOND-01` 在当前冻结模型家族和预声明 MMStar answer-letter 构造上被否定：
correct-image 相对 no-pixel 的操作性判别增量既不是当前家族稳定的正向视觉获益，也
不能作为解释总语义风险排序的可靠机制。`6/9` 的局部方向一致不得脱离失败的构念门
升格；不得换 prompt、答案文本、subset、proxy、benchmark 或新增 seed rescue。

\(V\) 仅是操作性视觉条件增量，不是互信息、正式视觉风险、无偏估计量、因果中介或
泛化界。

## 下一步

拒绝依赖 `VISCOND-01` positive gate 的 `OBJ-01` 启动条件；基于三条连续外部
checkpoint prediction 失败与本轮“正确图像总体降低答案 margin”的证据，先进行一次
预注册、定向的一手文献与理论搜索，寻找能区分视觉输入分布失配、视觉 token
训练动力学和跨模态数据覆盖的下一候选，优先选择不复用已失败生成 NLL proxy、且能
由现有 artifact 低成本证伪的机制。

## 状态

`REJECT_IDEA`
