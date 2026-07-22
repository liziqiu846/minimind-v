# Phase 3 v5 代码审计

本审计对应 `phase3-v5`，结论范围是代码路径与冻结协议的一致性，不替代运行时
资源哈希、Smoke、Pilot、Formal 或 CPU bundle 复核。

| 检查项 | 实现证据 | 审计结论 |
|---|---|---|
| Brier 公式 | `brier_metrics.py` 使用 `sum(p^2)-2*p_y+1`，仅在移位后的有效标签上按词元平均 | 通过 |
| 因果错位 | `shifted_valid_positions` 固定使用 `logits[:, :-1]` 对 `labels[:, 1:]` | 通过 |
| 标签掩码 | `caption_template.py` 只保留原描述词元和唯一助手 EOS，其余为 `-100` | 通过 |
| 有图/无像素文本一致 | `runner_common.py` 对同一 `input_ids`、`labels` 先后调用有像素和 `None` 像素评分；没有重新分词 | 通过 |
| M0 不调用图像替换 | M0 分支只构造 `lm_only` 输入且 `image=None`，有图字段由 v5 指标函数保持为 null | 通过 |
| 两个 v5 一级指标 | `PRIMARY_METRICS_V5` 只有 `robust_positive_brier_risk` 与 `visual_semantic_loss` | 通过 |
| 稳健 max 公式 | 正确风险和有图/无图间隔均使用 `max(pos1,pos2)`；严格成功条件使用 `> 0` | 通过 |
| M0 常量规则 | 正确风险来自 LM-only 的稳健 max；视觉增量 0、视觉损失 0.5；有图间隔/成功为 null | 通过 |
| 图片组等权 | 行级结果先按 `(model_id, filename)` 以 float64 平均，再对唯一图片组等权汇总 | 通过 |
| 类别聚合 | 先按 `(model_id, category, filename)` 聚合，五类仅作描述性输出 | 通过 |
| 码长计算 | `audit_description_bits_v5.py` 验证完整 MMS2 字节、SHA、解码身份，正式码长为 `bytes*8+4` | 通过 |
| 失败概率分配 | 固定模型族和压缩族各 0.025、各 20 槽；两族合计 0.05 | 通过 |
| 原始/截断界 | 两类上界均保存 raw/capped；视觉增量下界由 raw 上界换算并另存 raw/capped | 通过 |
| 事后选择披露 | 协议、界结果、报告均设置事后选择状态及 `simultaneous_coverage_claim=false` | 通过 |
| 分片和续跑 | Formal 固定 32 图分片；继续前逐文件清单、哈希、模型、图片、协议及代码清单绑定复核 | 通过 |
| 数据重叠排除 | 资源审计要求 1389 formal 减去冻结 44 图严格等于 1345 certifying 图 | 通过 |
| 结果包 CPU 复核 | v5 verifier 从原始 Brier 行重新计算行指标、图片聚合、类别、两类界和 NLL 摘要 | 通过 |
| v4 兼容 | 共享 runner 默认 `metric_version="v4"`，v4 分支字段不增加；冻结 v4 清单按其源提交验证 | 通过 |
| 禁止训练 | 所有 v5 协议和运行脚本只有评估路径，`training_allowed=false` | 通过 |

v5 指标可能在查看 v4 Formal 数值后确定，所以任何名义界均不得被表述为全新预注册
实验的同时 95% 覆盖保证。未平滑 NLL 仍只作尾部诊断。
