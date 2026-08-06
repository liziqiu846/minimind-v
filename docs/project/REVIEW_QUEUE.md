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
