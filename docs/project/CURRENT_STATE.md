# 上海交通大学实习——当前研究状态

**版本：v5**
**日期：2026-08-07**
**定位：项目当前工作状态的最高优先级入口。任何新对话、Codex 任务或阶段三研究决策开始前，先读本文。**

---

## 0. 文档职责与优先级

1. `docs/project/CURRENT_STATE.md`：当前状态最高优先级入口。
2. `docs/theory/VLM泛化理论基线.md`：理论单一事实来源。
3. `docs/project/DECISION_LOG.md`：关键研究决策，只追加历史。
4. `docs/project/EXPERIMENT_REGISTRY.md`：正式实验、审计、commit、状态与结论索引。
5. `docs/project/ACTIVE_RESEARCH_QUESTION.md`：人工冻结的一级科学问题与 Research Envelope。
6. `docs/project/IDEA_REGISTRY.md`：candidate idea 的长期登记与淘汰记录。
7. `docs/project/REVIEW_QUEUE.md`：不停机的异步人工审查队列。
8. `docs/project/AUTONOMOUS_LOOP_STATE.md`：跨调用恢复所需的最小机器状态。
9. `docs/project/NIGHT_POLICY.md`：预授权夜间自治规则。

若聊天记忆与仓库最新文档冲突，以仓库为准。

`NIGHTLY_REPORT_*.md` 只记录过程，不是 canonical state。每个 autonomous research
cycle 结束或出现重要科学状态变化后，必须把可靠状态同步回本文及相应 registry /
decision log，不能让 nightly report 成为更新的“隐藏真实状态”。

---

## 1. 项目总目标

项目主线不变：

\[
\boxed{
\text{LLM 泛化理论拓展到 VLM}
\rightarrow
\text{发现真正影响 VLM 泛化的规律}
\rightarrow
\text{MiniMind-V 验证}
\rightarrow
\text{理论导出训练算法}
\rightarrow
\text{提升真实任务泛化}
}
\]

MiniMind-V 只是低成本验证平台，不能反过来定义理论。

当前仍属于**阶段三**。只有当阶段三得到的理论规律正式用于训练目标、预算分配或模型选择时，才进入阶段四。

---

## 2. 当前已经确认的经验事实

阶段三 P/S 实验稳定暴露出：

\[
\boxed{\text{编码复杂度下降} \not\Rightarrow \text{真实 VLM 泛化改善}}
\]

因此，单纯继续优化 checkpoint 描述长度不足以解释或改善当前问题。

---

## 3. 当前研究对象的边界

任务书要求研究的是一般意义上的 **VLM 泛化**，即模型在未见数据上的表现。

此前“新图像条件泛化”是一个合法、清晰的子问题，但**不能与全部 VLM 泛化等同**。未见数据还可能涉及新图文组合、新问题/指令、新域、组合泛化等。

因此当前阶段不再把项目整体锁死为“只研究新图像泛化”。新图像条件泛化保留为重要子问题和可能的理论落点。

---

## 4. 当前大方向共识：先找 VLM 相比 LLM 真正新增的泛化因素

当前唯一 Active Research Question 是 `XID-01`：

> autoregressive supervision 下，当 language shortcut 与真实 image–text
> interaction rule 在 observed training support 上都能达到低 next-token NLL 时，
> 哪些 support / objective 条件能够识别可迁移规则，并控制 unseen multimodal
> combination risk？

证据级别为 theory `CONCLUSION_CANDIDATE`；真实 LVLM mechanism 尚未验证。
Round4 已冻结并通过 matched-support MiniMind-V pilot 的 data/model/resource
preflight。pilot 只区分 interaction identifiability 与 visual necessity /
conditional entropy explanation，不把新 metric、proxy、gate、audit 或 benchmark
qualification 当成科学机制。

当前不再一头扎进某个单一 proxy 或局部公式。先在任务书大方向下系统比较 VLM 泛化的主要来源。

### 4.1 数据侧

研究图像、文本及图文关系本身如何影响泛化，例如：

- 图文配对质量与噪声；
- 数据多样性、覆盖和共现结构；
- 图像、文本、图文组合的层次化统计结构；
- 域变化、组合变化等 VLM 特有分布因素。

目标不是得出“图像和文本都重要”这种显然结论，而是寻找**可定量、可预测、可用于数据选择或训练的规律**。

### 4.2 模型 / 表示侧

研究 VLM 的跨模态结构是否学到了真正可迁移的联合表示，例如：

- 视觉与语言信息如何融合；
- 模态失衡 / 模态坍塌；
- 跨模态共享表示、组合表示与可迁移结构；
- 为什么某些参数共享或压缩可以减少码长，却不改善真实性能。

### 4.3 训练侧

研究训练算法如何决定 VLM 最终泛化，例如：

- 对具体训练样本的数据依赖；
- 优化稳定性与训练轨迹；
- 正则化、采样和训练目标；
- 能否从泛化理论直接推出新的训练机制。

### 4.4 三条方向的关系

三者不是互斥路线。最终更可能形成：

\[
\boxed{
\text{数据结构}
\rightarrow
\text{模型/表示如何吸收信息}
\rightarrow
\text{训练过程如何形成最终模型}
\rightarrow
\text{泛化}
}
\]

当前任务是先比较三条大方向的科学价值与理论可行性，再决定阶段三主攻点。

---

## 5. CMI / 图像组数据依赖的当前定位

CMI 与图像组数据依赖**没有被否定**，但不再预设为整个项目唯一的第二层主线。

当前定位：

- 它属于**训练侧**的重要理论工具；
- 图像组 CMI 仍可用于研究“模型对具体训练图像身份的依赖”；
- 是否继续作为主攻方向，要和数据侧、模型/表示侧一起比较；
- 不再为了维护 CMI 路线而强行寻找新的单标量 proxy。

---

## 6. 当前 gradient replacement \(D_I\) 路线的正式状态

第一版：

\[
D_I=\sum_t\eta_t^2\|g_t-g_t^{ghost}\|_2^2
\]

经 infra audit 判定：

\[
\boxed{\text{B — MEASUREMENT INFRA CONFOUNDED}}
\]

crossed checkpoint-only pilot 在解耦 model seed / probe seed、增加 shared probes/panels 后，最终仍得到：

\[
\boxed{\text{DI\_MEASUREMENT\_STILL\_UNSTABLE}}
\]

因此正式停止：

\[
\boxed{
\text{图像组 CMI}
\rightarrow
\text{当前 gradient replacement }D_I\text{ 代理}
}
\]

不再增加 panel、probe、step，也不启动正式 rescue training。

这只否定当前具体代理，不否定 CMI、图像组数据依赖或其他信息论/训练稳定性理论。

---

## 7. 本轮理论讨论中形成但尚未升格为主线的内容

本轮讨论过“图像外层 + 条件文本内层”的层次化风险/梯度分解，以及 Neu 类 SGD 信息论工具。

这些内容目前只保留为**候选理论工具 / 基础引理方向**，原因是：

- “VLM 同时受图像和文本影响”本身科学新意不足；
- “固定预算如何分配图片与文本”尚未由任务或现有理论必然导出，不应拍脑袋升格为主线；
- 任何梯度方差、CMI、稳定性量都必须先证明其增加了真正的 VLM 科学内容，而不是重新命名已有理论。

---

## 8. 2026-08-07 autonomous research 对账

昨夜从文献地图生成 5 个初始 candidate，并依次完成低成本理论 gate、冻结 checkpoint
prediction test 和两个符合阶段三规则的 paired training pilot。当前证据支持的状态是：

| Idea | 当前科学状态 | 已排除的精确范围 | 仍然开放 |
|---|---|---|---|
| `XMC-01` | `BRIDGE_REJECTED` | 当前 contrastive/co-occurrence theory 到冻结 autoregressive MiniMind-V semantic-risk statistic 的理论桥 | 跨模态共现结构、谱结构或表示保持机制本身；若未来出现新的生成式风险证明或新 artifact，可重新登记不同 bridge |
| `COMP-01` | `PROXY_REJECTED` | What’sUp 上 caption+EOS NLL binding margin 作为组合绑定和总语义风险排序的 proxy | 跨模态组合绑定机制、其他预先理论化且非语言偏好主导的测量 |
| `VISCOND-01` | `PROXY_REJECTED` | MMStar answer-letter correct-image vs no-pixel margin 作为任务相关视觉条件信息及总风险排序的 proxy | 视觉条件信息影响泛化的机制、其他有构念效度且非事后搜索的操作化 |
| `VISSUP-01` | `INSTANTIATION_REJECTED` | 当前 9.16% rotation instruction、4,096-coordinate M2-current、frozen encoder/adapter 的具体 visual-necessary intervention | 其他有独立理论与反例支持的 objective design、不同合法机制或 richer visual targets |
| `PROJALLOC-01` | `INSTANTIATION_REJECTED` | 当前 frozen-base / hashed-coordinate setting 的 exact `1/4094/1` fixed-total projector allocation | frozen-feature identifiability、其他预注册 module-placement regime、objective mismatch、gradient routing、task-specific absorption |
| `LITMAP-04` | `BRIDGE_REJECTED` | 当前 objective-routing / task-specific-absorption primary literature 到本地唯一、单因素、no-sweep 最小干预的桥 | objective competition、gradient routing、task-specific absorption 与 frozen-feature/objective mismatch 机制本身 |
| `LITMAP-05` | `BRIDGE_REJECTED` | 当前 formal probing/decodability theory、direct LVLM evidence 与 MiniMind-V architecture 到唯一、no-sweep、具有可靠负向排除力的 frozen-feature readout bridge | frozen feature 中存在可读 signal、downstream absorption/transfer failure、objective mismatch、encoder limitation 与其他被独立理论固定的 readout family |
| `COVER-01` | `BRIDGE_REJECTED` | 当前 authoritative broad source/task labels、official/local lineage 与 audited literature 到唯一、no-sweep、单因素 complementary-coverage-versus-redundancy local bridge | coverage/diversity、Vision-Flan task diversity、domain/compositional coverage、source transfer、ALLaVA full lineage 与真正 source-factorial generative experiment |

这些状态不改动任何原始实验结果。历史 result 中的 `REJECT_IDEA` 是当时 autonomous
workflow 的“停止该 candidate 并转向下一路线”判定；其科学外推必须按上表的 failure
level 解读。当前没有证据达到 `MECHANISM_REJECTED`。

两个 paired pilot 的关键负结果：

- `VISSUP-01` root `43101`：held-out rotation 差 `-0.69 pp`，CV-Bench-2D 差
  `-0.14 pp`；不补 roots、不更换 task/ratio/proxy。
- `PROJALLOC-01` root `43201`：rotation 差 `+1.29 pp`，95% CI
  `[-2.08,+4.56] pp`；CV-Bench 差 `-1.39 pp`，margin 差 `-0.05817`；
  六门仅工程配对门通过，不运行 `43202/43203`。

---

## 9. 当前 Active Research Question

> 是否存在由数据发布者预先定义的 crossed multimodal schema：同一
> image/acquisition unit 系统地对应多个 text/task factors，从而在固定视觉来源、
> 质量、难度和 output format 后，唯一构造 baseline cells、complementary crossed
> cells、matched redundancy cells 与一个 held-out crossed cell，用 generative
> VLM prediction 裁决跨模态组合覆盖？

### 本次研究重心切换

- **Previous active question**：`COVER-01` 是否能从 authoritative broad
  source/domain/task labels 与本地 lineage 唯一构造 complementary coverage
  versus same-domain redundancy。
- **Why it was demoted**：442 条 raw records、380 个 unique titles、14 篇决定性
  primary sources 与 official MiniMind/ALLaVA lineage audit 显示，direct generative
  evidence 依赖 ratio/category/target search；LAION/VFLAN 与 broad task labels
  同时改变 acquisition、task、style、quality、difficulty 与 output schema。最干净
  的 source-domain control 只适用于 CLIP，无 autoregressive LVLM risk bridge。
- **New active question**：`CROSSFACT-01` authoritative crossed-cell gate。
- **Evidence motivating the switch**：本地 parquet 虽无 source IDs，但保存的
  169 个官方 ALLaVA captions 全部能以 exact assistant text 映射回 source row；
  因而 decisive failure 不是“lineage 完全不可恢复”，而是 broad source labels
  不正交。固定同一 image/acquisition unit，再 crossing publisher-defined
  text/task factors，是直接针对该混杂的更窄设计。
- **What remains open from the previous question**：coverage/diversity、
  Vision-Flan task diversity、source/domain/compositional coverage、
  source-specific transfer、ALLaVA 全量 ID 恢复与未来真正 factorial 的
  generative-LVLM 实验均开放；只否定当前 broad-label-to-local-single-factor
  bridge。

更完整的 Mission Envelope 与 active-question 历史见
`docs/project/ACTIVE_RESEARCH_QUESTION.md`。

---

## 10. 当前动态 backlog

- **ACTIVE**：`XID-01` cross-modal interaction identifiability。round1–3 theory
  已完成；round4 implementation 与 preflight 已通过，下一步按计划先做二条件
  non-scientific smoke，再运行 root `43301` paired pilot。
- **NEXT**：AR visual-credit competition；cross-modal compositional
  factorization。它们有直接证据与算法出口，但需由 `XID-01` 判断是特例、竞争解释
  还是独立机制。
- **BACKLOG**：joint multimodal support coverage；`OBJ-01`。coverage 是
  interaction identification 的可能数据条件，不预设某 graph statistic；OBJ 不能由
  已失败的 VISCOND proxy 启动。

`CROSSFACT-01` 保留为 `EXPERIMENT_TOOL` artifact，不再以 authoritative schema gate
占据科学主问题。只有 `XID-01` 产生独立理论 prediction 后，crossed-cell design 才
可能作为一种验证工具恢复。

---

## 11. 当前开放假设

1. frozen visual features 可能缺少当前任务可识别信号；
2. 信号可能被模型 task-specifically 吸收，但没有迁移到外部任务；
3. autoregressive token objective 可能造成视觉/语言梯度路由或竞争失衡；
4. objective 与 frozen representation 可能不匹配；
5. 不同、预先固定且有 direct evidence 的 module placement 仍可能有效；
6. 跨模态共现、组合绑定、视觉条件信息与数据覆盖等上位机制仍开放，只是当前
   bridge/proxy/instantiation 不成立。
7. frozen visual representation 可能已经包含 held-out task signal，但当前
   autoregressive objective / downstream module 没有吸收；也可能该信号在
   representation 中确实缺失；`LITMAP-05` 说明当前文献与 architecture 不能用唯一
   readout 区分二者，而不是二者之一已被排除。
8. authoritative domain/mixture/combination coverage 可能比原始样本数更能预测
   未见组合或域的风险；`COVER-01` 只说明 broad source/task labels 不能构成本地
   唯一单因素 bridge。
9. 同一 image/acquisition unit 上 publisher-defined text/task factors 的 crossed-cell
   coverage 可能隔离真正跨模态组合泛化；是否存在 authoritative schema、exact
   lineage 与 generative held-out cell 保留为实验设计问题，不再决定科学机制准入。
10. observed support 上多个低 NLL conditional predictors 可能对应不同的
    cross-modal interaction rules，并在 unseen cells 上产生不同风险；该
    `XID-01` formulation 仍需证明其超出普通 distribution-shift no-free-lunch 的
    VLM-specific 内容。

---

## 12. 当前禁止事项

- 不继续挽救当前 \(D_I\)；
- 不把当前 `BRIDGE_REJECTED`、`PROXY_REJECTED` 或
  `INSTANTIATION_REJECTED` 写成上位 mechanism 已失败；
- 不运行 `VISSUP-01` 的额外 roots，不换 rotation task/ratio/prompt/proxy；
- 不运行 `PROJALLOC-01` 的 `43202/43203`，不搜索 allocation，不恢复旧 sweep；
- 不回到只优化 checkpoint 码长；
- 不制造新的无理论桥 checkpoint proxy；
- 不把 random cluster、embedding neighborhood、事后 benchmark category 或原始
  sample count 直接称为 controlled coverage；
- 不把 LAION/VFLAN、broad dataset/task labels 或非唯一官方 ID 直接当作 factorial
  cell；不搜索 domain pair、mixture ratio、target cell 或 output format；
- 不把 predictor-equivalence diameter 直接实现成 checkpoint proxy；本轮先证明
  formal object 与 prediction；
- 不访问 final confirmation set；
- 不提前宣布进入阶段四。

---

## 13. 仓库与执行状态

- 当前最新 scientific result：`experiments/results/XID-01_round4/RESULT.md`。
  root 43301 valid pilot 强反向：primary consistent−ambiguous=`-48.21 pp`，
  mechanism diff=`+0.66 pp` 且两条件 full-rule success=0。当前 empirical
  instantiation 已拒绝，roots 43302/43303 禁止；round1–3 finite theory 仍仅为
  未获真实 LVLM 验证的 `CONCLUSION_CANDIDATE`。
- Round4 immutable plan commit=`5cbe500`。data/token/pixel/model/resource
  preflight 全通过：两条件 train rows=`11,040`、steps=`2,070`、coordinates=`4,096`；
  pixel/target order、target spans/masks、marginals、per-key entropy 精确匹配，
  paired token records 只在预定 contextual key slot 变化。
- 下一步：冻结 LITMAP-07 failure-targeted search plan，区分 key-specific
  factorization failure 与 representation/trainability ceiling；不直接训练变体。
- `RUNNING_JOB=none`，`HARD_STOP=false`。
- 新增 plans、results、raw receipts、logs 和 SHA manifests 已在
  `EXPERIMENT_REGISTRY.md` 建立 canonical 索引；失败原始证据保留。
- `LITMAP-06` 的 3,479 records、2,395 unique titles、10-source matrix、
  deterministic search index、5/5 DOI verification 与 source hashes 已固化；
  0 GPU/checkpoint/training，未访问 final confirmation。

---

## 14. 新对话启动模板

> 继续上海交通大学实习——VLM 泛化理论项目。先读取
> `docs/project/CURRENT_STATE.md` 和 `docs/theory/VLM泛化理论基线.md`，仓库
> canonical state 优先于聊天与 nightly report。当前仍处于阶段三；五个初始
> candidate 的失败粒度分别是 bridge/proxy/proxy/instantiation/instantiation，
> 后续 `LITMAP-04` 与 `LITMAP-05` 均为 bridge rejection，没有上位 mechanism 被
> 否定；`COVER-01` 也只得到 broad-label bridge rejection。治理纠偏后
> `CROSSFACT-01` 降为 experiment tool；`LITMAP-06` 选择 `XID-01`
> cross-modal interaction identifiability 为 active conjecture。先确认
> `experiments/plans/XID-01_round1.md` 已提交，再执行 finite support theorem、
> proof 与 exhaustive verification。不重跑既有实验，不制造新 proxy，不访问 final
> confirmation set。
