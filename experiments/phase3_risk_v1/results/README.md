# Phase 3 风险分化 v1 结果

本目录保存由冻结 Phase 3 v6 输入确定性生成的第一版结果：

- `v6_backfill/record_risks/`：10 个模型、41,070 条逐记录风险；
- `v6_backfill/image_group_risks/`：10 个模型、13,430 个模型内图片组；
- `v6_backfill/model_summaries/`：模型级描述统计与检查；
- `v6_backfill/model_summary.*`、`category_summary.*`：统一机器可读汇总；
- `v6_backfill/exploratory_bounds.json`：探索性 Hoeffding radius/bound；
- `v6_complexity.json`：archive、外部选择、外部超参数及总描述位数；
- `v6_current_summary/`：M2/M3 current 配对表及 PNG/PDF 图表。
- `matrix_dry_run.json`：18 个配置的静态映射与冻结数据检查；
- `current_equivalence.json`：current 映射和 MMS2 codec 新旧等价检查。

当前分析固定为 `current_coupled_post_hoc`，所有模型均为
`certified=false`，正式认证无效原因固定为：

1. `post_hoc_metric_design`
2. `coupled_mismatch_donors`

这些文件不认证 `visual_risk < 0.5`。18 个 low/current/high 配置尚未训练，
因此本目录不包含新训练模型、未来预算的实际编码长度或新评分结果。
