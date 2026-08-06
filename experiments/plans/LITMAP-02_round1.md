# LITMAP-02 Round 1 — 失败驱动的训练时跨模态机制 gate

**日期**：2026-08-07  
**阶段**：阶段三  
**类型**：预注册 primary-source 文献/理论筛选与新 candidate 生成；不训练、不访问
final confirmation set  
**不可变性**：本文件提交后不修改判定标准；如需修订，创建新 round。

## 科学问题

在 `COMP-01` 的生成 likelihood 关系判别、`XMC-01` 的冻结表示—风险理论桥和
`VISCOND-01` 的 correct-image vs no-pixel 条件增量均未形成稳定机制后，现有权威和
前沿文献中是否存在一个以 autoregressive VLM 训练时跨模态监督信息或优化动力学为
核心、能够由最小受控干预区分竞争解释的泛化机制？

## 假设

假设 H：至少存在一个不是任意 checkpoint proxy 重命名的训练时机制，使视觉条件
对目标的独特预测信号在 next-token 优化中被语言捷径、目标不平衡或数据构造系统性
削弱；可靠文献应当为它提供明确对象、方向性干预和未见视觉任务预测。

若文献只能说明“加入某个 loss / 更多视觉数据通常有效”，却不能区分该机制与普通
hard-example reweighting、额外算力、语言正则化或数据规模，则 H 在本轮覆盖范围内
不成立。

## VLM 特有性

候选对象必须依赖图像条件与文本目标之间的训练关系，例如：

- 视觉条件相对文本上下文对 autoregressive target 的独特监督是否被学习；
- 视觉 token / projector 与语言路径在同一生成目标中的非对称优化；
- 图文数据构造如何改变模型必须使用视觉证据的程度。

单模态 gradient norm、通用 loss landscape、普通压缩或把 vision/projector/language
模块名机械拆开，不构成 VLM 特有机制。不得恢复已否定的 gradient-replacement
\(D_I\)。

## 可证伪预测

至少一个保留候选必须在正式登记时给出如下形式的 prediction：

> 相同初始化、数据 draw、训练步数和主要算力下，hypothesis-specific intervention
> 应改变预声明的跨模态训练机制量，并在一个未用于选择 intervention 的 development
> 视觉任务上产生方向明确的改善；若机制量未按方向改变，或改善可由预声明的简单
> baseline 同样解释，则否定该候选。

本轮文献 gate 本身的可证伪预测是：可以找到至少一个由 primary source 支持、满足
下述全部保留门的候选。若找不到，则不为了继续训练而登记模糊变体。

## 最小分析

1. 先复用 `LITMAP-01` 与 `XMC-01_round2` 已保存记录，列出已覆盖与已否定路线；
   不重复 broad search。
2. 只做三组定向检索：
   - autoregressive LVLM 的视觉 token under-utilization、language dominance、
     modality competition / gradient starvation；
   - visual instruction/pretraining data 中使回答必须依赖图像的 supervision
     informativeness、negative construction 或 counterfactual grounding；
   - 能连接 multimodal training dynamics 与 held-out/OOD risk 的正式或受控理论。
3. 优先 2022–2026 的 CVPR/ICCV/ECCV、NeurIPS/ICML/ICLR、ACL/EMNLP 及可核查的
   新预印本；更早工作只作为明确理论基础。所有新检索响应保存到 `sources/`，
   决定性论文保存版本、URL、SHA-256 和定理/实验定位。
4. 对决定判断的 primary source 逐篇核查：模型是否为生成式 LVLM、训练目标、
   intervention、控制变量、held-out 对象、是否区分简单 baseline、作者限制。
5. 输出 evidence/applicability matrix；本 autonomous cycle 最多再登记 2 个新
   candidate，且只能选择一个作为 ACTIVE。
6. 在登记 candidate 前做只读 artifact gate：确认现有 checkpoint/log/data 是否足以
   回答；若 checkpoint-only 足够，不训练；否则只能提出符合阶段三规则的
   2-condition × 1 paired-seed pilot，并先创建新的 immutable experiment plan。

## 支持标准

候选必须全部满足：

1. 至少一项直接研究 autoregressive/generative LVLM 的受控 primary evidence，或
   一项正式多模态训练理论加一项独立生成式 LVLM 验证；
2. 文献对象明确到足以唯一规定 mechanism-specific measurement 或 intervention，
   不需要 sweep layer、proxy、loss、lambda、数据 subset 后挑结果；
3. 给出独立于 held-out error 本身的方向性机制 prediction；
4. 能预声明一个简单竞争 baseline，至少排除“普通 hard-example reweighting /
   额外 token loss / 更多有效 batch compute”之一；
5. 最小测试可由现有 artifact 或本服务器资源内的 paired pilot 完成，不访问 final
   confirmation，不改变数据统计关系；
6. 支持时能自然导出 objective、sampling、data construction 或 optimization 原则。

全部满足才可登记为 `NEW` 并进入下一 immutable experiment plan；文献支持本身不得
升格为 `PROMISING`。

## 否定标准

满足任一项即淘汰相应路线：

1. 证据仅来自 CLIP/dual-encoder classification 或 retrieval，且没有合法生成式
   LVLM 桥；
2. 机制只能通过复用 `COMP-01` caption NLL、`VISCOND-01` no-pixel ablation 或
   `XMC-01` 无桥 representation proxy 来测量；
3. intervention 实质只是增加 loss 权重、训练 token、数据量或算力，无法与简单
   baseline 区分；
4. 需要事后挑 benchmark、prompt、layer、proxy、lambda 或 seed；
5. 无法产生未查看对象的方向性 prediction，或算法出口只是“增大模型/数据”；
6. 需要访问 final confirmation、改变统计关系或明显扩大资源。

若所有路线被否定，`LITMAP-02` 记为 `REJECT_IDEA`，保留失败地图，并在 Research
Envelope 内开启下一 autonomous cycle；不得因此 `HARD_STOP`。

## 无法判断标准

只限：

1. 决定性论文全文/appendix 不可获得，无法核查关键对象；
2. 文献提出机制但没有足够控制实验，且本地 artifact 也无法区分竞争解释；
3. 唯一合法测试需要明显超出当前资源或改变冻结统计关系。

`INCONCLUSIVE` 不自动获得训练预算；相关路线写入 `REVIEW_QUEUE` 后转向其他候选。

## 可能混杂

- 把视觉 benchmark 提升等同为模型更使用视觉；
- 把 gradient magnitude 当成视觉信息量或因果贡献；
- 把额外辅助 loss 的收益误归因于特定机制，而非额外监督/compute；
- 用同一 development task 选择 intervention 又验证 prediction；
- 将 modality competition 的分类理论直接外推到 autoregressive generation；
- 最新预印本缺少同行评审或公开代码；
- 检索接口相关性排序和负结果发表偏差。

## 所需资源

- 本轮文献 gate GPU：0；
- 网络：优先 `research-lookup` 指定的学术搜索；服务器后端缺失时使用 arXiv、
  OpenAlex、Crossref 和官方论文/代码公共端点；
- 输出：全部新响应保存到 `sources/`，决定性 source 与 evidence matrix 归档；
- 本轮不训练、不访问 final confirmation；
- 若筛出候选，训练资源必须在下一 candidate plan 中单独预注册。
