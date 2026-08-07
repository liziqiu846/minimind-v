# Asynchronous Human Review Queue

重要事项写入此队列并冻结相关结论。除非同时触发 `HARD_STOP`，队列中存在事项
不得停止 Research Envelope 内其他已授权工作。

## 2026-08-07｜失败作用域对账

- `XMC-01`：`BRIDGE_REJECTED`，不否定跨模态共现/表示保持机制。
- `COMP-01`：`PROXY_REJECTED`，不否定组合绑定机制。
- `VISCOND-01`：`PROXY_REJECTED`，不否定视觉条件信息机制。
- `VISSUP-01`：`INSTANTIATION_REJECTED`，不否定 objective design 一般作用。
- `PROJALLOC-01`：`INSTANTIATION_REJECTED`，不否定其他 module-placement regime。

以下早先记录中的 workflow `REJECT_IDEA` 均按上述 failure level 解读；当前没有
`MECHANISM_REJECTED`。

## 2026-08-07｜XMC-01：纯数据解释已局部排除，模型保持桥待验证

- **Date**: 2026-08-07
- **Idea / issue**: 跨模态共现图/配对语义一致性是当前形式理论最强方向，但现有正式
  定理只覆盖 spectral contrastive dual encoder + linear probe；生成式 LVLM 桥未完成。
- **Why human should review it**: 它可能成为阶段三主攻方向，但不能把 CLIP 定理直接
  套到 MiniMind-V，也不能把新的 checkpoint proxy 当定理。
- **Current evidence**: 文献地图支持；round1 实际审计的 6/9 P/S pair 数据 SHA 与
  epoch permutation SHA 全相同，说明纯数据量在这些 pair 内不能解释结构排序。
  current-budget 3/9 只有一致 config，缺 training manifest，因此全矩阵结论为
  `DATA_GRAPH_IDENTITY_NOT_AUDITABLE`。
- **What Agent has already frozen**: 已冻结“纯数据 XMC 不能解释已审计 6 对 P/S”；
  未冻结全 9 对结论；未宣称模型保持版本成立。
- **Whether autonomous work can continue**: 可以；不触发 `HARD_STOP`。
- **Recommended human decision**: 允许下一 cycle 先恢复/核查 current-budget manifest，
  然后对冻结 checkpoint 做预注册的、标准外部 counterfactual pair forced-choice
  test；仍不训练新模型。

## 2026-08-07｜OBJ-01 / COVER-01：合法判别需要新训练

- **Date**: 2026-08-07
- **Idea / issue**: objective balance 与 controlled domain/compositional coverage 均有
  算法证据，但现有同数据 checkpoint 不能给出因果判别。
- **Why human should review it**: 真正验证需要重新训练；现有 artifact 不能给出因果
  判别，但当前两个 broad idea 都还没有满足 mechanism-intervention training 的
  candidate-specific prediction 与唯一最小设计。
- **Current evidence**: CoCa/MM1/Prismatic/SigLIP 及 Kempf/DataComp 的文献证据；
  尚无 MiniMind-V prediction test。
- **What Agent has already frozen**: 两个方向均保持 `NEW`，不以 broad 名称直接训练；
  `OBJ-01` 原先依赖的 `VISCOND-01` positive proxy gate 已失败，`COVER-01` 缺合法
  domain/mixture 标签。
- **Whether autonomous work can continue**: 可以；若后续新 candidate 满足
  AGENTS.md 的阶段三最小机制干预全部条件，可在预授权资源内执行，不需因训练本身
  停机。
- **Recommended human decision**: 无需立即决定；只有明显扩大服务器资源、改变冻结
  统计关系或访问 final confirmation 时才按 `HARD_STOP` 请求决定。

后续每条记录至少包含：

## YYYY-MM-DD｜Idea / issue

- **Date**:
- **Idea / issue**:
- **Why human should review it**:
- **Current evidence**:
- **What Agent has already frozen**:
- **Whether autonomous work can continue**:
- **Recommended human decision**:

## 2026-08-07｜COMP-01：caption-NLL binding proxy 被否定

- **Date**: 2026-08-07
- **Idea / issue**: 标准 What’sUp controlled panel 上，生成式 caption+EOS NLL
  binding margin 是否解释 M2/M3 development 风险排序。
- **Why human should review it**: 这是首个真正未查看外部模型 prediction test；结果
  否定当前 proxy，同时揭示生成 NLL 几乎被 pair 内同-caption 偏好支配，但不能
  外推为组合绑定机制不存在。
- **Current evidence**: 18/18 checkpoint、410 pairs、205-cluster bootstrap；
  sign concordance `5/9`，仅 `1/9` 预测方向 CI 不跨 0，low/current/high 分别
  `1/3,3/3,1/3`。触发 immutable plan 的 `≤5/9` 否定标准。
- **What Agent has already frozen**: `COMP-01=PROXY_REJECTED`；只否定当前
  What’sUp caption+EOS NLL binding margin。不得挑 current budget、更换
  panel/proxy、追加模型或训练来 rescue；组合绑定机制仍开放。保留 raw 四格 NLL、
  运行回执和 bootstrap 判定。
- **Whether autonomous work can continue**: 可以；已转向 `XMC-01` model-retention
  bridge。
- **Recommended human decision**: 无需立即决定；之后审查时重点确认 cluster
  bootstrap 与“生成 likelihood 不适合作为关系判别 bridge”的边界表述。

## 2026-08-07｜XMC-01：生成式 model-retention bridge 被理论 gate 否定

- **Date**: 2026-08-07
- **Idea / issue**: 是否可把 MMCL 共现谱、representation geometry 或 low-rank
  alignment theory 迁移成冻结 autoregressive MiniMind-V 的唯一保持量。
- **Why human should review it**: 这是对当前最强形式理论路线的适用性否定，不是否定
  原论文定理；边界措辞决定后续不能用无桥 CKA/CCA/HSIC 或 token probe 营救。
- **Current evidence**: 完整核查 13 篇 primary paper/appendix。最强“生成式”结果
  限于 dual-encoder tilting 与 linear Gaussian conditionals；最强 risk calibration
  限于 contrastive retrieval AUC；最直接 low-rank LVLM theorem 自述为机制解释而非
  quantitative bound，且 downstream 联系只属关联。
- **What Agent has already frozen**: `XMC-01=BRIDGE_REJECTED`；不得 sweep
  layer/pooling/kernel/rank/proxy，不把 contrastive/linear-probe theorem 直接套到
  autoregressive semantic risk。跨模态共现与表示保持机制本身未被否定。
- **Whether autonomous work can continue**: 可以；已转向 `VISCOND-01`，不触发
  `HARD_STOP`。
- **Recommended human decision**: 无需立即决定；之后可审查 theorem applicability
  matrix。若未来要恢复 XMC，必须提供新的生成式风险证明或真正新 artifact，而不是
  更换经验表示指标。

## 2026-08-07｜VISCOND-01：MMStar correct-image vs no-pixel proxy 构念门被否定

- **Date**: 2026-08-07
- **Idea / issue**: 正确图像相对同一 VLM no-pixel 条件的答案判别增量，能否作为
  解释 M2/M3 development 总语义风险排序的视觉利用机制。
- **Why human should review it**: pair 排序出现 `6/9` 局部一致，但 18 模型 pooled
  视觉增量显著为负；必须防止只报告局部排序、忽略操作性构念本身没有正向视觉获益。
- **Current evidence**: 官方 MMStar frozen revision；1,496 eligible questions、
  1,426 normalized-pixel groups、18/18 checkpoint。pooled \(V=-0.2212\)
  bits/token，95% CI `[-0.3067,-0.1348]`，仅 `2/18` 模型为正；预测方向 CI
  `4/9`，low/current/high 各 `2/3`。触发 immutable plan 的 pooled/positive-model
  否定项。
- **What Agent has already frozen**: `VISCOND-01=PROXY_REJECTED`；\(V\) 只称
  操作性条件增量，不称互信息、正式视觉风险或因果中介。不得换 prompt、答案文本、
  subset、proxy、benchmark 或新增 seed rescue，也不得基于该失败 gate 启动原
  `OBJ-01` 训练；视觉条件信息机制仍开放。
- **Whether autonomous work can continue**: 可以；已转入 `LITMAP-02`，以三条失败
  证据约束新的训练时跨模态监督/优化 mechanism 搜索，不触发 `HARD_STOP`。
- **Recommended human decision**: 无需立即决定；之后审查时重点确认 negative
  pooled \(V\) 的构念边界和局部 `6/9` 不应升格的联合判定逻辑。

## 2026-08-07｜VISSUP-01：visually necessary 具体 instantiation 被否定

- **Date**: 2026-08-07
- **Idea / issue**: 相同 rotated pixels/labels/steps 下，9.16%
  visual-necessary rotation instruction 是否比文本泄露 label 的 control 使
  4,096-coordinate MiniMind-V 学到可迁移视觉结构。
- **Why human should review it**: 文献中 V-GIFT 的较大模型、多 seed positive 没有
  迁移到当前低维模型；必须防止把单一 CV margin 正方向当作成功，忽略预声明
  rotation mechanism 与外部 accuracy 均为负。
- **Current evidence**: root `43101` paired training 全部工程/配对门通过。rotation
  control/visual accuracy=`0.25198/0.24504`，Δ=`-0.00694`、95% CI
  `[-0.03770,0.02282]`；CV-Bench-2D=`0.35466/0.35327`，Δ=`-0.00139`、
  95% CI `[-0.04242,0.04033]`。CV margin Δ=`+0.00284 bits/token`，但不足以覆盖
  两项主 accuracy 失败。
- **What Agent has already frozen**: `VISSUP-01=INSTANTIATION_REJECTED`；只否定
  当前 9.16% rotation、4,096-coordinate、frozen encoder/adapter setting。不补
  `43102/43103`，不换 rotation task、ratio、prompt、metric、subset 或 benchmark
  rescue；objective design 一般作用仍开放；raw scores、coordinates、
  training/scoring receipts 和 logs 全部保留。
- **Whether autonomous work can continue**: 可以；转入 `LITMAP-03`，检索低维
  visual trainability / module allocation / objective routing 的真正不同机制。
- **Recommended human decision**: 无需立即决定；后续审查时确认结论限制为当前
  低维/frozen-encoder setting，不外推为“视觉自监督一般无效”。

## 2026-08-07｜LITMAP-03：选择 fixed-total projector allocation 路线

- **Date**: 2026-08-07
- **Idea / issue**: `VISSUP-01` 失败后，文献是否支持一个不换 task/ratio/proxy、
  能区分 frozen-encoder identifiability 与 module-allocation capacity 的唯一最小
  candidate。
- **Why human should review it**: ACL 2024 PEFT/CROME 更支持 connector 或 pre-LLM
  adapter，Cambrian-1 则支持 vision encoder unfreezing；公开研究没有匹配
  trainable parameter count，因此本地 `1/4094/1` 方向是可证伪迁移，不是文献已证
  结论。
- **Current evidence**: 五族检索 541 raw records / 480 unique titles，核查 11 篇
  primary sources；三篇独立 autoregressive-LVLM direct sources 证明 module
  placement 重要但方向不闭合。本地 current 与 projector-dominant 均为 4,096
  coordinates、22 个 factor mappings、无 unused coordinates。
- **What Agent has already frozen**: 只登记 `PROJALLOC-01`；pilot 比较 current
  `582/2327/1187` 与唯一正维极端 `1/4094/1`。不换成 vision-heavy、不搜索比例、
  不运行旧 9-point/72-run sweep，也不以该结果翻转
  `VISSUP-01=INSTANTIATION_REJECTED`。
- **Whether autonomous work can continue**: 可以；另建 immutable plan 后以 fresh
  root `43201` 运行 paired pilot，阳性才补 `43202/43203`。
- **Recommended human decision**: 无需立即决定；之后审查 fixed-total
  intervention 是否充分隔离 module allocation，以及结论是否严格限制在当前
  frozen-base / hashed-coordinate setting。

## 2026-08-07｜PROJALLOC-01：exact fixed-total projector instantiation 被否定

- **Date**: 2026-08-07
- **Idea / issue**: 在总 4,096 coordinates 固定时，把 allocation 从 current
  `582/2327/1187` 改为 projector-dominant `1/4094/1`，是否能使相同
  visual-necessary signal 进入模型并外部迁移。
- **Why human should review it**: rotation accuracy 有 `+1.29 pp` 小幅正点估计，
  但远低于预注册 `+5 pp`、CI 跨 0、absolute accuracy 仍低于 0.30；同时完整
  CV-Bench accuracy 与 margin 都反向。必须防止只报告 mechanism 点估计而忽略联合
  support gate 和外部退化。
- **Current evidence**: root `43201` 两条件各 `2,064/2,064` steps，所有 paired
  engineering invariants 通过。rotation current/projector=`0.25099/0.26389`，
  difference=`+0.01290`、95% CI `[-0.02083,0.04563]`；CV-Bench=
  `0.35257/0.33866`，difference=`-0.01391`、95% CI
  `[-0.03964,0.01113]`，margin difference=`-0.05817 bits/token`。六项 pilot
  criteria 只有 paired invariants 通过。
- **What Agent has already frozen**: `PROJALLOC-01=INSTANTIATION_REJECTED`；不得
  运行 `43202/43203`、改变 allocation、追加 seed、换 metric/proxy、运行旧
  9-point sweep，也不得据此恢复 `VISSUP-01`。结论只适用于当前 frozen-base、
  hashed-coordinate、visual-necessary setting；其他 module-placement regime、
  frozen-feature identifiability 与 objective mismatch 仍开放。
- **Whether autonomous work can continue**: 可以；转入 `LITMAP-04`，检索
  objective competition / gradient routing、task-specific absorption 与
  frozen-feature/AR-objective mismatch 的真正不同机制。
- **Recommended human decision**: 无需立即决定；之后审查 paired allocation 是否
  隔离了预期 capacity 因素，并确认外推边界不被扩大成“frozen encoder 不可读”或
  “objective competition 已成立”。

## 2026-08-07｜LITMAP-04：objective-routing 本地最小干预 bridge 被否定

- **Date**: 2026-08-07
- **Idea / issue**: direct autoregressive-LVLM objective-routing /
  task-specific-absorption evidence 是否能唯一落到本地 single-factor、no-sweep
  最小干预。
- **Why human should review it**: 文献中存在多项 direct positive mechanisms，但其
  原始设置同时改变 component、teacher/tokenizer/head、loss、layer/rank/ratio、
  training stage 或计算资源；必须防止把“方法有效”误写成“可在本项目单因素验证”，
  也不能反向把 bridge failure 写成上位机制失败。
- **Current evidence**: 555 raw records、523 unique titles、14 篇决定性 primary
  sources 全文/appendix 核查，source hashes 通过。Direct evidence 与 matched
  control 门通过，unique local intervention 门失败；结果 commit `872657d`。
- **What Agent has already frozen**: `LITMAP-04=BRIDGE_REJECTED`；只否定当前
  literature-to-local-minimal-intervention bridge。不从已核查路线中任挑 component
  或 sweep 超参数训练；objective competition、gradient routing、task-specific
  absorption 与 frozen-feature/objective mismatch 仍开放。
- **Whether autonomous work can continue**: 可以；转入 `LITMAP-05`
  frozen-feature sufficiency / identifiability gate，先冻结 immutable plan。
- **Recommended human decision**: 无需立即决定；之后可审查 14-paper applicability
  matrix 与 no-sweep local-feasibility gate 的边界。

## 2026-08-07｜LITMAP-05：frozen-feature identifiability bridge 被否定

- **Date**: 2026-08-07
- **Idea / issue**: formal probing/decodability theory、direct LVLM evidence 与
  MiniMind-V architecture 是否能共同唯一固定一个有可靠正负推断边界的
  frozen-feature readout。
- **Why human should review it**: 文献明确支持“内部表示可读而最终回答失败”是一种
  可能现象，但所有 formal objects 与 direct protocols 都依赖 family、target、
  layer、token、pooling、regularization 或 selection choice；必须避免把
  `NO_CANDIDATE` 外推为“frozen encoder 没有信号”。
- **Current evidence**: 553 raw records、491 unique titles、13 篇决定性 primary
  sources 与 exact local interface 全部可核查；source hashes 和 deterministic
  index rebuild 通过。Formal family/target/regularization 不唯一，direct LVLM
  studies 使用 layer/token/pooling/LR 或 max-over-layer selection，负 probe 无
  completeness；0 GPU、0 checkpoint inference、0 training。
- **What Agent has already frozen**: `LITMAP-05=BRIDGE_REJECTED`；只否定当前
  frozen-feature identifiability bridge。不得用 layer/pooling/probe/metric sweep
  反向制造 bridge；feature signal、downstream absorption/transfer、objective
  mismatch、encoder limitation 均开放。
- **Whether autonomous work can continue**: 可以；转入 `COVER-01`
  authoritative controlled-coverage gate，先提交 immutable plan。
- **Recommended human decision**: 无需立即决定；之后审查 asymmetric negative
  inference boundary 是否足够保守，以及 13-paper matrix 是否遗漏真正的
  completeness theorem。

## 2026-08-07｜COVER-01：broad-label controlled-coverage bridge 被否定

- **Date**: 2026-08-07
- **Idea / issue**: authoritative broad source/domain/task labels 与 current
  MiniMind/ALLaVA lineage 是否能唯一构造 complementary coverage versus
  same-domain redundancy，并冻结一个 generative held-out target。
- **Why human should review it**: 保存的 169 个 official ALLaVA captions 全部能映射
  到 local parquet，推翻了“schema 无 ID 即 lineage 完全不可恢复”的过强说法；
  但 sample 又暴露 3 个 duplicated VFLAN IDs。必须同时避免低估可恢复性和把 sample
  reconstruction 外推成 full exact lineage。
- **Current evidence**: 442 raw records、380 unique titles、14 篇决定性 primary
  sources；fresh-temp deterministic index byte-identical。Direct generative studies
  依赖 ratio/category/target search 或复合 curation；DomainNet 的 clean control
  仅认证 CLIP。Local parquet 与官方 revision/tree 的 size/hash 完全一致，
  169/169 official assistant texts exact-match，full/translated lineage 未证明。
- **What Agent has already frozen**: `COVER-01=BRIDGE_REJECTED`；只否定当前
  broad-label-to-local-single-factor bridge。不否定 coverage/diversity、
  Vision-Flan task diversity、source transfer 或未来 factorial experiment；不把
  结果写成 `MECHANISM_REJECTED`。
- **Whether autonomous work can continue**: 可以；转入 `CROSSFACT-01`，
  只核查同一 image/acquisition unit 上 publisher-defined crossed text/task cells，
  plan commit 前不执行新分析。
- **Recommended human decision**: 无需立即决定；之后审查 official duplicate-ID
  handling、license boundary 与 broad-label confounding scope 是否表述准确。

## 2026-08-07｜LITMAP-06：选择 XID-01 作为新的科学机制主线

- **Date**: 2026-08-07
- **Idea / issue**: 三条初始搜索起点共同暴露
  `cross-modal interaction identifiability under autoregressive supervision`：
  observed support 上多个低 NLL 条件规则可能只在 unseen multimodal cells 分歧。
- **Why human should review it**: 该 formulation 有潜在论文价值，但也可能退化为普通
  no-free-lunch/support mismatch。后续必须证明 VLM-specific interaction 与
  language-shortcut ambiguity 增加了什么正式内容，不能只换名复述组合泛化。
- **Current evidence**: LITMAP-06 搜索 3,479 records、2,395 unique titles，核查
  10 篇决定性 primary sources；text bias、cross-modal skill-composition gap、
  controlled support-arrangement effects均有直接证据，但没有兼容 theorem 覆盖
  discrete AR conditional predictors。5/5 DOI verification 通过。
- **What Agent has already frozen**: `XID-01=ACTIVE_CONJECTURE`；首先做 finite
  support theorem/proof 与 exhaustive verification。当前不运行真实模型训练，不把
  predictor-equivalence diameter 当经验 proxy，不访问 final confirmation。
- **Whether autonomous work can continue**: 可以；按规则创建并提交
  `XID-01_round1` immutable plan 后直接继续。
- **Recommended human decision**: 无需立即决定；之后重点审查 theorem 是否超出
  普通 distribution-shift impossibility，以及新 prediction 是否可在不制造新 gate
  的条件下转入 MiniMind-V。

## 2026-08-07｜XID-01：finite theory bridge 成为 PROMISING candidate

- **Date**: 2026-08-07
- **Idea / issue**: round1 matched-support proposition 与 round2 finite-class
  target-risk decomposition 均通过，正式区分 source-target alignment 与 exact
  source-minimizer interaction-identification diameter。
- **Why human should review it**: theorem algebra 和 finite-class concentration 本身
  不是 VLM-specific；论文潜力取决于能否从 interaction-diagnostic support /
  separation 推出可验证的 \(I_{S\to U}\) 控制，而不是只定义 target-risk term。
- **Current evidence**: round1 redundant minimax target error=`0.5`，identifying
  unique NLL gap解析/枚举一致；round2 1,147,625 risk tables、1,530,375 ERM cases、
  0 violations，并精确恢复 round1。
- **What Agent has already frozen**: `XID-01=PROMISING` 仅指 theory bridge。真实
  LVLM mechanism 未验证；禁止把 target-risk terms 当 checkpoint proxy，禁止立即
  启动模型训练。
- **Whether autonomous work can continue**: 可以；下一轮预注册 diagnostic mass
  \(\lambda\)、separation \(\gamma\)、base shortcut advantage \(\beta\) 与
  estimation radius 的 prediction theorem。
- **Recommended human decision**: 无需立即决定；之后审查 separation theorem 是否
  真正产生“diagnostic support vs redundant sample count”的新预测。
