# Phase 3 风险分化实验基础设施 v1

本目录扩展冻结的 Phase 3 v6 评分结果，不修改候选、contrast hull、
teacher forcing、正确图片或 K=5 错配供体。

## 指标

- `language_risk`：操作性语言风险，`1-q_mismatch_mean`。错配图片仍经过视觉路径，
  因此它不是纯 LLM 风险。
- `visual_risk`：视觉风险，`(1-(q_correct-q_mismatch_mean))/2`。
- `total_semantic_risk`：正确图片条件下的总语义风险，`1-q_correct`。

每条记录必须满足
`total_semantic_risk = language_risk + 2*visual_risk - 1`，绝对误差超过
`1e-6` 时立即失败。

模型主均值以唯一 filename 图片组为单位：先在 filename 内平均记录，再对图片组
等权平均。记录级分布同时输出，但只作描述性统计。

## 当前统计解释

当前 SugarCrepe++ 分析只输出探索性 Hoeffding radius/bound，且固定写入
`certified=false`。它不构成正式固定模型外部认证，原因是：

1. `post_hoc_metric_design`：风险是在观察 v6 结果后确定；
2. `coupled_mismatch_donors`：五轮供体来自同一评估集合的全局错排。

只有未来使用预声明指标、fresh confirmation set 和 independent frozen donor bank
时，`fresh_confirmation_independent_donor_bank` 模式才允许 `certified=true`。

## 复杂度与公平性

实验控制的是 M2 私有坐标总数和 M3 共享坐标数相等，称为“相同坐标预算下的
公平比较”，不称为相同描述长度比较。实际 `archive_bits` 由符号分布和整体
zlib-9 压缩共同决定，是实验输出。

完整描述长度定义为：

`archive_bits + external_selection_bits + external_hyperparameter_bits`

其中 `external_selection_bits=ceil(log2(candidate_family_size))`。MMS2 header
已经包含的模型组、映射根等信息不在外部元数据中重复计数。分模块 entropy 是
量化符号频率的零阶理论估计，不能冒充实际分模块编码长度。

所有 CLI 都支持 `--help`。生成器和结果写入默认拒绝覆盖已有目录。

## 已保存结果

冻结 v6 的风险回填、复杂度审查、统一汇总和图表保存在
[`results/`](results/README.md)。这些结果是探索性集中分析，不是正式外部认证；
18 个新配置仍只有静态 dry-run，没有启动训练。
