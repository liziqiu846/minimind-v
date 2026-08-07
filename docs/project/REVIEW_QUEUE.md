# Asynchronous Human Review Queue

重要事项写入此队列并冻结相关结论。除非同时触发 `HARD_STOP`，队列中存在事项
不得停止 Research Envelope 内其他已授权工作。

## 2026-08-07｜XMC-01：纯数据机制已局部排除，模型保持桥待验证

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
- **Why human should review it**: 真正验证需要重新训练，今晚授权明确禁止。
- **Current evidence**: CoCa/MM1/Prismatic/SigLIP 及 Kempf/DataComp 的文献证据；
  尚无 MiniMind-V prediction test。
- **What Agent has already frozen**: 两个方向均保持 `NEW`，不升格、不训练。
- **Whether autonomous work can continue**: 可以继续其他 checkpoint-only candidate。
- **Recommended human decision**: 仅在 checkpoint-only prediction test 形成稳定规律后，
  再决定是否批准最小训练实验；正式算法主实验仍需 `HARD_STOP`。

后续每条记录至少包含：

## YYYY-MM-DD｜Idea / issue

- **Date**:
- **Idea / issue**:
- **Why human should review it**:
- **Current evidence**:
- **What Agent has already frozen**:
- **Whether autonomous work can continue**:
- **Recommended human decision**:

## 2026-08-07｜COMP-01：外部组合 binding prediction 被否定

- **Date**: 2026-08-07
- **Idea / issue**: 标准 What’sUp controlled panel 上，生成式 caption+EOS NLL
  binding margin 是否解释 M2/M3 development 风险排序。
- **Why human should review it**: 这是首个真正未查看外部模型 prediction test；结果
  否定当前 bridge，同时揭示生成 NLL 几乎被 pair 内同-caption 偏好支配。
- **Current evidence**: 18/18 checkpoint、410 pairs、205-cluster bootstrap；
  sign concordance `5/9`，仅 `1/9` 预测方向 CI 不跨 0，low/current/high 分别
  `1/3,3/3,1/3`。触发 immutable plan 的 `≤5/9` 否定标准。
- **What Agent has already frozen**: `COMP-01=REJECTED`；不得挑 current budget、
  更换 panel/proxy、追加模型或训练来 rescue。保留 raw 四格 NLL、运行回执和
  bootstrap 判定。
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
- **What Agent has already frozen**: `XMC-01=REJECTED`；不得 sweep
  layer/pooling/kernel/rank/proxy，不把 contrastive/linear-probe theorem 直接套到
  autoregressive semantic risk。
- **Whether autonomous work can continue**: 可以；已转向 `VISCOND-01`，不触发
  `HARD_STOP`。
- **Recommended human decision**: 无需立即决定；之后可审查 theorem applicability
  matrix。若未来要恢复 XMC，必须提供新的生成式风险证明或真正新 artifact，而不是
  更换经验表示指标。

## 2026-08-07｜VISCOND-01：MMStar correct-image vs no-pixel 构念门被否定

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
- **What Agent has already frozen**: `VISCOND-01=REJECTED`；\(V\) 只称操作性条件
  增量，不称互信息、正式视觉风险或因果中介。不得换 prompt、答案文本、subset、
  proxy、benchmark 或新增 seed rescue，也不得基于该失败 gate 启动原 `OBJ-01`
  训练。
- **Whether autonomous work can continue**: 可以；已转入 `LITMAP-02`，以三条失败
  证据约束新的训练时跨模态监督/优化 mechanism 搜索，不触发 `HARD_STOP`。
- **Recommended human decision**: 无需立即决定；之后审查时重点确认 negative
  pooled \(V\) 的构念边界和局部 `6/9` 不应升格的联合判定逻辑。

## 2026-08-07｜VISSUP-01：visually necessary paired pilot 被机制门否定

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
- **What Agent has already frozen**: `VISSUP-01=REJECTED`；不补
  `43102/43103`，不换 rotation task、ratio、prompt、metric、subset 或 benchmark
  rescue；raw scores、coordinates、training/scoring receipts 和 logs 全部保留。
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
  不运行旧 9-point/72-run sweep，也不以该结果翻转 `VISSUP-01=REJECTED`。
- **Whether autonomous work can continue**: 可以；另建 immutable plan 后以 fresh
  root `43201` 运行 paired pilot，阳性才补 `43202/43203`。
- **Recommended human decision**: 无需立即决定；之后审查 fixed-total
  intervention 是否充分隔离 module allocation，以及结论是否严格限制在当前
  frozen-base / hashed-coordinate setting。

## 2026-08-07｜PROJALLOC-01：fixed-total projector-capacity 解释被否定

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
- **What Agent has already frozen**: `PROJALLOC-01=REJECTED`；不得运行
  `43202/43203`、改变 allocation、追加 seed、换 metric/proxy、运行旧 9-point
  sweep，也不得据此恢复 `VISSUP-01`。结论只适用于当前 frozen-base、
  hashed-coordinate、visual-necessary setting。
- **Whether autonomous work can continue**: 可以；转入 `LITMAP-04`，检索
  objective competition / gradient routing、task-specific absorption 与
  frozen-feature/AR-objective mismatch 的真正不同机制。
- **Recommended human decision**: 无需立即决定；之后审查 paired allocation 是否
  隔离了预期 capacity 因素，并确认外推边界不被扩大成“frozen encoder 不可读”或
  “objective competition 已成立”。
