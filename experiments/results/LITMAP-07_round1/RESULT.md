# LITMAP-07 Round 1 Result

## 当前科学问题

`XID-01` 的 population-identifying support 没有形成 shared cross-key rule；这是
answer-only autoregressive visual credit 没有形成共享视觉状态，还是
representation/trainability ceiling？

## 假设

若失败暴露了可推进的 neural mechanism，primary literature 应给出
supervision/objective → shared visual update or task-specific absorption → unseen
composition risk 的可核查链，并产生能与 representation ceiling 区分的预测。

## 本轮实验

16 个冻结 query family/backend 组合获得 2,455 raw records、1,242 unique titles；
全文核查 11 篇 primary sources。本轮 0 GPU、0 checkpoint、0 training，未访问 final
confirmation，也未生成图。

## 判定标准

- **支持**：至少两个独立 direct/formal sources、可解释 chance 与 reversal 的可能性、
  能区分 credit/factorization 和 trainability、可本地验证且有算法出口。
- **否定**：只能重述 XID failure，或必须通过 layer/rank/ratio/proxy/metric search。
- **无法判断**：决定性全文不可用，或完整提取后机制仍观察等价。

## 执行结果

- Park et al. 在生成式 VLM 的 matched text/image tasks 上显示：显式
  image-to-text supervision 改善 simple-to-hard image generalization；其
  Theorems F.1/F.2 将 update alignment 与 infinitesimal held-out loss change
  联系起来，但没有证明 shared-rule recovery。
- `Words or Vision` 独立显示 matched-size training mixture 可降低 text-over-image
  bias；OGM-GE 与 PMR 证明多模态 fused objective 中弱模态 under-optimization 是
  可干预现象，但其分类 setting 不能直接外推到 AR rule formation。
- Cambrian-1 与 Idefics2 的受控研究显示 vision encoder、connector preparation、
  frozen/unfrozen state 与 trainable degrees of freedom 会显著改变视觉能力，因此
  representation/trainability ceiling 不能被排除。
- Daunhawer et al. 只在 asymptotic contrastive global optimum 下
  block-identify shared content；一般 compositional theory 也没有闭合 AR
  optimization bridge。这个缺口是具体、非平凡并值得建立的新理论，而不是放弃理由。
- 唯一通过的候选为 `VSTATE-01`：
  **shared visual-state mediation of autoregressive gradients**。其预测是：在固定
  pixels、support、coordinates 与最终 answer target 时，key-invariant visual-state
  supervision 应同时改善 explicit state prediction、完整 cross-key rule 与
  unseen composition；若 state 不可表示，则这些效应共同失败。
- `XID-01_round4` 的反转不计作支持证据；它只限定下一实验必须检验完整 rule panel，
  不能只看 held-out key `e`。

## 结论

选择 `VSTATE-01` 为新的 `SCIENTIFIC_MECHANISM` 与
`ACTIVE_CONJECTURE`。它把宽泛的 factorization 问题收缩为一个 theory-first
optimization bridge，同时保留 frozen representation/trainability ceiling 为明确的
竞争解释。

## 下一步

冻结 `VSTATE-01_round1` 理论计划：在最小 factorized autoregressive model 中证明
answer-only key-wise visual gradients何时抵消，以及 key-invariant state target
何时提供 non-cancelling shared update；先做解析证明和 exhaustive verification，
不立即训练新模型。

## 状态

`CONTINUE`
