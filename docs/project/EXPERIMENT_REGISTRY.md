# 上海交通大学实习——实验与审计登记表

**版本：v1**  
**日期：2026-08-06**  
**规则：一项正式实验 / 审计一条记录。结果不删除，只更新状态。**

---

## 状态枚举

- `VALID`：可用于当前科学推断。
- `INVALID_FOR_INFERENCE`：原始产物保留，但不得用于科学推断。
- `REJECTED_ROUTE`：路线已被实验否定，不再作为主线。
- `AUDIT_PASS`：工程 / 协议审计通过。
- `PROPOSED`：仅提出，尚未冻结或执行。
- `SUPERSEDED`：被后续更严格实验替代。

---

## 注册表

| 日期 | 名称 | 科学问题 | 分支 / commit | 主要对象 | 结果 | 状态 | 关键产物 / 备注 |
|---|---|---|---|---|---|---|---|
| 2026-07-26 起 | Phase 3 P vs S budget experiment | 私有模块坐标 P 与完全共享坐标 S：共享是否只减少码长，是否损害视觉/语义泛化 | `phase3-private-vs-shared-budget-v1` 相关协议 | P/S × 2048/4096/8192 × 3 seeds；AdamW；MMS2 complexity；语义/视觉指标 | 观察到共享结构常显著减少描述长度，但真实性能并不稳定改善，形成“码长—真实性能脱钩” | `VALID` | 该现象是后续理论主线的主要经验起点。 |
| 2026-08-05 | Shared gradient conflict diagnostic | P/S 脱钩是否由共享坐标上的局部跨模块梯度冲突解释 | commit `422fe05df5dbb188044410675c9aef1355d5b04b` | 同 checkpoint、严格 split shared coordinate、平方 L2/归一化冲突诊断 | 关键预注册解释标准失败；方向预测不优于简单基线 | `REJECTED_ROUTE` | `experiments/results/phase3_shared_gradient_conflict_v1/` |
| 2026-08-06 | Old P/S training-unit audit | 旧协议是否可以把 batch/step 更新解释为图像组数据依赖 | read-only audit | 旧 dataset / sampler / gradient accumulation | 训练统计单位实际是普通 image+canonical conversation pair；存在重复抽样；optimizer step 混合多个 pair | `AUDIT_PASS` | 结论：旧协议不能直接验证 image-group dependence；理论不改，实验重设计。 |
| 2026-08-06 | Phase 3 image-group dependence SGD v1 | 图像组 replacement sensitivity \(D_I\) 是否比 checkpoint 码长更好解释新图像泛化 | branch `stage3-image-group-dependence-sgd-v1`; protocol commit `ea1b58d6d82e12d311975fb1facbb624d611f8de`; codec fix `118a5416bc914d9d4d178e871f63026d97a9291c`; formal results commit `584920421f0e718a9c186d353d704a8ffac003f7` | P/S × {2048,8192} × 3 seeds；plain SGD；10000 unique exact-image groups；11 fixed diagnostic steps；\(D_I=\sum \eta_t^2\|g_t-g_t^{ghost}\|^2\) | 预注册标准 1 PASS；标准 2/3/4 FAIL。但后续发现结构性测量混杂 | `INVALID_FOR_INFERENCE` | 原始 summary 保留。不得用于 P/S 结构推断、\(D_I\)-performance 相关性或理论失败判断。 |
| 2026-08-06 | Phase 3 image-group dependence infra audit | 上一项失败是否由 implementation bug 或 measurement infra 混杂导致 | 基于同一分支 / 现有 12 模型；本地 audit 产物尚待入库 | 诊断实现、probe sampling、step concentration、raw vs MMS2 | 无 implementation bug；probe 跨 seed 改变；probe variation 为 structure variation 5.44–10.44×；top-3 contribution 59.0–80.9%；raw/MMS2 有 1/6 P/S 排序翻转 | `AUDIT_PASS` | 最终分类：**B — MEASUREMENT INFRA CONFOUNDED**。本地 `infra_audit/` 产物需在下一轮前冻结入库。 |
| 2026-08-06 | D_I minimal rescue experiment | 在去除 probe 混杂后，当前 \(D_I\) 是否值得保留为结构解释指标 | 尚未创建正式分支 / commit | 计划：budget=2048；P/S × 3 model seeds；model seed 与 probe seed 分离；共享多个 probe panels；更多 diagnostic steps；raw checkpoint 主性能 | 尚未执行 | `PROPOSED` | 必须先形成 ≤1 页预注册科学设计，冻结具体 panel 数、step 数、成本和停止门槛，再由用户明确批准。 |

---

## Phase 3 image-group dependence SGD v1：机械结果记录

### 原预注册相关结果

- `Spearman(D_I,error) = 0.510490`；
- `Spearman(C(h),error) = 0.524476`；
- 2048 budget 内 `Spearman(D_I,error) = -0.314286`；
- 8192 budget 内 `Spearman(D_I,error) = 0.028571`；
- code/performance-decoupled P/S pairs：K=3，\(D_I\) 方向正确 1/3。

这些数字仅作为**历史描述性记录**。由于 infra audit 已判定 measurement confounded，不能继续作为有效推断证据。

### infra audit 关键结果

同 probe 的 P/S 逐 step \(d_t\) 相关性：

| Budget/seed | Pearson | Spearman |
|---|---:|---:|
| 2048/43101 | 0.9834 | 0.9455 |
| 2048/43102 | 0.9929 | 0.9818 |
| 2048/43103 | 0.9979 | 1.0000 |
| 8192/43101 | 0.9813 | 0.9455 |
| 8192/43102 | 0.9985 | 0.9818 |
| 8192/43103 | 0.9834 | 0.9727 |

probe variation / structure variation：

- 2048：5.44×（raw-L2），9.19×（log-L2）；
- 8192：10.44×（raw-L2），7.95×（log-L2）。

step 集中度：

- 最大单 step 占比：22.9%–52.5%；
- top-3 占比：59.0%–80.9%。

raw / MMS2 对齐：

- 中位数 `|Δperformance| = 3.85e-5`；
- 最大 `|Δperformance| = 2.20e-4`；
- 1/6 P/S pair 排序翻转；
- raw error 下 `Spearman(D_I,error) = 0.2657`。

最终审计分类：

\[
\boxed{\text{B — MEASUREMENT INFRA CONFOUNDED}}
\]

---

## 待补录事项

下一轮正式实验前，应将以下本地审计产物冻结到 GitHub，并把对应 commit 回填到本表：

```text
experiments/results/phase3_image_group_dependence_sgd_v1/infra_audit/infra_audit_summary.json
experiments/results/phase3_image_group_dependence_sgd_v1/infra_audit/diagnosis_steps.csv
experiments/results/phase3_image_group_dependence_sgd_v1/infra_audit/raw_vs_mms2.csv
experiments/results/phase3_image_group_dependence_sgd_v1/infra_audit/raw_development/
experiments/results/phase3_image_group_dependence_sgd_v1/infra_audit/gradient_connectivity.json
```
