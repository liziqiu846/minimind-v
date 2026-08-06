# XMC-01 Round 1 Result

## 当前科学问题

纯数据层的图文配对误差/共现图，是否在历史 P/S 同预算配对间变化到足以解释性能
排序？

## 假设

P/S 同预算同 seed 使用相同的数据、训练行顺序和图文训练边；若成立，纯数据版本的
`XMC-01` 不能单独解释 P/S 排序。

## 本轮实验

只读比较历史 training manifest 中的数据 SHA、协议、训练规模和每 epoch 实际
permutation SHA。计划 9 个 P/S pair；没有读取性能 proxy、没有 forward、没有训练。

## 判定标准

- 支持：9/9 可审计 pair 的数据图字段与实际 permutation receipt 均一致。
- 否定：任一 pair 存在影响图文训练边的差异。
- 无法判断：关键 manifest/receipt 缺失。

## 执行结果

- 6/9 pair 可完整审计：low/high × seeds 43101/43102/43103。
- 这 6 对的数据 SHA、训练样本数、协议、batch/step 设置和三个 epoch 的实际
  permutation SHA 全部一致。
- 3/9 current-budget pair 的 P/S config 在数据 SHA、train seed、预声明 permutation
  规则和训练设置上全部一致，但仓库缺少对应 training manifest，不能核对实际
  permutation receipt。
- 机器结论：`DATA_GRAPH_IDENTITY_NOT_AUDITABLE`。

## 结论

在已审计的 6 对内，纯数据共现机制不可能解释 P/S 差异；但缺失 3 个 current-budget
回执使全矩阵结论按预注册标准保持无法判断。`XMC-01` 若继续，必须研究冻结模型对
跨模态结构的保持，而不是把相同数据统计重新与性能做相关。

## 下一步

预注册一个 text-bias-controlled、same-word counterfactual forced-choice NLL
checkpoint-only test，联合区分 `XMC-01` 的模型保持版本与 `COMP-01` 的组合绑定机制。

## 状态

`REVIEW_QUEUE`

