# 上海交通大学实习——当前研究状态

**版本：v4**
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

> MiniMind-V 当前训练数据及可在本服务器取得的 authoritative source data 中，是否
> 存在无需新 proxy、由来源语义唯一固定的 domain / mixture / multimodal-combination
> strata，使“增加互补覆盖”相对“增加同域冗余”能够形成单因素、可证伪且可在当前
> 资源内验证的 VLM 泛化 prediction？

### 本次研究重心切换

- **Previous active question**：`LITMAP-05` 是否存在 architecture/theory 唯一
  固定的 frozen-feature readout，可区分 representation-absent 与
  downstream-unabsorbed。
- **Why it was demoted**：553 条 raw records、491 个 unique titles 与 13 篇决定性
  primary sources 的完整核查显示，formal quantities 都依赖研究者事先选择
  predictive family、target distribution 或 regularization；最直接的 LVLM studies
  也需要 layer/token/pooling/learning-rate 选择或 max-over-layer。MiniMind-V 只固定
  SigLIP2 `last_hidden_state` 的位置，没有固定 task readout 或 negative
  completeness。
- **New active question**：`COVER-01` authoritative controlled-coverage gate。
- **Evidence motivating the switch**：连续两次 training instantiation 与两次
  literature bridge 均无法无歧义定位 representation/objective failure；相比继续
  制造 probe，数据来源已有的 domain/mixture/combination labels 更可能提供不依赖
  checkpoint proxy 的受控科学对象。
- **What remains open from the previous question**：frozen-feature signal、
  downstream absorption/transfer failure、objective mismatch、encoder limitation
  及 linear/nonlinear decodability 均未被机制性否定；只否定当前
  identifiability bridge。

更完整的 Mission Envelope 与 active-question 历史见
`docs/project/ACTIVE_RESEARCH_QUESTION.md`。

---

## 10. 当前动态 backlog

- **ACTIVE**：`COVER-01` authoritative controlled-coverage gate。先建立并提交
  immutable literature/data-interface plan；提交前不执行新 scientific analysis、
  checkpoint inference 或训练。
- **NEXT**：尚未登记可执行 candidate。`COVER-01` 只有在 authoritative strata、
  single-factor contrast、held-out prediction 与 local feasibility 同时通过时才允许
  选择一个 coverage candidate。
- **BACKLOG**：`OBJ-01`。它不能由已失败的 `VISCOND-01` positive gate 启动；
  `LITMAP-04` 也没有提供合法最小 objective bridge。该上位假设仍开放，但不是可直接
  训练 candidate。

`LITMAP-05` 已按 immutable gate 作出 `NO_CANDIDATE` /
`BRIDGE_REJECTED`。下一步先提交 `COVER-01_round1` immutable plan，再核查
authoritative domain/mixture labels、现有数据 lineage 与唯一 controlled-coverage
contrast；不得把数据量、随机 cluster 或事后 embedding 分组换名为 coverage。

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
   未见组合或域的风险；但是否存在可用于本地单因素实验的可靠 strata 尚待
   `COVER-01` 审计。

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
- 不访问 final confirmation set；
- 不提前宣布进入阶段四。

---

## 13. 仓库与执行状态

- 当前最新 scientific result：`experiments/results/LITMAP-05_round1/RESULT.md`
  （`NO_CANDIDATE` / `BRIDGE_REJECTED`，由本次 result commit 冻结）。
- 下一 immutable plan：`experiments/plans/COVER-01_round1.md`，尚待创建并提交。
- `RUNNING_JOB=none`，`HARD_STOP=false`。
- 昨夜新增 plans、results、raw receipts、logs 和 SHA manifests 已在
  `EXPERIMENT_REGISTRY.md` 建立 canonical 索引；失败原始证据保留。
- `LITMAP-05` 的 result、13-source evidence matrix、deterministic search index、
  local interface audit 与 source hashes 已固化；13/13 决定性来源均可核查。

---

## 14. 新对话启动模板

> 继续上海交通大学实习——VLM 泛化理论项目。先读取
> `docs/project/CURRENT_STATE.md` 和 `docs/theory/VLM泛化理论基线.md`，仓库
> canonical state 优先于聊天与 nightly report。当前仍处于阶段三；五个初始
> candidate 的失败粒度分别是 bridge/proxy/proxy/instantiation/instantiation，
> 后续 `LITMAP-04` 与 `LITMAP-05` 均为 bridge rejection，没有上位 mechanism 被
> 否定。当前 active question 是 `COVER-01` authoritative controlled-coverage
> gate；先创建并提交 immutable plan，不重跑既有实验，不制造新 probe，不访问
> final confirmation set。
