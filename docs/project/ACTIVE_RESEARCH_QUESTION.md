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

> 在生成 NLL 关系绑定、无桥表示保持量和 correct-image vs no-pixel 条件增量均未
> 形成稳定机制后，是否存在一个以训练时跨模态监督信息或优化动力学为核心、具有
> 权威机制证据且能由最小受控干预区分竞争解释的 VLM 泛化候选？

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
- **Status**: REJECTED_AS_ACTIVE；完整外部 prediction test 仅 5/9 sign concordance、
  1/9 预测方向 CI 不跨 0，触发预注册否定。

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
- **Status**: REJECTED_AS_ACTIVE；13 篇 primary-source/appendix audit 未找到从冻结
  autoregressive LVLM 表示到未见语义风险的唯一量。最强结果分别止于 contrastive
  retrieval/linear probe、linear-Gaussian dual-encoder conditional 或机制性
  UFM；继续需要 layer/kernel/rank/proxy 选择，触发预注册否定。

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
- **Status**: REJECTED_AS_ACTIVE；官方 MMStar 1,496 eligible items、1,426 独立
  image groups、18/18 checkpoint 的 pooled correct-image vs no-pixel \(V\) 为
  `-0.2212` bits/token，95% CI `[-0.3067,-0.1348]`，仅 `2/18` 模型为正。虽有
  `6/9` pair 方向一致和 `4/9` 预测方向 CI，但已触发预注册构念否定；不得换
  prompt、答案形式、subset、proxy、benchmark 或 seed rescue。

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
- **Status**: ACTIVE_LITERATURE_GATE；当前只允许创建并 commit `LITMAP-02`
  immutable plan，然后检索和筛选。不得因“训练可能有效”直接启动实验。
