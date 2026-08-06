# VISSUP-01 Round 1 Result

## 当前科学问题

visually necessary rotation supervision 是否能相对等 pixels / labels / compute 的
文本泄露 control 改善 held-out rotation 与新外部 CV-Bench-2D？

## 假设

若 caption-only 监督没有迫使当前低维 MiniMind-V 吸收视觉结构，则
visual-necessary condition 应同时改善预注册机制量和外部 vision-centric 指标。

## 本轮实验

按 immutable plan 先下载并 hash 官方 `nyu-visionx/CV-Bench` revision
`bc284db50d036958861cb60cdd7b77612052ce0d` 的 README、tree 与 2D parquet，只做
pre-model schema gate。没有实现 scorer、没有训练、没有运行任何模型输出。

## 判定标准

- 支持：完整官方 2D panel 可确定性规范化为计划写死的 `A/B/C/D` 四选一后，才可
  继续 paired pilot。
- 否定：本轮尚未进入科学效应判定。
- 无法判断：官方 schema 不满足四选一门时记为 `PANEL_INELIGIBLE`，不得丢题或
  就地改计划。

## 执行结果

- parquet SHA-256 与官方 LFS oid 一致：
  `33196034ef4bf3265cae4a7ff5c4071b2ff1cc21123e8e285c6a91393897ecbc`；
- 完整 2D split 有 1,438 rows：Count 788、Relation 650；
- 选项数为 2 选 650 题、4 选 493 题、5 选 156 题、6 选 139 题；
- gold label 包含 A–F，其中 E 63 题、F 23 题；
- 因而“每题恰为 A/B/C/D”不成立，触发 `PANEL_INELIGIBLE`；
- 训练次数 `0`，模型评分次数 `0`，GPU 用时 `0`，未访问 final confirmation。

## 结论

round1 没有回答 VISSUP 科学假设；它只发现了在模型运行前可证实的外部 metric/schema
confound。不能删除 945 个非四选一题，也不能改写 round1 后继续。

## 下一步

使用本 candidate 唯一一次合法 rescue，创建并 commit `VISSUP-01_round2`：
保留全部 1,438 rows，按每题官方 2–6 个 options 计算 variable-choice NLL；训练
intervention、panel、primary accuracy/margin 和全部效应阈值不变。

## 状态

`CONTINUE`
