# 上海交通大学实习——实验与审计登记表

**版本：v3**
**日期：2026-08-07**
**规则：一项正式实验 / 审计一条记录。结果不删除，只更新状态。**

---

## 状态枚举

- `VALID`：可用于当前科学推断。
- `INVALID_FOR_INFERENCE`：原始产物保留，但不得用于科学推断。
- `REJECTED_ROUTE`：路线已被实验否定，不再作为主线。
- `AUDIT_PASS`：工程 / 协议审计通过。
- `PROPOSED`：仅提出，尚未冻结或执行。
- `SUPERSEDED`：被后续更严格实验或决策替代。
- `PROXY_REJECTED`：实验有效，但只否定当前经验 proxy 的构念或预测效度。
- `BRIDGE_REJECTED`：理论审计有效，但只否定当前 theory-to-LVLM bridge。
- `INSTANTIATION_REJECTED`：实验有效，但只否定当前具体实现 / 干预 / 参数化。
- `MECHANISM_REJECTED`：只有核心机制预测被直接检验且主要竞争解释受控时使用。

历史 `REJECTED_ROUTE` 保留用于既有记录；新记录必须采用有科学作用域的 failure
level。result 文件中的 `REJECT_IDEA` 是 workflow disposition，不自动等价于
`MECHANISM_REJECTED`。

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
| 2026-08-07 | XMC-01 round1 P/S data-graph identity audit | 纯数据图文共现结构是否在同预算 P/S 间变化到足以解释性能排序 | plan commit `1624428`; result commit `1c3678c` | 历史 P/S 9 个预算/seed pair 的 config、training manifest、dataset/permutation receipt | 可完整审计的 6/9 pair 数据 SHA 与每 epoch permutation SHA 全相同；3 个 current-budget pair config 一致但缺 training manifest；结论 `DATA_GRAPH_IDENTITY_NOT_AUDITABLE` | `AUDIT_PASS` | 可用于冻结“纯数据 XMC 不能解释已审计 6 对 P/S”；不得外推到缺失的 3 对，也不证明模型保持机制。`experiments/results/XMC-01_round1/` |
| 2026-08-07 | LITMAP-01 VLM mechanism evidence map | VLM 相比 LLM 新增的泛化因素中，哪些数据/表示/训练机制同时具有理论、实验与算法出口 | plan commit `ba55681`; map commit `c68b2d0`; close commit `ddfe8c5` | 4 组 scoping map；OpenAlex/arXiv/targeted primary sources | 形成 `XMC-01`、`COMP-01`、`VISCOND-01`、`OBJ-01`、`COVER-01` 五个初始 candidate；不构成任何 mechanism 结论 | `VALID` | `docs/project/literature/night_20260807/`; `docs/project/NIGHTLY_REPORT_20260807.md` 仅为过程日志 |
| 2026-08-07 | COMP-01 round1 external binding prediction test | caption+EOS NLL 四格 margin 能否表示组合绑定并预测 M2/M3 总语义风险排序 | plan `ca9496e`; result `887778c` | 18 frozen checkpoints；完整 What’sUp 410 relation pairs；205-cluster bootstrap | sign concordance `5/9`，预测方向 CI `1/9`；95.37%–99.76% pairs 两图偏好同一 caption，proxy 被语言偏好主导 | `PROXY_REJECTED` | 只否定当前 caption-NLL binding proxy，不否定跨模态组合绑定机制。`experiments/results/COMP-01_round1/` |
| 2026-08-07 | XMC-01 round2 autoregressive model-retention bridge audit | 是否存在可唯一固定 frozen autoregressive MiniMind-V statistic 并连接 unseen semantic risk 的正式 bridge | plan `7540cf7`; result `ab30fda` | 13 篇 primary paper 正文/appendix 与 theorem applicability matrix | 最强结果止于 contrastive retrieval/linear probe、linear-Gaussian dual encoder 或机制性 UFM；本地量仍需 layer/pooling/kernel/rank/proxy 选择 | `BRIDGE_REJECTED` | 只否定当前理论桥，不否定跨模态共现/表示保持机制。`experiments/results/XMC-01_round2/` |
| 2026-08-07 | VISCOND-01 round1 MMStar visual-increment prediction test | correct-image vs no-pixel answer margin 能否作为视觉条件利用与总风险排序 proxy | plan `9b39317`; result `c67bde0`; logs `bdd330d` | 官方 MMStar 1,496 eligible items、1,426 image groups；18 frozen checkpoints | pooled \(V=-0.2212\) bits/token，95% CI `[-0.3067,-0.1348]`；仅 `2/18` 为正；pair concordance `6/9` | `PROXY_REJECTED` | 只否定当前 answer-letter visual-increment proxy；不否定视觉条件信息机制。`experiments/results/VISCOND-01_round1/` |
| 2026-08-07 | LITMAP-02 failure-driven visual-supervision gate | 三条 checkpoint route 失败后，是否有 direct autoregressive-LVLM evidence 支持一个唯一最小训练 candidate | plan `d6e1646`; result `2423086` | 568 records / 532 unique titles；6 篇决定性 primary sources | 选择 `VISSUP-01`；其他多-head/loss/layer 方案因需要额外选择而未进入本地首测 | `VALID` | `experiments/results/LITMAP-02_round1/` |
| 2026-08-07 | VISSUP-01 round1 external schema gate | 预注册 CV-Bench scorer 是否适配官方 variable-choice schema | plan `20a67bb`; result `267c8ec` | 官方 CV-Bench 2–6 choices schema；模型运行前 audit | 原固定四选项 scorer 不适配；0 training / inference；允许唯一 schema rescue，其他设计冻结 | `SUPERSEDED` | `experiments/results/VISSUP-01_round1/`; round2 只修正 per-row A–F scorer |
| 2026-08-07 | VISSUP-01 round2 paired pilot | visual-necessary rotation instruction 能否优于 label-revealed control，学习 held-out rotation 并迁移 CV-Bench | plan `5045a4d`; preflight `fa6cafa`; smoke `69f7d9f`; result `d24ce25`; coordinates `499dfa1` | root `43101`；2 conditions × 2,064 steps；1,008 held-out rotation；1,438 CV-Bench images | rotation 差 `-0.69 pp`，95% CI `[-3.77,+2.28] pp`；CV-Bench 差 `-0.14 pp`；paired engineering gates 通过 | `INSTANTIATION_REJECTED` | 只否定当前 9.16% rotation / 4,096-coordinate / frozen encoder-adapter instantiation；不补 roots。`experiments/results/VISSUP-01_round2/` |
| 2026-08-07 | LITMAP-03 low-dimensional visual-trainability gate | VISSUP 失败后，优先检验 frozen identifiability、module allocation 还是 objective routing | plan `c48135f`; result `3e85125` | 541 records / 480 unique titles；11 篇 primary sources；本地 4,096-coordinate feasibility audit | 文献方向冲突但支持 module trainability 是可干预对象；选择唯一 fixed-total `PROJALLOC-01`，不运行旧 sweep | `VALID` | `experiments/results/LITMAP-03_round1/` |
| 2026-08-07 | PROJALLOC-01 round1 paired pilot | 固定总 4,096 coordinates 时，projector-dominant allocation 能否改善视觉吸收与外部泛化 | plan `2bfec22`; implementation `487c81a`; preflight `ac936dc`; smoke `6676b42`; result `376f7de` | root `43201`；current `582/2327/1187` vs exact `1/4094/1`；相同 data/steps/scorers | rotation 差 `+1.29 pp`、95% CI `[-2.08,+4.56] pp`；CV-Bench 差 `-1.39 pp`、margin 差 `-0.05817`；六门仅工程门通过 | `INSTANTIATION_REJECTED` | 只否定当前 frozen-base / hashed-coordinate exact allocation；禁止 `43202/43203` 与 allocation search。`experiments/results/PROJALLOC-01_round1/` |
| 2026-08-07 | LITMAP-04 objective-routing / task-specific absorption gate | 是否有 direct autoregressive-LVLM primary evidence 支持一个不重复失败路线的唯一最小干预 | plan `fe957d8`; result `872657d` | 555 raw records、523 unique titles；14 篇决定性 primary sources；objective competition、gradient routing、task-specific absorption、frozen-feature/AR-objective mismatch | direct mechanisms 与 controls 存在，但所有本地路线均依赖额外 component、teacher/tokenizer/head、proxy、loss/layer/rank/ratio 选择、multi-stage schedule 或超出资源；无法唯一形成 single-factor no-sweep 干预，结论 `NO_CANDIDATE` | `BRIDGE_REJECTED` | 只否定当前 literature-to-local-minimal-intervention bridge，不否定上位训练动力学机制。`experiments/results/LITMAP-04_round1/` |
| 2026-08-07 | LITMAP-05 frozen-feature sufficiency / identifiability gate | 是否有 architecture/theory 唯一固定的 frozen-feature readout，可区分 representation-absent 与 downstream-unabsorbed | plan `2c4f8bb`; result this commit | 553 raw records、491 unique titles、58 prior-search duplicates、45 heuristic score≥10；13 篇决定性 primary sources；exact SigLIP2→64-token projector-input interface | formal theory 需要 analyst 选择 predictive family/target/regularization；direct LVLM studies 需要 layer/token/pooling/LR 或 max-over-layer selection；本地 architecture 不固定 task readout，负 probe 无 completeness；`NO_CANDIDATE` | `BRIDGE_REJECTED` | 只否定当前 frozen-feature identifiability bridge，不否定 feature signal、downstream absorption、objective mismatch 或 encoder limitation。`experiments/results/LITMAP-05_round1/` |
| 2026-08-07 | COVER-01 authoritative controlled-coverage gate | 是否存在 source-defined authoritative strata 与 exact local lineage，可形成 complementary-coverage vs same-domain-redundancy 的唯一单因素 contrast | current plan commit | direct generative VLM/LVLM controlled-mixture evidence、formal adjacent theory、official dataset schemas/licenses、current MiniMind-V manifests | immutable plan 由本次 commit 冻结；round1 只执行 literature/data-lineage/local-interface gate，0 checkpoint/GPU/training | `PROPOSED` | `experiments/plans/COVER-01_round1.md`；支持后才允许登记一个 training candidate 并另建 plan |

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

## 既往远端同步事项：已核对

2026-08-07 对账确认：

- commit `b1205ae42bb2af2e0658d440d90799db3ed43ced` 是当前 `HEAD` 的 ancestor；
- `origin/stage3-image-group-dependence-sgd-v1` 包含该 commit；
- `experiments/results/phase3_image_group_dependence_sgd_v1/infra_audit/` 与
  `experiments/results/phase3_di_crossed_probe_pilot_v1/` 均存在于当前仓库。

因此 v2 的“下一次正式实验前待完成”事项已关闭。远端 default branch 是否已合并不
改变当前本地 canonical evidence；如需发布到其他分支，属于独立仓库发布事项。
