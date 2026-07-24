# Phase 3 预算趋势实验：18 模型矩阵

本目录保存相同坐标预算下 M2/M3 公平比较的最终机器可读结果。实验先通过
`low-43101` 严格执行门，再按冻结 manifest 完成其余 10 个模型；12 个新模型
均为 3 epochs、1875 optimizer steps，未重试、未调参、未选择 checkpoint。
6 个 current 模型只读取冻结 v6 回填与已有 MMS2 复杂度结果，没有重新训练。

主要文件：

- `model_summary.csv/json`：18 个模型的实际 archive/description bits 与三类风险；
- `paired_differences.csv/json`：9 个 `M3-M2` 配对差；
- `budget_summary.csv/json`：low/current/high 三根均值、总体标准差和符号一致性；
- `category_summary.csv/json`：SugarCrepe++ 类别级描述统计；
- `plots/`：四张 PNG/PDF 图；
- `run_receipt.json`：统一分析状态与文件哈希；
- `execution/`：第一道门、两轮调度和共享 GPU 授权/显存探针收据；
- `run_records/`：12 个新模型的完整阶段日志、训练/量化/评分收据、MMS2 工件
  及单模型汇总。

逐记录 scorer 输出、图片组风险、训练 checkpoint 和解码坐标未重复提交到 Git；
完整运行工件保存在执行机：

`/home/lizhaohui/lzq/minimind-v-stage2-rerun-20260721/experiments/runs/phase3_risk_v1`

本分析固定为 `certified=false`，正式认证无效原因是
`post_hoc_metric_design` 与 `coupled_mismatch_donors`。探索性 Hoeffding
radius/bound 不认证任何模型的 `visual_risk < 0.5`。
