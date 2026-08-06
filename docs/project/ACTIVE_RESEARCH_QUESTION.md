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

> 在相同训练数据、预算和 seed 下，较短的共享结构若真实性能更差，是否是因为它
> 更弱地保留了对象关系与词序所定义的跨模态组合绑定？

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
- **Status**: ACTIVE。
