# 上海交通大学实习——实验与审计登记表

**版本：v2**  
**日期：2026-08-06**  
**规则：一项正式实验 / 审计一条记录。结果不删除，只更新状态。**

---

## 状态枚举

- `VALID`：可用于当前科学推断。
- `INVALID_FOR_INFERENCE`：原始产物保留，但不得用于科学推断。
- `REJECTED_ROUTE`：路线已被实验否定，不再作为主线。
- `AUDIT_PASS`：工程 / 协议审计通过。
- `PROPOSED`：仅提出，尚未冻结或执行。
- `SUPERSEDED`：被后续更严格实验或决策替代。

---

## 注册表

| 日期 | 名称 | 科学问题 | 分支 / commit | 主要对象 | 结果 | 状态 | 关键产物 / 备注 |
|---|---|---|---|---|---|---|---|
| 2026-07-26 起 | Phase 3 P vs S budget experiment | 私有模块坐标 P 与完全共享坐标 S：共享是否只减少码长，是否损害视觉/语义泛化 | `phase3-private-vs-shared-budget-v1` 相关协议 | P/S × 2048/4096/8192 × 3 seeds；AdamW；MMS2 complexity；语义/视觉指标 | 观察到共享结构常显著减少描述长度，但真实性能并不稳定改善，形成“码长—真实性能脱钩” | `VALID` | 该现象是后续理论主线的主要经验起点。 |
| 2026-08-05 | Shared gradient conflict diagnostic | P/S 脱钩是否由共享坐标上的局部跨模块梯度冲突解释 | commit `422fe05df5dbb188044410675c9aef1355d5b04b` | 同 checkpoint、严格 split shared coordinate、平方 L2/归一化冲突诊断 | 关键预注册解释标准失败；方向预测不优于简单基线 | `REJECTED_ROUTE` | `experiments/results/phase3_shared_gradient_conflict_v1/` |
| 2026-08-06 | Old P/S training-unit audit | 旧协议是否可以把 batch/step 更新解释为图像组数据依赖 | read-only audit | 旧 dataset / sampler / gradient accumulation | 训练统计单位实际是普通 image+canonical conversation pair；存在重复抽样；optimizer step 混合多个 pair | `AUDIT_PASS` | 结论：旧协议不能直接验证 image-group dependence；理论不改，实验重设计。 |
| 2026-08-06 | Phase 3 image-group dependence SGD v1 | 图像组 replacement sensitivity \(D_I\) 是否比 checkpoint 码长更好解释新图像泛化 | branch `stage3-image-group-dependence-sgd-v1`; protocol commit `ea1b58d6d82e12d311975fb1facbb624d611f8de`; codec fix `118a5416bc914d9d4d178e871f63026d97a9291c`; formal results commit `584920421f0e718a9c186d353d704a8ffac003f7` | P/S × {2048,8192} × 3 seeds；plain SGD；10000 unique exact-image groups；11 fixed diagnostic steps；\(D_I=\sum \eta_t^2\|g_t-g_t^{ghost}\|^2\) | 预注册标准 1 PASS；标准 2/3/4 FAIL。但后续发现结构性测量混杂 | `INVALID_FOR_INFERENCE` | 原始 summary 保留。不得用于 P/S 结构推断、\(D_I\)-performance 相关性或理论失败判断。 |
| 2026-08-06 | Phase 3 image-group dependence infra audit | 上一项失败是否由 implementation bug 或 measurement infra 混杂导致 | 基于同一分支 / 现有 12 模型；本地 audit 产物尚待远端确认 | 诊断实现、probe sampling、step concentration、raw vs MMS2 | 无 implementation bug；probe 跨 seed 改变；probe variation 为 structure variation 5.44–10.44×；top-3 contribution 59.0–80.9%；raw/MMS2 有 1/6 P/S 排序翻转 | `AUDIT_PASS` | 最终分类：**B — MEASUREMENT INFRA CONFOUNDED**。`infra_audit/` 远端目录截至 v2 仍未发现。 |
| 2026-08-06 | D_I minimal rescue experiment | 在去除 probe 混杂后，当前 \(D_I\) 是否值得保留为结构解释指标 | 未进入正式训练 | 原计划：budget=2048；P/S × 3 model seeds；shared panels；更多 steps；raw checkpoint 主性能 | 正式 rescue 未执行；在冻结 K/T 前先由 crossed checkpoint-only pilot 检查测量稳定性，pilot 已触发停止当前 D_I proxy 的条件 | `SUPERSEDED` | 不再启动正式 rescue training，不再通过继续增加 panel/probe/step 挽救当前 \(D_I\)。 |
| 2026-08-06 | Phase 3 D_I crossed checkpoint-only pilot v1 | 修复 probe identity 混杂后，当前 gradient replacement sensitivity 的测量是否稳定到足以支持正式 rescue | Codex 报告本地 commit `b1205ae42bb2af2e0658d440d90799db3ed43ced`；截至 v2 GitHub 远端未解析到该 commit | budget=2048；6 raw checkpoints；3 shared panels × 33 probes；594 diagnoses；model/probe seed 解耦 | identity audit PASS；增加 K/T 明显降低 CV 与贡献集中，但 T=33 ICC raw/log=0.084/0.160，最低 P/S bootstrap 符号保持率=0.497，seed 43101 跨 panel 发生 P/S 方向翻转；结论 `DI_MEASUREMENT_STILL_UNSTABLE` | `VALID` | 该 pilot 可用于停止“当前 D_I 作为 P/S/CMI 主代理”的路线，但不能解释为 CMI 理论失败。报告目录：`experiments/results/phase3_di_crossed_probe_pilot_v1/`，远端截至 v2 未发现。 |

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

## Phase 3 D_I crossed checkpoint-only pilot v1：关键结果

### Shared-probe audit

- 3 panels × 33 probes = 99 个 panel/slot；
- 六模型间 train/ghost group、图像 hash、conversation hash、预处理与选中位置逐项一致；
- identity audit：`PASS`。

### K/T 稳定性

probe/structure ratio（raw）：

- T=11：K=1/2/3 为 `0.520 / 0.406 / 0.341`；
- T=22：`1.231 / 0.900 / 0.743`；
- T=33：`1.372 / 0.996 / 0.815`。

probe/structure ratio（log）：

- T=11：`0.528 / 0.391 / 0.325`；
- T=22：`0.961 / 0.695 / 0.566`；
- T=33：`1.036 / 0.742 / 0.609`。

随着 T=11→22→33：

- bootstrap CV：`0.084–0.194 → 0.070–0.119 → 0.059–0.106`；
- 最大单 probe contribution：`12.3%–26.6% → 7.3%–14.5% → 5.7%–10.2%`；
- top-3 contribution：`36.0%–48.3% → 21.1%–28.3% → 16.2%–23.7%`。

说明更多 probe / panel 能降低测量方差和贡献集中，但没有解决核心 P/S 符号稳定性。

### 跨 panel 稳定性

T=33：

- ICC(A,1)：raw `0.084`，log `0.160`；
- panel Pearson：raw `0.775–0.836`，log `0.880–0.933`；
- panel Spearman：raw `0.771–0.943`，log `0.829–0.943`；
- 最低 P/S bootstrap 符号保持率：T=11/22/33 为 `0.566 / 0.584 / 0.497`；
- seed 43101：`P>S / P<S / P>S`；
- seed 43102、43103：三个 panel 均为 `P<S`。

最终结论：

\[
\boxed{\text{DI\_MEASUREMENT\_STILL\_UNSTABLE}}
\]

因此不冻结正式 K/T，不进入 formal rescue。

---

## 待补录 / 远端同步事项

截至 v2，通过 GitHub 远端接口尚未发现：

```text
experiments/results/phase3_image_group_dependence_sgd_v1/infra_audit/
experiments/results/phase3_di_crossed_probe_pilot_v1/
```

Codex 报告 crossed pilot 本地 commit：

```text
b1205ae42bb2af2e0658d440d90799db3ed43ced
```

但该 SHA 截至 v2 未能由远端 GitHub 解析。

**下一次正式实验前必须先完成上述必要证据的 push / freeze，并把真实远端 commit 回填本表。**
