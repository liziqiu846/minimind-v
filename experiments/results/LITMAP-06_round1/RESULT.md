# LITMAP-06 Round 1 Result

## 当前科学问题

在已有 proxy、intervention 和 theory-bridge 失败之后，哪一个真正 VLM-specific
的上位机制最值得成为新的 Active Research Question？

## 假设

至少一个上位机制应同时具有未被现有理论关闭的 autoregressive-LVLM 缺口、能解释
已有失败边界、产生新可证伪 prediction，并自然连接理论对象和训练原则。

## 本轮实验

四族定向检索汇总 3,479 records、2,395 unique titles，并完整核查 10 篇决定性
primary sources。比较 AR visual-credit competition、cross-modal composition、
joint support coverage 以及由三者合流产生的 cross-modal interaction
identifiability；本轮没有 checkpoint、GPU 或训练。

## 判定标准

- **支持**：VLM-specific novelty、未关闭的具体理论缺口、新 prediction、已有失败的
  合法重解释、候选理论对象和算法出口同时存在。
- **否定**：相容理论已解决、与受控反例冲突、只能产生 gate/proxy/audit，或算法
  出口只是无机制调参。
- **无法判断**：决定性全文/定理/venue 无法核实，或候选 expected value 仍相同且无
  低成本区分事实。

## 执行结果

- `Words or Vision` 和 PMR 支持 modality competition，但现有理论止于
  pure-text/multimodal mixture 或分类融合，未覆盖多模态样本内部 language shortcut
  对同一 next-token target 的解释竞争。
- ComPABench 显示 individual skills 很高仍可伴随极低的跨模态组合表现；一般 CG
  theory 明确需要 task-specific assumptions，并将 interdependent “generative
  effects” 留作开放问题。
- 受控 CLIP 研究显示相同规模下 support arrangement 会改变组合/域泛化；同时
  constituent frequency 能预测一类 object-combination retrieval，否定“所有组合都
  必须见过 joint cell”的过强版本。
- 对比学习 identifiability theorem 证明连续生成机制下 shared content 可被
  block-identify，但其 contrastive objective、连续可逆 latent、content invariance
  和已知维度不覆盖离散 autoregressive conditional risk。
- 三条证据合流为更强候选：
  **cross-modal interaction identifiability under autoregressive supervision**。
  当 observed support 上多个条件预测规则都可达到低 NLL，而语言 shortcut 与真实
  image–text interaction 只在未见组合上分歧时，训练目标本身不必识别可迁移规则。
- 该候选不是旧 `COMP-01` 换名：旧路线测试 frozen caption-NLL proxy；新问题研究
  training support 上低风险条件预测器的等价类及 target-support divergence。
- 新 prediction 已形成但尚未查看结果：在 \(N\)、factor marginals、target format
  和模型类匹配时，增加能区分 shortcut rule 与 intended interaction rule 的 support
  cells，应比增加 observationally redundant cells 更能降低 unseen-combination
  risk。
- 决定性全文、定理假设和官方 venue 均可核实，因此不是 `INCONCLUSIVE`。

## 结论

选择 `XID-01`（cross-modal interaction identifiability）为新的
`SCIENTIFIC_MECHANISM` 与 Active Research Question，证据标签仅为
`CONJECTURE` + `EMPIRICAL_SUPPORT`。下一步首先定义等价类并证明最小有限支持命题；
当前证据不授权真实模型训练或声称已有泛化规律。

## 下一步

冻结 `XID-01_round1`：构造匹配样本数与边际暴露、只改变 interaction-identifying
support 的最小二元 autoregressive problem，先给出 theorem/proof 和 exhaustive
verification，再决定是否存在合法的 MiniMind-V prediction test。

## 状态

`CONTINUE`
