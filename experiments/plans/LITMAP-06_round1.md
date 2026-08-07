# LITMAP-06 Round 1 — failure-informed scientific-mechanism reselection

**日期**：2026-08-07  
**阶段**：阶段三，`EXPLORATION MODE`  
**角色**：`LITERATURE_SCREEN`，不是 `SCIENTIFIC_MECHANISM`  
**证据上限**：`EXPLORATORY_SIGNAL`；本轮不能建立机制、因果规律或正式 theorem

## 科学问题

在 `COMP-01`、`VISCOND-01` 的 proxy failure，`VISSUP-01`、
`PROJALLOC-01` 的 instantiation failure，以及 `XMC-01`、`LITMAP-04/05`、
`COVER-01` 的 bridge failure 之后，哪一个真正 VLM-specific 的上位机制具有最高
scientific expected value，值得成为新的 Active Research Question？

本轮搜索起点是三个上位机制，不把它们视为固定答案：

1. **AR visual-credit competition**：autoregressive target 在文本上下文已经容易
   预测时，是否系统性削弱学习可迁移视觉依赖的收益或 credit，使低 next-token
   loss 与未见数据视觉泛化脱钩？
2. **Cross-modal compositional factorization**：训练数据包含对象、属性和关系的
   边际暴露时，为什么模型仍不能把它们组合成可迁移的 image–relation–text
   structure？
3. **Joint multimodal support coverage**：VLM 的有效样本量是否取决于
   image × concept × relation × linguistic realization × domain 的联合支持与连接，
   而不只是样本数或单边际多样性？

若权威文献与已有失败证据共同指向更强的上位机制，允许替换上述任一搜索起点，但
必须记录替换依据；不得用 metric、benchmark、audit、gate、readout 或参数分配策略
替换。

## 假设

> 假设 H：至少一个上位机制同时满足：（a）现有 LLM 理论遗漏了多模态特有对象；
> （b）现有 multimodal theory 尚未直接覆盖 autoregressive LVLM 的未见数据风险；
> （c）已有本地失败能被该机制重新解释而不复活已否定的 proxy/instantiation；
> （d）可提出一个非平凡、可证伪 prediction；（e）若成立可自然导出训练原则。

如果三条机制都已被权威工作直接解决、需要明显不合理的假设、与已有受控反例冲突，
或只能产生新的 proxy/gate 而不能产生科学预测，则 H 在当前候选集下不成立；应由
搜索暴露的缺口生成新的上位机制，而不是降低标准。

## VLM 特有性

三条起点分别依赖：

- image 与 language context 对同一 autoregressive target 的竞争性解释；
- 视觉实体/关系与语言实现之间的跨模态组合；
- 两个模态及其语义、关系和域因素的联合支持。

这些对象不能由只含 token sequence 的普通 LLM 样本量、语言边际或 checkpoint
code length 完整表达。

## 可证伪预测

### H1：AR visual-credit competition

若该机制成立，应存在受控证据表明：在视觉信息保持不变而文本侧 target
predictability / shortcut availability 改变时，可迁移视觉依赖或未见任务表现发生
方向明确的变化；单纯增加同类 token/steps 不能充分解释该变化。

### H2：Cross-modal compositional factorization

若该机制成立，应存在以下缺口或证据：即使训练覆盖相关边际概念，缺失交互关系或
factorized structure 仍造成 held-out multimodal composition error；该误差不能只由
词袋偏好、output format 或普通 domain shift 解释。

### H3：Joint multimodal support coverage

若该机制成立，应存在理论或受控实验区分相同/相近 \(N\) 与边际覆盖、但不同联合
支持结构的训练分布，并预测 unseen composition/domain risk 的方向；某个 graph
statistic 本身不被预先当作正式理论量。

## 最小文献分析

每个机制执行一个明确 scientific question 驱动的 targeted search：

1. `Why can autoregressive multimodal training minimize language loss while
   failing to learn transferable visual dependence?`
2. `What theory or controlled evidence explains cross-modal compositional
   generalization beyond marginal concept exposure?`
3. `Does multimodal generalization depend on joint support coverage or
   connectivity beyond sample size and marginal diversity?`

检索与核查规则：

- 首选 NeurIPS、ICML、ICLR、CVPR、ICCV、ECCV、ACL、EMNLP、NAACL、
  JMLR/PMLR 的 primary sources 和权威机构工作；
- 使用 arXiv、OpenAlex、Semantic Scholar/Crossref 与会议官方页面的至少三个互补
  索引；保存 query、日期、原始响应和 URL；
- 2025/2026 工作不因 citation 少自动排除；较老 foundational work 可按影响力纳入；
- 每个机制筛选少量决定性全文，实际核查 research question、formal statement、
  assumptions、proof structure、experiment protocol 与 limitations；
- 对每篇关键论文回答它解释什么、遗漏什么、为何不直接覆盖 autoregressive LVLM、
  需要增加什么理论对象，以及该缺口是否值得自行证明；
- `parallel-cli` 当前不可用且项目无 `PARALLEL_API_KEY`，本轮使用公开 API 与
  official full text fallback，并保留失败回执；不得伪造 citation count 或 venue；
- 生成一张 mechanism → existing theory → autoregressive-LVLM gap → prediction →
  algorithm 的研究缺口图，仅用于综合表达，不作为科学证据。

## Expected-value 选择标准

本轮不设“唯一 proxy / 唯一 intervention / 唯一数据格子”硬门。对候选作有依据的
定性比较：

1. VLM-specific novelty；
2. 是否尚未被直接解决；
3. 是否解释现有本地失败而不与 failure-scope ledger 冲突；
4. 是否能产生尚未查看、方向明确的 prediction；
5. 是否存在值得自行建立的新理论对象；
6. 是否能在 MiniMind-V 上以低成本区分竞争解释；
7. 是否有自然算法出口。

只选择一个最高 expected-value 机制作为 ACTIVE；其余进入 `NEXT` 或 `BACKLOG`。

## 支持标准

某机制可被选择为新的 ACTIVE，需要：

- 问题本身具有清楚的 VLM-specific novelty；
- 权威文献没有直接关闭该问题，且识别出具体 autoregressive-LVLM gap；
- 至少能提出一个非平凡、可证伪 prediction；
- 已有失败证据至少排除一个简单但错误的 operationalization，而不否定机制；
- 可看出候选 theoretical object 与 algorithmic implication。

这只支持“值得继续研究”，最高证据标签为 `CONJECTURE` 加文献支持；不升级
`PROMISING`。

## 否定标准

单个起点应降级或替换，如果：

- 已有权威理论在相容 assumptions 下直接解决核心问题；
- 所需新 bridge 依赖明显不合理或与 autoregressive LVLM 不对应的对象；
- 已有受控反例与其方向性 prediction 冲突；
- 无法产生区别于 metric/gate/audit 的 observable consequence；
- 算法出口只是无机制的调参或工程优化。

不得因为文献尚无完整 theorem 或本地没有完美 proxy 而否定机制。

## 无法判断标准

- 决定性论文全文/appendix 无法取得或版本/venue 无法核实；
- 三个机制在当前证据下 expected value 接近，且缺少一个低成本区分事实；
- 搜索结果只覆盖 CLIP/classification/dual encoder，无法判断 autoregressive LVLM
  extension 是否合理。

无法判断时记录缺失信息和下一条 targeted question；不得自动申请更多训练预算，
也不得转为 gate building。

## 可能混杂

- benchmark failure 与机制 failure 混用；
- 把 CLIP / classification theorem 直接套到生成式 LVLM；
- 把 gradient、probe、graph statistic 或 dataset schema 当成上位机制；
- 新论文尚未同行评审或 citation metadata 不稳定；
- 本地 MiniMind-V 低维/冻结设置限制被误写成一般 LVLM 规律；
- 只寻找支持候选的论文，忽略反例和 limitations；
- 用“文献未证明”错误替代“bridge 不可能”。

## 所需资源

- GPU / checkpoint / training：`0`；
- final confirmation：不访问；
- 网络：公开 scholarly APIs、会议官方页面、arXiv/作者公开全文；
- 磁盘：只保存文本/JSON/PDF 摘要与一张图；当前磁盘使用率 99.4%，不批量下载
  大型数据或无关 PDF；
- 时间：优先核查每条机制的决定性 primary sources，不做全领域 broad scan。

## 冻结声明

本计划提交后才执行新检索与全文分析。搜索可发现更好的上位机制，但不得事后修改
本计划的 expected-value、支持、否定或无法判断标准；需要改变标准时必须创建新的
round。现有 `CROSSFACT-01` 未跟踪 artifact 保留，不删除、不覆盖，也不因本轮
方向纠偏被解释成已完成 scientific result。
