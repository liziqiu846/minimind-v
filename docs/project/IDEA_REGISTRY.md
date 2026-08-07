# Autonomous Research Idea Registry

本表记录 Research Envelope 内所有 candidate idea。Agent 提出新 idea 前必须先检查
本表，避免用不同名称重新引入已经否定的机制。

Failed ideas must never be deleted.

允许状态：

- `NEW`
- `TESTING`
- `PROXY_REJECTED`
- `BRIDGE_REJECTED`
- `INSTANTIATION_REJECTED`
- `MECHANISM_REJECTED`
- `INCONCLUSIVE`
- `PROMISING`
- `CONCLUSION_CANDIDATE`

历史 result 中的 `REJECT_IDEA` 是 autonomous workflow disposition，不自动等价于
`MECHANISM_REJECTED`。任何失败必须在下方 Failure-scope ledger 中写清科学作用域。

## Dynamic backlog

| Queue | Candidate | Why now? |
|---|---|---|
| `ACTIVE` | `COVER-01` authoritative controlled-coverage gate | `LITMAP-05` 已证明当前文献与 architecture 不能唯一固定具有负向排除力的 readout；先核查 authoritative domain/mixture/combination strata 与本地数据 lineage，不制造新 proxy |
| `NEXT` | 尚无可执行 candidate | 只有 `COVER-01` 同时通过 authoritative strata、single-factor contrast、held-out directional prediction 与 local feasibility 门，才登记一个 coverage candidate |
| `BACKLOG` | `OBJ-01` | 原 OBJ 启动依赖的 VISCOND positive gate 已失败；LITMAP-04 也未提供合法最小 objective bridge，不得无机制地启动训练 |

| ID | Candidate mechanism | Category | VLM-specific novelty | Literature relation | Why it may explain code/performance decoupling | Falsifiable prediction | Cheapest valid test | Future algorithmic implication | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| XMC-01 | 跨模态共现图/配对语义一致性，以及模型对主要跨模态谱方向的保持 | Data + representation | 图文联合分布和非对称共现图是单模态 LLM 不具有的对象 | Zhang et al. 2023 给出 spectral MMCL→共现矩阵分解→linear-probe bound；DataComp/DFN/BLIP 提供数据算法证据 | 码长不决定配对语义误差、图连接性或模型是否保留对应谱方向；压缩可降低复杂度同时增加表示近似误差 | 在预声明的关系保持/关系破坏图文对上，真实性能较差的同数据模型应有更小的正确配对 margin；若纯数据统计在同数据 P/S 间不变且无模型保持差异，则不能解释 P/S | 先审计现有 artifact 是否支持冻结 checkpoint 的 pair-margin / representation test；不对历史结果试多个 proxy | semantic-pair filtering、coverage-aware sampling、谱/低秩保持正则 | round1：6/9 P/S 实际数据/permutation 相同，3/9 缺 manifest；round2：完整核查 13 篇 primary theory，最强结果分别止于 contrastive linear probe/retrieval、Gaussian dual-encoder conditional 或机制性 UFM，均无唯一 autoregressive LVLM statistic→semantic-risk bridge；禁止 proxy/layer/rank sweep rescue | BRIDGE_REJECTED |
| COMP-01 | 跨模态组合绑定相对 bag-of-words / language shortcut | Representation + data | 保持对象/词边际信息但丢失图文关系和顺序，是跨模态组合问题 | Winoground、ARO、SugarCrepe；ARO 提供 composition-aware hard-negative 证据 | 更短/更共享的模型可能维持普通 NLL，却在关系交换、属性绑定和词序反事实上退化 | 同词集合、只改变关系/顺序的预声明反事实对上，较差模型的正确-vs-反事实 margin 应更小 | 冻结 checkpoint 对标准外部双图双描述 panel 做 forced-choice NLL；交叉差分抵消加性文本偏好 | 组合感知 hard negatives、relation-balanced sampling | round1 完整 What’sUp 410 pairs：sign concordance `5/9`、预测方向 CI `1/9`、budget concordance low/current/high=`1/3,3/3,1/3`；95.37%–99.76% pairs 两图偏好同一 caption；触发预注册否定且禁止 rescue | PROXY_REJECTED |
| VISCOND-01 | 任务相关视觉条件信息的保持与利用，而非语言先验替代 | Representation | 需要区分语义预测风险与图像条件增量，属于生成式 LVLM 特有问题 | Eyes Wide Shut、MMStar、POPE、VCD | 结构压缩可保留语言能力却损伤视觉表示或图像对输出的条件影响，因此码长和真实性能脱钩 | 较差模型在预声明的视觉必要样本上应表现出更小的 correct-image 相对 counterfactual-image 增益，且不能由 language-only baseline 解释 | 冻结模型、固定视觉必要样本与单一预声明操作性代理；不得称互信息或正式视觉风险 | 视觉保持辅助目标、vision-aware sampling、视觉对比解码/正则 | round1：官方 MMStar 1,496 eligible items / 1,426 image groups、18/18 frozen checkpoints；pooled correct-image vs no-pixel \(V=-0.2212\) bits/token，95% CI `[-0.3067,-0.1348]`，仅 `2/18` 模型为正；pair concordance `6/9`、预测方向 CI `4/9`，触发构念否定；禁止换 prompt/subset/proxy/benchmark/seed rescue | PROXY_REJECTED |
| OBJ-01 | contrastive / generative / next-token 监督对视觉关系学习的不平衡 | Training | 图文对齐、生成和语言建模目标竞争是跨模态训练特有结构 | CoCa、SigLIP、MM1、Prismatic、LLaVA-1.5 | 参数压缩不保证视觉监督足够；next-token loss 可由语言捷径降低而视觉关系未学好 | 固定数据/算力下增加预声明视觉关系辅助目标应改善视觉必要/组合泛化，且不以码长变化解释 | 今晚只能冻结最小训练设计；真正判别需要新训练 | joint contrastive-captioning、visual-dependency weighting、objective-balanced curriculum | `ALGORITHMIC_EVIDENCE`; causal LVLM validation absent | NEW |
| COVER-01 | 图文域与组合覆盖，而非样本量本身 | Data | 联合覆盖对象是“域×视觉概念×文本表达”的跨模态组合 | Kempf et al. 2025、DataComp、MM1 | 短码模型仍可能在未覆盖组合上失败；简单规模/码长无法编码覆盖关系 | 受控增加互补域/组合应改善预声明 OOD 方向，而增加冗余同域数据不应有同等收益 | 今晚只能核查现有数据清单；合法测试需控制数据 mixture 后重训 | coverage-aware sampling、dataset mixture optimization、targeted recaptioning | `EMPIRICAL_MECHANISM`；CLIP→LVLM bridge 未完成 | NEW |
| VISSUP-01 | caption-only next-token 监督相对“必须看图”的自监督 instruction 不充分 | Training + data construction | 用相同图像/答案/算力改变文本是否泄露标签，直接干预 autoregressive 目标是否需要视觉条件 | ROSS（ICLR 2025）、Words or Vision（CVPR 2025）、ASVR、JARVIS、LaVer、V-GIFT | 同样低维参数结构可用语言统计拟合 caption；码长不保证训练样本迫使模型吸收可迁移视觉结构 | 等 rotated pixels、label distribution、steps 下，visual-necessary rotation mix 应比 label-revealed control 提高 held-out rotation 能力，并方向性改善尚未评分的新外部 vision-centric panel；否则机制在当前 MiniMind-V 不成立 | M2-current，10,000 base draws + 固定 1,008 rotation samples；先 1 个 paired mapping root，positive 才补 total 3；不计算 no-pixel proxy | visually necessary task sampling、self-supervised instruction construction | round1：官方 CV-Bench variable-choice schema gate，0 runs；round2 root 43101 paired pilot：rotation control/visual=`0.2520/0.2450`，Δ=`-0.00694`、95% CI `[-0.03770,0.02282]`；CV-Bench=`0.3547/0.3533`，Δ=`-0.00139`；当前 instantiation 的机制门与外部门均失败，禁止补 roots 或换 task/ratio/proxy | INSTANTIATION_REJECTED |
| PROJALLOC-01 | 固定总 trainable coordinates 下，把低维更新容量从 vision/language targets 转移到跨模态 projector | Training + representation | 直接干预 frozen visual features 进入 autoregressive LLM token space 的可训练桥，而不是机械按模块名拆复杂度或新造 checkpoint proxy | ACL 2024 PEFT 显示 connector tuning 对 unseen tasks 更常有益而 vision unfreeze 多数无益；CROME 显示 frozen encoder+LLM 下 adapter-only 可强适配；Cambrian-1 则在 matched LLM/data/hyperparameters 下支持 vision unfreeze，留下需本地裁决的冲突 | 相同 4,096-coordinate 码长可因 allocation 不同而具有不同视觉更新可达性；若 projector 是瓶颈，current 的部分复杂度并未用于把视觉 cue 映射为 LLM 可用 token | `1/4094/1` 相对 current `582/2327/1187`：held-out rotation accuracy 至少 `+5 pp`、paired-bootstrap CI lower `>0`、绝对 accuracy `>=0.30`；CV-Bench-2D image-group accuracy 至少 `+1 pp` 且 gold-margin difference `>0` | fresh root `43201` 的二条件 paired pilot；相同 base、visual-necessary data、pixels、labels、prompt、optimizer、steps、scorers 与总 4,096 coordinates；阳性后才补 roots `43202/43203` | 若跨 seed 与外部任务稳定，可导出 task-aware module allocation / projector-dominant PEFT 原则；失败则否定当前严格 setting 的 projector-capacity 解释 | round1 root `43201`：paired invariants 全通过；rotation current/projector=`0.25099/0.26389`，差 `+1.29 pp`、95% CI `[-2.08,+4.56] pp`、margin 差 `-0.00105`；CV-Bench=`0.35257/0.33866`，差 `-1.39 pp`、95% CI `[-3.96,+1.11] pp`、margin 差 `-0.05817`。六门仅工程配对门通过，触发 `REJECT_IDEA`；适用范围仅为当前 frozen-base / hashed-coordinate / visual-necessary setting。排除当前 exact fixed-total projector allocation instantiation，仍允许 frozen-feature identifiability、objective mismatch 或其他训练动力学；禁止 `43202/43203`、allocation/metric/proxy search | INSTANTIATION_REJECTED |
| LITMAP-04 | objective routing / task-specific absorption literature-to-local bridge | Training theory gate | 裁决 autoregressive LVLM 中视觉/语言目标竞争、视觉 credit routing 与 task-specific transfer 是否能形成本地单因素干预 | CoMMIT、MoReS、DPA、VIGIL、OPD-V、ROSS、ASVR、DV-SFT、JARVIS、LaVer、V-GIFT 等 14 篇决定性 primary sources | 若存在唯一最小干预，可区分 representation 缺失、task absorption 与 objective competition；否则继续训练会把多因素/超参选择误当机制检验 | ≥2 direct sources、≥1 matched control、mechanism+external evidence，且唯一 no-sweep 本地干预必须同时成立 | 冻结 literature gate；不运行 checkpoint/GPU/training | 支持时导出 objective-routing intervention；失败时精确冻结 bridge 并转向 representation/data gate | 555 raw records、523 unique titles、14 篇全文/appendix 核查；direct evidence 门通过，但所有本地路线需要额外 component、proxy、layer/rank/loss/ratio 选择、multi-stage 或超出资源；`NO_CANDIDATE` | BRIDGE_REJECTED |
| LITMAP-05 | frozen-feature sufficiency / identifiability bridge | Representation theory gate | 直接定位视觉信号是否已进入 frozen representation，区别于下游 autoregressive absorption/transfer | formal probing/decodability theory 与 direct LVLM studies 均表明 readout 依赖 analyst choice；MiniMind-V architecture 只固定 feature tensor、不固定 task readout | 若 frozen representation 已含可识别任务信号，训练失败更可能位于 downstream absorption；若信号缺失，objective rescue 缺少输入基础 | 必须存在 architecture/theory 唯一固定 readout；若无，禁止 layer/rank/pooling/probe/metric sweep | 553 raw records、491 unique titles、13 篇决定性 primary sources与 exact local interface audit；0 probe/GPU/training | 可导出 encoder-side representation repair 或 downstream-side absorption intervention 的分流原则 | `NO_CANDIDATE`：formal family/target/regularization 仍需选择，direct LVLM evidence 使用 layer/token/pooling/LR 或 max-over-layer selection，负 probe 无 completeness；只否定当前 identifiability bridge | BRIDGE_REJECTED |

## Failure-scope ledger

### XMC-01

- **Failure level**: `BRIDGE_REJECTED`
- **What exactly is rejected**: 当前已核查的 contrastive/co-occurrence、dual-encoder
  geometry 与 low-rank alignment theory，不能唯一固定一个冻结 autoregressive
  MiniMind-V statistic 并推出 unseen semantic-risk 方向。
- **What is NOT rejected**: 跨模态共现结构、谱结构、联合数据结构或模型表示保持会
  影响 VLM 泛化的上位机制。
- **Evidence**: round1 中可完整审计的 6/9 P/S pair 使用相同 data/permutation；
  round2 核查 13 篇 primary sources，正式结果止于 contrastive retrieval /
  linear probe、linear-Gaussian dual-encoder conditional 或机制性 UFM；任何本地量
  仍需选择 layer/pooling/kernel/rank/proxy。
- **Remaining hypothesis space**: 新的 autoregressive generative-risk theorem、新的
  可识别 artifact、不同但先验唯一的 model-retention bridge。
- **Next search implication**: 只有“新理论桥或新 artifact”才能恢复；禁止通过
  CKA/CCA/HSIC、layer 或 rank sweep 换名重试。

### COMP-01

- **Failure level**: `PROXY_REJECTED`
- **What exactly is rejected**: What’sUp panel 上 caption+EOS teacher-forced NLL
  四格 binding margin，不能可靠表示跨模态组合绑定，也不能稳定预测 M2/M3 总语义
  风险排序。
- **What is NOT rejected**: 组合绑定、关系理解、属性绑定或 compositional
  generalization 会影响 VLM 泛化的机制。
- **Evidence**: sign concordance `5/9`，预测方向 CI `1/9`；low/current/high budget
  concordance `1/3,3/3,1/3`；`95.37%–99.76%` pairs 的两图偏好同一 caption，表明
  proxy 被加性语言偏好主导。
- **Remaining hypothesis space**: 有独立构念效度、能控制语言偏好且不依赖事后
  metric 选择的关系测量或直接机制干预。
- **Next search implication**: 不换 panel、caption scoring 或 budget rescue；只有
  新理论缺口、外部反例和先验固定的新测量才能形成新 candidate。

### VISCOND-01

- **Failure level**: `PROXY_REJECTED`
- **What exactly is rejected**: MMStar answer-letter correct-image relative to
  no-pixel gold-vs-distractor margin \(V\)，不能作为当前家族正向视觉利用或总语义
  风险排序的可靠 proxy。
- **What is NOT rejected**: 任务相关视觉条件信息、视觉依赖、语言捷径或视觉信息
  利用会影响泛化的上位机制；\(V\) 也从未被证明为互信息或正式视觉风险。
- **Evidence**: 18/18 frozen checkpoints；pooled \(V=-0.2212\) bits/token，
  95% CI `[-0.3067,-0.1348]`，仅 `2/18` 为正；pair concordance `6/9`、预测方向
  CI `4/9`。
- **Remaining hypothesis space**: 有理论构念效度的 counterfactual、干预或训练期
  测量；视觉输入分布/提示接口不匹配也仍开放。
- **Next search implication**: 不换 prompt、answer text、subset、benchmark 或
  proxy rescue；不能用本 proxy 的 positive gate 启动 `OBJ-01`。

### VISSUP-01

- **Failure level**: `INSTANTIATION_REJECTED`
- **What exactly is rejected**: 固定 9.16% rotation instruction、M2-current、
  4,096 hashed trainable coordinates、当前 frozen encoder/adapter 和既定
  autoregressive target 的 visual-necessary intervention。
- **What is NOT rejected**: visually necessary supervision、视觉辅助目标、训练目标
  设计或 richer direct visual targets 在其他合法 setting 中的上位作用。
- **Evidence**: root `43101` paired invariants 全通过；rotation 差 `-0.69 pp`，
  95% CI `[-3.77,+2.28] pp`；CV-Bench 差 `-0.14 pp`，两项主 accuracy 均未改善。
- **Remaining hypothesis space**: frozen-feature identifiability、objective mismatch、
  gradient routing、task-specific absorption，以及有 direct evidence 的不同 objective
  instantiation。
- **Next search implication**: 不补 roots，不换 task/ratio/prompt/metric；搜索必须
  由本失败暴露出的机制缺口和 direct autoregressive-LVLM primary evidence 驱动。

### PROJALLOC-01

- **Failure level**: `INSTANTIATION_REJECTED`
- **What exactly is rejected**: 当前 frozen-base、visual-necessary data、
  4,096 hashed coordinates 下，exact `1/4094/1` projector-dominant 相对
  `582/2327/1187` current allocation 的具体 fixed-total intervention。
- **What is NOT rejected**: module placement 一般规律、frozen encoder 是否可读、
  其他有独立理论支持且预先固定的 allocation regime、objective competition 或
  gradient routing。
- **Evidence**: root `43201` 全部 engineering invariants 通过；rotation 差
  `+1.29 pp`、95% CI `[-2.08,+4.56] pp`，CV-Bench accuracy 差 `-1.39 pp`，
  margin 差 `-0.05817`；六门仅工程配对门通过。
- **Remaining hypothesis space**: frozen-feature/AR-objective mismatch、
  task-specific absorption、objective routing，以及非 allocation-search 形式的新
  module-specific mechanism。
- **Next search implication**: 禁止 `43202/43203`、allocation sweep、metric/proxy
  search；`LITMAP-04` 应优先裁决 objective-level competing explanations。

### LITMAP-04

- **Failure level**: `BRIDGE_REJECTED`
- **What exactly is rejected**: 当前核查的 objective-routing、visual-credit、
  task-specific-absorption 与 auxiliary-objective primary literature，不能唯一导出
  一个适用于本地 MiniMind-V、single-factor、no-sweep、资源可行且能区分至少两个
  competing explanations 的最小干预。
- **What is NOT rejected**: objective competition、gradient routing、task-specific
  absorption、frozen-feature/objective mismatch，或文献中多组件方法在其原始 setting
  中的有效性。
- **Evidence**: 555 raw records、523 unique titles、81 prior-search duplicates、
  56 个 heuristic score≥10；完整核查 14 篇决定性 primary sources。Direct mechanism
  与 matched controls 存在，但本地路线均需要额外 architecture/component、
  teacher/tokenizer/head、seeing/blind proxy、layer/rank/loss/ratio 选择、
  multi-stage schedule 或超出当前资源；14/14 来源可核查，故不是 inconclusive。
- **Remaining hypothesis space**: 由新 architecture/theory 唯一确定的
  frozen-feature sufficiency readout；未来出现单因素 objective intervention；
  controlled coverage/data mechanisms。
- **Next search implication**: 不从已核查方法中任挑一个 component 或超参数进行
  exploratory training；转入 `LITMAP-05`，先裁决 frozen representation 中是否有
  可识别 signal。若仍无 bridge，转向 authoritative controlled coverage gate。

### LITMAP-05

- **Failure level**: `BRIDGE_REJECTED`
- **What exactly is rejected**: 当前 formal probing/decodability theory、direct
  LVLM evidence 与 MiniMind-V architecture 不能共同唯一固定一个无需
  layer/token/pooling/readout/regularization/metric 选择、且对 negative result
  具有 completeness 或 impossibility 排除力的 frozen-feature readout。
- **What is NOT rejected**: frozen representation 可能含有 task signal；
  downstream projector/autoregressive decoder 可能未吸收或迁移该 signal；
  objective mismatch、encoder limitation，以及由独立理论预先固定的 linear 或
  nonlinear decodability family 均未被否定。
- **Evidence**: 五族检索得到 553 raw records、491 unique titles、58 个
  prior-search duplicates 与 45 个 heuristic score≥10 records；13 篇决定性
  primary sources和 exact local interface 均可完整核查。Predictive
  \(\mathcal V\)-information、DIB 与 representational-similarity decoding theory
  都要求 analyst 选择 family、target 或 regularization；最直接 LVLM studies
  遍历 layer/token/pooling/LR 或使用 max-over-layer；MiniMind-V 仅固定 SigLIP2
  `last_hidden_state` 与 64-token projector input。负有限 probe 没有 completeness
  guarantee。
- **Remaining hypothesis space**: encoder-side signal absence、已有 signal 的
  downstream absorption/transfer failure、frozen-feature/objective mismatch、
  authoritative controlled-coverage data mechanism，以及未来出现的正式
  generative-LVLM readout theorem。
- **Next search implication**: 禁止通过 layer、token、pooling、classifier、
  regularization、rank 或 metric sweep 制造 positive probe；转入 `COVER-01`，
  优先使用 source-defined domain/mixture/combination strata，避免再造 checkpoint
  proxy。
