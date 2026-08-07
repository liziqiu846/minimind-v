# Research Mission 与当前 Active Research Question

当前阶段：阶段三。

## Mission Question（人工冻结）

> VLM 相比 LLM 的泛化新增了什么科学因素，这些因素如何形成可验证理论规律，并
> 最终指导训练以改善真实泛化？

项目最终主线仍是：

> 理论 → 可验证预测 → 实验验证 → 训练方法 → 真实性能提升

Mission Question 不得由 Agent 自行改变。

## 当前 Active Research Question

当前 active question 是：

> 是否存在一个由 architecture 与正式理论共同唯一固定、无需 layer/rank/proxy
> sweep 的 frozen-feature readout，能够先裁决当前视觉表示是否含有 held-out
> rotation 所需信号，并区分“信号在 frozen representation 中缺失”与“信号存在但
> 下游 autoregressive 模型未吸收/未迁移”？

这一问题是当前子问题，不是永久冻结的唯一主线。Agent 可以依据可靠实验、
反例或权威文献自主切换 Active Research Question。

每次切换必须：

1. 保留旧问题及其适用范围；
2. 记录旧问题为什么走不下去；
3. 记录新问题来自什么证据或文献；
4. 说明新问题为什么比旧问题更直接推进 Mission Question。

不得删除历史问题，也不得用改名方式重复已经失败的路线。

## 当前 Mission Envelope

### 数据侧

- 图文配对质量；
- 图文联合分布；
- 共现结构；
- 域覆盖；
- 组合覆盖；
- 多模态数据多样性；
- 其他真正具有 VLM 特有性的跨模态数据结构。

### 模型 / 表示侧

- 跨模态表示；
- 模态失衡；
- 语言捷径；
- 视觉信息保持；
- shared / private representation；
- 组合表示；
- 跨模态可迁移结构。

### 训练侧

- 多模态训练目标；
- 优化不对称；
- 数据依赖；
- 稳定性；
- 采样；
- 正则化；
- 其他与跨模态关系学习直接有关的训练机制。

三条方向不是互斥路线。

当前允许研究：

> 数据结构 → 模型/表示吸收什么信息 → 训练过程如何形成这种表示 → 未见数据泛化

之间的因果候选机制。

## 冻结项

Agent 不得自行改变：

- Mission Question；
- 项目最终目标；
- VLM 泛化的广义定义；
- 当前仍处于阶段三；
- train / selection / confirmation 的统计关系；
- final confirmation set 的角色；
- MiniMind-V 作为低成本验证平台的定位。

Agent 可以自主改变：

- Active Research Question；
- 当前 active candidate；
- 数据侧、表示侧或训练侧重点；
- 当前理论工具；

前提是切换有证据、有文献依据，并明确服务于 Mission Question。

## 当前明确禁止

- 继续挽救 gradient replacement D_I；
- 回到只优化 checkpoint 码长；
- 把 token 数直接替代独立图像数；
- 机械按 vision / projector / language 名称拆复杂度；
- 未经理论桥梁制造新的 proxy 后反向寻找解释；
- 把经验 proxy 描述成正式互信息或严格理论量；
- 自行改变官方阶段标签。

阶段三内允许在非 final confirmation 数据上进行符合预注册和最小训练规则的
机制干预与 `PROVISIONAL_ALGORITHM_TEST`。

## Active Research Question 历史

### 2026-08-07｜初始 active question

- **Question**: checkpoint 描述长度下降但真实 VLM 泛化没有稳定改善时，哪一种
  VLM 特有机制能够解释这种脱钩并产生可验证预测？
- **Origin**: 已有 phase 2 / phase 3 结果显示码长改善与真实性能并不稳定一致。
- **Status**: SUPERSEDED_AS_ACTIVE；它仍是经验起点，但作为当前问题过宽，不能直接
  决定唯一最小实验。

### 2026-08-07｜COMP-01 active question

- **Question**: 在相同训练数据、预算和 seed 下，较短的共享结构若真实性能更差，
  是否是因为它更弱地保留了跨模态组合绑定？
- **Why the old question was insufficient**: 旧问题同时覆盖数据、表示和训练机制；
  `XMC-01_round1` 已显示已审计 P/S pair 的实际数据图相同，继续停留在宽问题不能
  区分模型保持机制。
- **Evidence / literature origin**: 6 对 P/S data/permutation equality；Winoground、
  ARO、SugarCrepe 关于 same-word relation/order failure 与 hard-negative training 的
  primary evidence。
- **Mission relation**: 它直接测试 VLM 相比 LLM 新增的跨模态关系绑定，能被外部
  benchmark 否定，并有 composition-aware training 的自然出口。
- **Status**: DEMOTED_AS_ACTIVE；failure level=`PROXY_REJECTED`。完整外部
  prediction test 仅 5/9 sign concordance、1/9 预测方向 CI 不跨 0，否定当前
  caption+EOS NLL binding proxy，不否定跨模态组合绑定机制。

### 2026-08-07｜XMC-01 model-retention bridge active question

- **Question**: 是否存在一个具有正式理论桥、可由冻结 autoregressive LVLM 表示
  唯一计算的跨模态对应结构保持量，能够预测未见数据真实性能差异？
- **Why the old question was insufficient**: `COMP-01` 的生成式 caption NLL
  relation margin 跨 budget 不稳定，且 95.4%–99.8% pair 的两图偏好同一 caption；
  继续围绕生成 likelihood 会重复已经失败的 language-bias bridge。
- **Evidence / literature origin**: `XMC-01_round1` 已排除 6/9 pair 的纯训练数据图
  差异；Zhang et al. 2023 提供 MMCL→共现谱→linear-probe 的正式起点，但尚未证明
  适用于 generative LVLM。
- **Mission relation**: 先审计理论能否连接“联合数据结构→模型表示保持→真实风险”，
  可避免继续制造无桥 proxy；支持时有 representation-preserving training 的算法
  出口，否定时可低成本转向视觉条件利用机制。
- **Status**: DEMOTED_AS_ACTIVE；failure level=`BRIDGE_REJECTED`。13 篇
  primary-source/appendix audit 未找到从冻结 autoregressive LVLM 表示到未见语义
  风险的唯一量。最强结果分别止于 contrastive retrieval/linear probe、
  linear-Gaussian dual-encoder conditional 或机制性 UFM；该结果只否定当前 bridge，
  不否定跨模态共现或表示保持机制。

### 2026-08-07｜VISCOND-01 active question

- **Question**: 在相同训练数据、预算和 seed 下，真实性能更差的冻结 MiniMind-V
  是否系统性地更少利用任务相关图像条件，而更多依赖 language-only prior？
- **Why the old question was insufficient**: `XMC-01` 没有合法的生成式 LVLM
  representation-risk bridge；继续测通用 embedding geometry 会变成无理论约束的
  proxy search。
- **Evidence / literature origin**: `COMP-01` 显示生成 caption NLL 被语言偏好主导；
  Eyes Wide Shut、MMStar、POPE、VCD 等工作提供视觉依赖/语言捷径的经验机制，但
  尚无正式生成风险 theorem。
- **Mission relation**: correct-image 相对 counterfactual/no-image 的预测变化是
  生成式 LVLM 特有且可直接证伪的操作性代理；若稳定，可导向视觉保持辅助目标、
  vision-aware sampling 或 decoding/training intervention。
- **Status**: DEMOTED_AS_ACTIVE；failure level=`PROXY_REJECTED`。官方 MMStar
  1,496 eligible items、1,426 独立 image groups、18/18 checkpoint 的 pooled
  correct-image vs no-pixel \(V\) 为
  `-0.2212` bits/token，95% CI `[-0.3067,-0.1348]`，仅 `2/18` 模型为正。虽有
  `6/9` pair 方向一致和 `4/9` 预测方向 CI，但已触发预注册构念否定；不得换
  prompt、答案形式、subset、proxy、benchmark 或 seed rescue。视觉条件信息机制
  本身仍开放。

### 2026-08-07｜训练时跨模态监督/优化机制 active question

- **Question**: 在三条冻结 checkpoint prediction route 均失败后，是否存在一个以
  训练时跨模态监督信息或优化动力学为核心、不是任意 checkpoint proxy 重命名的
  VLM-specific mechanism，能由最小受控干预区分至少两个竞争解释并预测未见任务
  泛化？
- **Why the old question was insufficient**: `VISCOND-01` 显示同一冻结 VLM 在
  视觉必要 MMStar 上加入正确像素后，预声明答案 margin 对当前家族总体反而下降；
  因而不能以该代理为正门启动 `OBJ-01`，也不能继续换视觉 ablation 来营救。
- **Evidence / literature origin**: `COMP-01` 的 caption likelihood 被语言偏好主导，
  `XMC-01` 缺 autoregressive-risk theorem bridge，`VISCOND-01` 的构念正向门失败；
  CoCa、Prismatic、MM1 等已有受控工作提示 objective、视觉表示与数据 mixture 会
  改变能力，但现有 registry 尚未给出适合当前 artifact 的唯一 causal mechanism。
- **Mission relation**: 转向训练时可干预对象可以直接区分“跨模态信号没有被学习”
  与“冻结输出代理不具构念效度”，并保留从科学规律自然导出训练机制的出口；正式
  登记候选前必须先通过定向 primary-source literature/theory gate。
- **Status**: COMPLETED_AS_GATE；定向检索 568 records / 532 unique titles，全文
  核查 6 篇 primary sources。ROSS、ASVR、JARVIS、LaVer 和 V-GIFT 为生成式 LVLM
  提供相互独立的直接视觉 target 干预；其中只有 V-GIFT 同时给出三 seed、
  matched-compute、single-image 与本地最小可实现设计。保留 `VISSUP-01`，其余多
  head/loss/layer 方案不进入本地首测。

### 2026-08-07｜VISSUP-01 visually necessary instruction active question

- **Question**: 在相同 M2-current 结构、base draws、rotated pixels、rotation label
  distribution、optimizer steps 与 target token format 下，visual-necessary
  rotation instruction 是否比文本直接泄露 label 的 control 更能形成可迁移视觉
  能力，并改善尚未评分的新外部 CV-Bench-2D performance？
- **Why the old question was insufficient**: 训练侧 broad question 仍允许多种 loss、
  layer、head 和 data mixture；LITMAP-02 显示其中多数需要事后选择。V-GIFT 的
  standard autoregressive instruction 数据干预可以把主差异收缩为“任务是否必须
  看图”，且不复用前三个失败 proxy。
- **Evidence / literature origin**: V-GIFT 在 full/LoRA、三个 backbone 和三 seed
  上报告 vision-centric 平均改善；matched extra iterations 无改善，复用原图和
  single-image views 仍有效。ICLR 2025 ROSS 以及 ASVR/JARVIS/LaVer 独立支持
  text-only output supervision 遗漏视觉结构；CVPR 2025 *Words or Vision* 只提供
  text/multimodal mixture 的正式相邻 risk decomposition，不被当作本 candidate
  theorem。
- **Mission relation**: 这是“训练监督关系 → 模型吸收视觉结构 → 未见视觉任务”
  的直接因果候选；若成功可自然导出 visually necessary sampling/data construction，
  若失败则否定该机制在当前低维 MiniMind-V 下的可迁移性。
- **Status**: DEMOTED_AS_ACTIVE；failure level=`INSTANTIATION_REJECTED`。round1
  在模型运行前发现 CV-Bench 为 2–6 choices，按规则使用唯一 schema rescue。
  round2 root `43101` paired pilot 中，visual 相对 control 的 held-out rotation
  accuracy 差为 `-0.00694`，95% CI `[-0.03770,0.02282]`；CV-Bench-2D 差为
  `-0.00139`。这只否定当前 9.16% rotation / 4,096-coordinate / frozen
  encoder-adapter instantiation；禁止补 roots、换 rotation task/ratio/prompt/proxy，
  但不否定 objective design 一般作用。

### 2026-08-07｜LITMAP-03 low-dimensional visual trainability gate

- **Question**: VISSUP 显式视觉监督未进入 4,096-coordinate M2-current 的主要原因，
  是否存在权威证据支持的 frozen-encoder identifiability、trainable-subspace
  capacity/module allocation 或 objective competition 机制，并能由一个最小干预
  区分至少两个解释？
- **Why the old question was insufficient**: `VISSUP-01` 不仅没有外部迁移，held-out
  rotation 本身也保持 chance；因此不能把失败只归因于 transfer benchmark，也不能
  通过换 rotation ratio/task 来维护“必须看图就会学到”。
- **Evidence origin**: VISSUP 的严格 paired pixels/labels/steps 结果；ROSS/ASVR/
  JARVIS/LaVer 使用 richer latent target 或额外 component，而 V-GIFT 的较大模型
  结果没有迁移到本低维设置。需要补查 parameter-efficient MLLM、visual adapter
  capacity、gradient routing 与 frozen vision encoder task identifiability 的
  primary sources。
- **Mission relation**: 若能找到可判别机制，可解释为何相同参数码长/训练信号未产生
  视觉能力，并自然导出 module-aware allocation 或视觉 target routing；若只有通用
  PEFT engineering 或事后 gradient/representation proxy，则不进入主线。
- **Status**: COMPLETED_AS_GATE；五族检索得到 541 raw records / 480 unique titles，
  全文核查 11 篇 primary sources。ACL 2024 PEFT 与 CROME 支持 connector /
  pre-LLM adapter 的作用，Cambrian-1 支持 vision encoder unfreezing；方向冲突且均
  未固定 trainable parameter count，因此只保留本地 fixed-total
  `PROJALLOC-01`，不运行旧 module sweep。

### 2026-08-07｜PROJALLOC-01 fixed-total projector allocation active question

- **Question**: 在相同 frozen base、11 targets、总 4,096 trainable coordinates、
  visual-necessary data、pixels、labels、prompt、optimizer、steps 与 scorers 下，
  projector-dominant `1/4094/1` 是否比 current `582/2327/1187` 更能学习 held-out
  rotation，并方向性改善尚未由这些新模型评分的 CV-Bench-2D？
- **Why the old question was insufficient**: `LITMAP-03` 只能证明 module placement
  值得干预；公开文献对 encoder-vs-projector 方向冲突，而且增加参数和 compute
  混杂，不能裁决当前 4,096-coordinate setting。
- **Evidence / literature origin**: ACL 2024 的 connector tune-vs-freeze 与 visual
  encoder tune-vs-freeze、CROME 的 frozen encoder+LLM adapter-only adaptation、
  Cambrian-1 的 matched LLM/data/hyperparameter encoder unfreezing；本地 arbitrary
  private-coordinate constructor 已只读验证 `1/4094/1` 产生 22 个 factor mappings、
  总计 4,096 coordinates、无 unused coordinates。
- **Mission relation**: 该实验直接区分“frozen visual features 可读但 projector
  subspace 容量不足”与“增加 projector 容量仍无法吸收视觉 cue”，可解释为何相同
  参数复杂度对应不同跨模态泛化，并保留 module-aware PEFT 的算法出口。
- **Status**: DEMOTED_AS_ACTIVE；failure level=`INSTANTIATION_REJECTED`。root
  `43201` 的全部 paired engineering invariants 通过，但 projector-dominant 的
  rotation 差只有 `+1.29 pp`、95% CI
  `[-2.08,+4.56] pp`、absolute accuracy `0.26389`，CV-Bench-2D accuracy 与 margin
  分别反向 `-1.39 pp` 和 `-0.05817 bits/token`。预注册六门仅工程配对门通过，
  禁止补 `43202/43203`、换 allocation/metric/proxy 或运行旧 sweep。其他合法
  module-placement regime、frozen-feature identifiability 与 objective mismatch
  仍开放。

### 2026-08-07｜LITMAP-04 objective-routing / task-specific absorption gate

- **Question**: 在显式 visual-necessary supervision 与 projector-dominant allocation
  都失败后，是否存在由 direct autoregressive-LVLM primary evidence 支持、可由单一
  最小干预区分 frozen-feature identifiability、task-specific absorption 与
  objective competition / gradient routing 的新机制？
- **Why the old question was insufficient**: `PROJALLOC-01` 已直接否定当前
  fixed-total setting 的 projector-capacity 解释；rotation 小幅正点估计未达到门且
  CI 跨 0，外部 CV-Bench accuracy/margin 反向。继续搜索 allocation、追加 seed 或换
  proxy 只能维护失败假设，不能判断信号未编码、仅被 task-specifically 吸收，还是
  autoregressive objective 阻碍跨任务迁移。
- **Evidence / literature origin**: `VISSUP-01` 在相同 pixels/labels/steps 下连
  held-out rotation 都无改善；`PROJALLOC-01` 增加 projector coordinate share 后
  rotation 仍近 chance 且外部任务退化。LITMAP-03 已证明 module placement 文献方向
  冲突，尚未系统裁决 objective-level gradient conflict、视觉/语言 token loss
  dominance 或 task-specific-to-external transfer mismatch。
- **Mission relation**: 该 gate 直接追问“训练信号如何进入跨模态表示并决定未见任务
  风险”，若成立可自然导出 objective routing、gradient balancing 或 representation
  matching 原则；若没有满足严格门的机制，则应转向新的数据/表示 candidate，而不是
  重复训练 rescue。
- **Status**: DEMOTED_AS_ACTIVE；failure level=`BRIDGE_REJECTED`。冻结计划后共
  搜索 555 raw records、523 unique titles，完整核查 14 篇决定性 primary sources。
  Direct mechanisms 与 matched controls 存在，但没有路线同时满足 unique、
  single-factor、no-sweep 与本地资源门；结果是 `NO_CANDIDATE`。这只否定当前
  literature-to-local-minimal-intervention bridge，不否定 objective competition、
  gradient routing、task-specific absorption 或 frozen-feature/objective mismatch。

### 2026-08-07｜LITMAP-05 frozen-feature sufficiency / identifiability gate

- **Question**: 是否有 architecture-defined、theory-supported 且无需
  layer/rank/pooling/proxy sweep 的 readout，能判断当前 frozen visual
  representation 是否含有 held-out rotation 所需信号，并把 representation
  insufficiency 与 downstream absorption/transfer failure 区分开？
- **Why the old question was insufficient**: `LITMAP-04` 找到的 objective-routing
  路线都需要多 component、额外 teacher/tokenizer/head、loss/layer/rank/ratio
  选择、seeing/blind proxy 或超出本地资源，不能唯一裁决三个 competing
  explanations；直接启动其中任一路线都会重开已禁止的 search。
- **Evidence / literature origin**: `VISSUP-01` 与 `PROJALLOC-01` 两个不同
  instantiation 均未使 held-out rotation 明显离开 chance，说明在继续改变 objective
  前必须先裁决 frozen feature 中有没有可识别 signal；`LITMAP-04` 也明确把
  frozen-feature/objective mismatch 保留为开放空间。
- **Mission relation**: 该 gate 直接定位“视觉数据结构是否进入了模型表示”与“已进入
  表示但未被生成目标吸收”之间的最小断点；若有唯一 readout，可产生无需新训练的
  falsifier，并为 encoder-side 或 downstream-side 算法选择提供依据；若没有，则转向
  controlled coverage 而不制造新 probe。
- **Status**: ACTIVE_LITERATURE_GATE；下一步创建并提交
  `experiments/plans/LITMAP-05_round1.md`。plan commit 前不执行新 scientific
  search/readout；本 gate 不训练、不访问 final confirmation，也不得 sweep
  layer/rank/pooling/probe/metric。
