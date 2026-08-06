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
