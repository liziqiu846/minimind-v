# 上海交通大学实习——研究决策日志

**版本：v4**
**日期：2026-08-07**
**规则：只追加，不删除历史。每条记录“决定 / 依据 / 后果”。**

---

## 2026-07-25｜阶段三与阶段四边界

**决定**：当前工作继续归属阶段三；只有正式使用阶段三理论结论和认证指标指导训练、预算分配或模型选择时，才进入阶段四。

**依据**：当前仍在建立、验证和筛选理论量及结构规律。

**后果**：后续命名、实验和 Codex 任务不得提前称为阶段四。

---

## 2026-07-25｜理论决定实验

**决定**：任何新实验必须先有一页以内科学设计；理论对象、假设、科学问题、判定标准冻结并经用户确认后，Codex 才能实现和执行。

**依据**：避免旧 DataLoader / sampler 反过来定义理论对象。

**后果**：若现有 MiniMind-V 协议不满足理论统计单位，应改实验协议，不降低理论定义。

---

## 2026-07-26｜P/S 核心科学问题

**决定**：阶段三重点比较私有结构 P 与完全共享结构 S，研究“容量不足还是共享过强”；主要联合考察语义风险、视觉性能和复杂度。

**依据**：共享结构显著缩短码长，但真实性能不稳定改善。

**后果**：码长不再被视为足以解释 VLM 泛化的唯一结构变量。

---

## 2026-08-05｜共享梯度冲突路线停止

**决定**：不再用共享坐标上的局部梯度冲突解释 P/S 脱钩。

**依据**：严格对齐后的诊断未达到预注册解释标准；方向预测不优于简单基线。

**后果**：该路线进入“已否定 / 不再作为主线”。

---

## 2026-08-05｜理论主线转向训练数据依赖

**决定**：在 checkpoint 描述长度之外，引入训练数据依赖 / CMI 作为第二层理论主线。

**依据**：短编码只能给出一侧泛化控制，无法解释 P/S 中“码长更短但真实性能没有更好”的排序脱钩。

**后果**：核心问题转为寻找图像组级训练数据依赖，并把抽象 CMI 推到可计算训练过程量。

---

## 2026-08-06｜旧 P/S 数据协议不适合直接验证图像组依赖

**决定**：停止在旧 pair-level / replacement sampling 协议上把 batch / optimizer-step 更新创新解释为图像组级数据依赖。

**依据**：旧训练单位不是“独立图像组 + 条件文本层次”；optimizer step 混合普通 pair，且存在重复抽样。

**后果**：重新设计 theory-matched 的图像组实验，而不是修改理论去适配旧 DataLoader。

---

## 2026-08-06｜第一版图像组 D_I 实验启动

**决定**：用独立 exact-image 训练组、独立 ghost pool、plain SGD 构造第一版图像组 replacement sensitivity 实验：

\[
D_I=\sum_t\eta_t^2\|g_t-g_t^{ghost}\|_2^2.
\]

**依据**：希望得到比 checkpoint 码长更贴近图像组数据依赖的可计算训练量。

**后果**：完成 P/S × {2048,8192} × 3 seeds，共 12 个模型的预注册实验。

---

## 2026-08-06｜第一版 D_I 预注册结果不得直接解释为理论失败

**决定**：在发现潜在 infra 问题后，不立即以标准 2/3/4 失败否定 \(D_I\) 或 CMI 主线，先做实现与测量审计。

**依据**：总体相关性与 within-budget 结果冲突，怀疑 probe sampling / raw-vs-quantized 对齐问题。

**后果**：暂停理论结案，优先完成 read-only infra audit。

---

## 2026-08-06｜第一版 D_I 正式定性为 B — MEASUREMENT INFRA CONFOUNDED

**决定**：第一版 \(D_I\) 标记为 `INVALID_FOR_INFERENCE`。

**依据**：

1. 未发现 implementation bug；
2. `config_seed` 同时决定模型映射和诊断 train / ghost probe；
3. probe variation 是 structure variation 的约 5.44–10.44 倍；
4. 11-step 诊断中少数 step 占据大部分 \(D_I\)；
5. \(D_I\) 对应 raw checkpoint，而原性能相关分析使用 MMS2 量化后模型，存在 1/6 P/S 排序翻转。

**后果**：

- 保留所有原始结果，不删除；
- 旧 \(D_I\) 不得用于结构比较、性能相关性或理论成败判断；
- CMI / 图像组数据依赖主线继续保留；
- 允许且只允许一次最小、预注册的 \(D_I\) 挽救实验。

---

## 2026-08-06｜主性能对象必须与 D_I 所在模型状态一致

**决定**：后续 \(D_I\) 主相关分析必须使用产生 \(D_I\) 的同一个 raw checkpoint 的 held-out 新图像性能。

**依据**：量化虽平均影响较小，但能改变 P/S 排序并显著改变相关系数。

**后果**：MMS2 只作为独立“量化干预”分析，不再混入 \(D_I\) 主效应判断。

---

## 2026-08-06｜下一步只做 D_I 最小挽救设计，不立即训练

**决定**：先写并冻结一页以内的 D_I 最小挽救实验设计。

**设计方向（当时尚未冻结具体数值）**：

- 只先用 budget=2048；
- P/S × 3 model seeds，共 6 条训练轨迹；
- model seed 与 probe seed 分离；
- 所有模型共享相同多个 probe panels；
- 增加诊断 step 数；
- 保存逐 panel / 逐 step 贡献；
- 检查 panel 方差、ICC/排序稳定性、leave-one-step-out、step 集中度、P/S 方向稳定性。

**停止条件**：若共同 probe、多 panel、更多 step 后 probe variation 仍大于 structure variation，或排序持续由少数 step 支配，则永久停止把当前 \(D_I\) 作为 P/S 结构解释指标。

**后果**：这只否定 `CMI -> 当前 D_I` 这座具体代理桥，不否定上层图像组数据依赖理论。

---

## 2026-08-06｜项目文档成为跨对话同步机制

**决定**：以后不再依赖长对话人工交接。GitHub 文档作为项目状态锚点。

**文档**：

- `docs/project/CURRENT_STATE.md`
- `docs/theory/VLM泛化理论基线.md`
- `docs/project/DECISION_LOG.md`
- `docs/project/EXPERIMENT_REGISTRY.md`

**后果**：任何新对话先读 `CURRENT_STATE.md`；若聊天记忆与仓库文档冲突，以仓库最新文档为准。

---

## 2026-08-06｜正式 rescue 前先做 checkpoint-only crossed diagnostic pilot

**决定**：不直接冻结正式 rescue 的 panel 数 K 和 diagnostic step 数 T；先对现有 budget=2048 的 6 个 raw checkpoints 做一次 crossed diagnostic pilot。

**依据**：原 infra audit 只有 3 个 probe panel，且与 3 个 model seed 一一混杂；11 个 step 又对应不同 \(W_t\) 和 LR 权重。现有数据无法合法估计跨 panel 方差下降率，也无法可靠冻结正式 K/T。

**Pilot 固定设计**：

- 3 个 shared probe panels；
- 每 panel 33 个 probes；
- 6 个 raw checkpoints；
- 总计 594 次 diagnosis；
- model seed 与 probe seed 完全分离；
- 不重训模型、不访问 final confirmation set、不做性能相关性。

**后果**：该 pilot 只用于测量稳定性校准，不被解释为正式 \(D_I\) 或 CMI 泛化证书。

---

## 2026-08-06｜当前 gradient replacement D_I 代理路线停止

**决定**：停止继续使用或挽救当前

\[
D_I=\sum_t\eta_t^2\|g_t-g_t^{ghost}\|_2^2
\]

作为 P/S 结构解释与图像组 CMI 的主要可计算代理。不再增加 panel / probe / step，也不再启动正式 rescue training。

**依据**：crossed pilot 已消除最主要的 probe identity 混杂，并显著改善贡献集中和 CV，但核心结构信号仍不稳定：

1. 99 个 shared probes 的 identity audit PASS；
2. T=33 时 ICC(A,1) 仅 raw `0.084`、log `0.160`；
3. 最低 P/S bootstrap 符号保持率在 T=33 时为 `0.497`；
4. seed 43101 在三个 panel 上出现 `P>S / P<S / P>S` 的方向翻转；
5. 虽然 K 增加会降低 probe/structure ratio，T 增加会降低 CV 和少数 probe 支配，但这些改进没有换来稳定的 P/S 结构方向。

**后果**：

- 当前 `CMI -> gradient replacement D_I` 代理桥停止；
- 不把该结果解释成 CMI / 图像组数据依赖理论失败；
- 项目返回理论层，寻找新的训练过程 / 数据依赖可计算量；
- 下一候选量必须独立于 held-out error，并通过“新科学内容、解释码长—性能脱钩、可导出算法、MiniMind-V 可验证”四项筛选；
- 当前仍处于阶段三。

---

## 2026-08-06｜crossed pilot 与 infra audit 远端同步状态

**决定**：在后续正式实验前，必须确认 crossed pilot 和 infra audit 必要产物已经 push / freeze 到 GitHub，并回填真实远端 commit。

**依据**：Codex 报告 pilot 本地产物位于 `experiments/results/phase3_di_crossed_probe_pilot_v1/`，并报告 commit `b1205ae42bb2af2e0658d440d90799db3ed43ced`；但截至本次文档维护，通过 GitHub 远端接口未能解析该 commit，且未发现 pilot 目录和上一轮 `infra_audit/` 目录。

**后果**：新对话可以依赖文档理解科学结论，但在下一次正式 Codex 实验前，应先完成结果产物的远端冻结，避免“文档已更新、证据未入库”的断层。

---

## 2026-08-06｜阶段三重新上升到任务书大方向筛选

**决定**：不再把 CMI / 图像组数据依赖预设为整个项目唯一的第二层主线。当前先回到任务书要求，从 VLM 泛化的大问题出发，系统比较三类方向：**数据侧、模型/表示侧、训练侧**。

**依据**：

1. 任务书要求的是一般 VLM 在未见数据上的泛化，而“新图像条件泛化”只是其中一个子问题；
2. 当前 gradient replacement \(D_I\) 已停止，说明继续围绕单一 proxy 深挖容易偏离总目标；
3. “图像和文本都影响泛化”或“图片数/每图文本数如何分配”等问题目前不足以自动成为核心创新；
4. VLM 相比 LLM 真正新增的科学内容更可能同时来自多模态数据结构、跨模态表示/模态失衡以及训练过程；
5. 最终目标仍要求从理论自然导出能提升真实泛化的训练算法。

**三条方向**：

- **数据侧**：图文配对质量、数据多样性/覆盖、共现结构、层次化样本结构、域与组合变化；
- **模型/表示侧**：跨模态融合、模态失衡/坍塌、共享与组合表示、结构/压缩为何可能与真实性能脱钩；
- **训练侧**：数据依赖、CMI、稳定性、优化轨迹、正则化、采样与训练目标。

**后果**：

- CMI 保留为训练侧重要理论工具，但不再为了维护该路线强行寻找新 proxy；
- 暂不开新 MiniMind-V / Codex 实验；
- 下一步先以任务书和两篇核心论文为主干，按需补充可靠的新 VLM/CLIP 泛化文献；
- 先回答“**VLM 相比 LLM，泛化问题到底新在哪里？**”，再用“科学新意、解释码长—性能脱钩、可导出算法、MiniMind-V 可验证”四项标准冻结新的阶段三主攻问题。

---

## 2026-08-07｜纯数据共现结构不能单独解释已审计 P/S 配对

**决定**：`XMC-01` 保留为 promising candidate，但其纯数据版本不能作为已审计
P/S 结构排序的解释；后续必须研究冻结模型是否保留任务相关跨模态结构。

**依据**：

1. Zhang et al. 2023 为图文配对语义误差与共现谱提供直接 MMCL 理论桥，但对象是
   spectral contrastive dual encoder + linear probe，不是生成式 LVLM；
2. read-only manifest audit 中，low/high × 3 seeds 共 6 个 P/S pair 的 dataset SHA、
   训练规模和三个 epoch 的实际 permutation SHA 完全一致；
3. current-budget 3 个 pair 的 config 虽一致，但 training manifest 缺失，故全矩阵
   结论按预注册标准为 `DATA_GRAPH_IDENTITY_NOT_AUDITABLE`。

**后果**：

- 冻结“纯数据 XMC 不能解释已审计 6 对 P/S”；
- 不把缺失回执当成默认相同，不宣称 9/9；
- 不对历史结果批量试新 proxy；
- 下一合法 prediction test 应使用冻结 checkpoint、标准外部同词反事实图文对，
  检查模型保持/组合绑定，而不是重新训练。

---

## 2026-08-07｜失败必须按证据粒度分类

**决定**：后续 candidate 失败必须区分
`PROXY_REJECTED`、`BRIDGE_REJECTED`、`INSTANTIATION_REJECTED` 与
`MECHANISM_REJECTED`。具体测试失败不能自动升级为上位机制失败。

**依据**：昨夜多个有效负结果直接裁决的是操作性 proxy、理论适用桥或某个固定
training instantiation，而不是完整机制空间。把 workflow `REJECT_IDEA` 直接写成
mechanism rejection 会比证据实际支持的范围杀掉更多假设。

**后果**：

- `IDEA_REGISTRY.md` 对每个失败 idea 永久记录 failure level、精确排除范围、未排除
  内容、证据、剩余假设空间与下一检索含义；
- 历史 result 中 `REJECT_IDEA` 保持原样，作为当轮停止/转向判定；
- 只有直接检验机制核心预测并控制主要竞争解释后，才允许
  `MECHANISM_REJECTED`。

---

## 2026-08-07｜昨夜五个 candidate 的科学失败作用域

**决定**：

| Idea | Failure level | 精确决定 |
|---|---|---|
| `XMC-01` | `BRIDGE_REJECTED` | 当前 contrastive/co-occurrence theory 到 autoregressive LVLM unseen semantic risk 的桥不成立；不否定跨模态共现机制 |
| `COMP-01` | `PROXY_REJECTED` | caption+EOS NLL binding margin 被语言偏好主导，不能可靠表示组合绑定；不否定组合绑定机制 |
| `VISCOND-01` | `PROXY_REJECTED` | correct-image vs no-pixel answer-letter margin 构念门失败；不否定视觉条件信息机制 |
| `VISSUP-01` | `INSTANTIATION_REJECTED` | 当前 9.16% rotation、4,096-coordinate、frozen encoder/adapter intervention 失败；不否定 objective design 一般作用 |
| `PROJALLOC-01` | `INSTANTIATION_REJECTED` | 当前 exact `1/4094/1` fixed-total hashed-coordinate intervention 失败；不否定其他 module-placement regime |

**依据**：`XMC-01_round2` 的 theorem applicability audit、`COMP-01_round1` 与
`VISCOND-01_round1` 的 frozen-checkpoint prediction tests、`VISSUP-01_round2` 与
`PROJALLOC-01_round1` 的有效 paired pilot 均有冻结判定标准、原始回执和结果归档。

**后果**：当前没有 idea 达到 `MECHANISM_REJECTED`；后续文献搜索与候选生成必须
保留各上位机制的 remaining hypothesis space，同时禁止用换 proxy、换比例、补 seed
或近似变体营救已失败实例。

---

## 2026-08-07｜Active Question 转向 objective routing / task-specific absorption

**决定**：将 fixed-total projector allocation 问题降级，新的 Active Research
Question 进入 `LITMAP-04`：检索 direct autoregressive-LVLM primary evidence，区分
frozen-feature identifiability、task-specific absorption 与 autoregressive objective
competition / gradient routing。

**依据**：

1. `VISSUP-01` 的 visual-necessary instantiation 没有提高 held-out rotation 或
   CV-Bench；
2. `PROJALLOC-01` 在相同总 4,096 coordinates 下增加 projector share 后，rotation
   小幅正点估计未达门且 CI 跨 0，CV-Bench accuracy/margin 反向；
3. 两次失败仍未区分视觉信号未编码、只被 task-specifically 吸收或 objective 对视觉
   梯度路由不利。

**后果**：

- 冻结 `experiments/plans/LITMAP-04_round1.md`；
- 本 gate 不运行 GPU、checkpoint inference 或训练；
- 只有满足 direct evidence、competing-explanation control、唯一最小干预和 no-sweep
  条件时才登记一个新 candidate，否则记录 `NO_CANDIDATE` 并转向新的数据/表示搜索；
- frozen-feature identifiability、其他合法 module-placement regime、objective
  mismatch 与 task-specific absorption 保持开放。

---

## 2026-08-07｜Canonical state 必须同步 autonomous research

**决定**：`CURRENT_STATE.md` 继续作为最高优先级状态入口。每个 autonomous cycle
结束或重要科学状态变化后，必须检查并同步 `CURRENT_STATE.md`、本日志、
`EXPERIMENT_REGISTRY.md`、`IDEA_REGISTRY.md`、`AUTONOMOUS_LOOP_STATE.md`，必要时
同步 `REVIEW_QUEUE.md`。

**依据**：昨夜 nightly report、active-question history 与结果 registry 已领先于
8 月 6 日版本的 `CURRENT_STATE.md`，造成 canonical state 与真实研究状态分叉。

**后果**：nightly report 只作为过程日志；不得保存比 `CURRENT_STATE.md` 更新的
隐藏科学状态。状态同步不删除失败证据，也不改变原始实验结果。

---

## 2026-08-07｜LITMAP-04 objective-routing 本地干预桥被否定

**决定**：`LITMAP-04` 按 immutable gate 判为 `NO_CANDIDATE`，科学 failure
level=`BRIDGE_REJECTED`；不从已核查路线中任挑 component 或超参数启动训练。

**依据**：

1. 五族搜索得到 555 raw records、523 unique titles，完整核查 14 篇决定性 primary
   sources，source hashes 全部通过；
2. direct autoregressive-LVLM mechanism、matched/component controls 与 external
   evidence 数量门通过；
3. 所有本地路线均依赖额外 teacher/tokenizer/head、multi-stage schedule、
   seeing/blind proxy、loss/layer/rank/task/mixture 选择，或超出当前资源；
4. 唯一原本简单的 V-GIFT 路线已经由 `VISSUP-01` 当前 instantiation 有效否定，
   不能换名重试。

**后果**：

- 只否定当前 literature-to-local-minimal-intervention bridge；
- objective competition、gradient routing、task-specific absorption 与
  frozen-feature/objective mismatch 保持开放；
- Active Research Question 切换到 `LITMAP-05` frozen-feature sufficiency /
  identifiability gate；
- 在 immutable plan 提交前不执行新 scientific search/readout；之后也不得 sweep
  layer/rank/pooling/probe/metric。若无唯一 readout bridge，转入 controlled
  coverage gate。

---

## 2026-08-07｜LITMAP-05 frozen-feature identifiability bridge 被否定并转向 COVER-01

**决定**：`LITMAP-05` 按 immutable gate 判为 `NO_CANDIDATE`，科学 failure
level=`BRIDGE_REJECTED`。Active Research Question 切换为 `COVER-01`
authoritative controlled-coverage gate。

**依据**：

1. 五族冻结检索得到 553 raw records、491 unique titles，完整核查 13 篇决定性
   primary sources；source hashes 与 deterministic index rebuild 均通过；
2. predictive \(\mathcal V\)-information、DIB 与
   representational-similarity decoding theory 都需要 analyst 预先选择 predictive
   family、target distribution 或 regularization；
3. 最直接 LVLM studies 仍遍历 layer/token/pooling/LR 或使用 max-over-layer，
   negative finite probes 没有 completeness/impossibility guarantee；
4. MiniMind-V architecture 只固定 SigLIP2 `last_hidden_state` 与 64-token
   projector input，不固定 task readout、regularization、metric 或负向排除边界。

**后果**：

- 只否定当前 formal theory + direct evidence + local architecture 到唯一
  frozen-feature readout 的 bridge；
- frozen-feature signal、downstream absorption/transfer、objective mismatch、
  encoder limitation 与 independently justified readout families 保持开放；
- 禁止通过 layer/token/pooling/classifier/rank/metric sweep 反向制造 bridge；
- `COVER-01` 首先审计 authoritative source-defined domain/mixture/combination
  strata、exact data lineage、single-factor contrast、held-out prediction 与本地
  资源可行性；plan 提交前不执行新的 scientific analysis，不访问 final
  confirmation。

---

## 2026-08-07｜COVER-01 broad-label coverage bridge 被否定并转向 CROSSFACT-01

**决定**：`COVER-01` 按 immutable gate 判为 `NO_CANDIDATE`，科学 failure
level=`BRIDGE_REJECTED`。Active Research Question 切换为 `CROSSFACT-01`
authoritative crossed-cell gate；在其独立 immutable plan commit 前不执行新分析。

**依据**：

1. 五族冻结检索得到 442 raw records、380 unique titles，完整核查 14 篇决定性
   primary sources；deterministic index fresh-temp rebuild byte-identical；
2. Vision-Flan、MM1/MM1.5、DCVLR 与近年的 mixture-optimization work 提供 direct
   generative data-composition evidence，但均把 coverage 与 task/source/style/quality/
   difficulty/output format 同时改变，或需要 ratio/category/target search；
3. DomainNet controlled study 以 matched sizes、source-defined domains/classes 和
   three seeds 提供最干净 evidence，但认证对象是 CLIP zero-shot classification，
   没有到 autoregressive LVLM risk 的 bridge；
4. local `pretrain_i2t.parquet` 的 size/SHA-256 与官方 MiniMind revision/tree
   完全一致。虽然 schema 无 ID，保存的 169 个 official ALLaVA caption rows 全部以
   exact assistant text 映射到 local rows；因此“lineage 完全不可恢复”不是合法
   rejection reason；
5. sample 中 3 个 VFLAN `id` 各出现两次，full-dataset/translation lineage 仍未
   证明；更关键的是 LAION/VFLAN label 不是 source-factorial coverage variable。

**后果**：

- 只否定当前 authoritative broad source/task label + current lineage + audited
  literature 到本地 unique single-factor complementary/redundancy experiment 的
  bridge；
- 不否定 coverage/diversity、Vision-Flan task diversity、domain/compositional
  generalization、source-specific transfer、ALLaVA 全量 lineage 或未来真正
  factorial 的 generative-LVLM experiment；
- 不从 LAION/VFLAN、broad task categories、embedding/LLM clusters 中搜索
  mixture、domain pair 或 target；
- `CROSSFACT-01` 只核查 publisher-defined 的同一 image/acquisition unit × multiple
  text/task factors，要求 exact cells、source-factor orthogonality、matched
  redundancy 与 outcome 前冻结的 held-out cell；
- 本轮 0 GPU、0 checkpoint inference、0 training，未访问 final confirmation；
  没有 `MECHANISM_REJECTED`，没有 `HARD_STOP`。
