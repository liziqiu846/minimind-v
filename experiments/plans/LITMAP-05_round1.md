# LITMAP-05 Round 1 — frozen-feature sufficiency / identifiability gate

**日期**：2026-08-07  
**阶段**：阶段三  
**类型**：LITMAP-04 failure-driven primary-source literature/theory gate；不训练、
不运行 checkpoint、不访问 final confirmation  
**不可变性**：本文件提交后不修改科学问题、query families、readout 接受门或判定
标准；修订必须创建新 round。

## 科学问题

`VISSUP-01` 与 `PROJALLOC-01` 两个不同的具体训练 instantiation 均未使 held-out
rotation 明显离开 chance，`LITMAP-04` 又没有找到可唯一落地的 objective-routing
最小干预。继续改变训练前，当前最小区分问题是：

> 是否存在一个由 architecture 与正式理论共同唯一固定、无需 layer/rank/pooling/
> probe/metric sweep 的 frozen-feature readout，能够检验当前 frozen visual
> representation 是否已包含 held-out rotation 所需信号，并区分：

1. **representation-absent**：任务相关信号没有保留在实际交给 projector 的 frozen
   visual output 中；
2. **representation-present but downstream-unabsorbed**：信号在该 output 中可由先验
   固定 readout 读取，但 projector / autoregressive decoder 没有吸收或迁移；
3. **readout-nonidentifiable**：某个 ad hoc probe 的失败只说明选定 hypothesis class
   不足，不能推出 representation 中不存在信号；
4. **task/interface mismatch**：readout 操作化依赖新的图像变换、prompt、subset 或
   label construction，无法裁决当前失败 setting。

本轮只审计是否存在合法 bridge，不执行本地 probing。若 bridge 成立，只登记一个
checkpoint-only candidate，并另建 immutable experiment plan。

## 既有失败证据与约束

本轮必须同时尊重：

- `VISSUP-01` root `43101`：rotation difference=`-0.00694`，95% CI
  `[-0.03770,0.02282]`；CV-Bench difference=`-0.00139`；
- `PROJALLOC-01` root `43201`：rotation difference=`+0.01290`，95% CI
  `[-0.02083,0.04563]`，absolute accuracy=`0.26389`；CV-Bench difference=
  `-0.01391`，margin difference=`-0.05817 bits/token`；
- `LITMAP-04=BRIDGE_REJECTED`：已核查 objective methods 不能唯一形成
  single-factor、no-sweep、本地可行的干预；
- `XMC-01=BRIDGE_REJECTED`：不得搜索 layer、pooling、kernel、rank、CKA/CCA/HSIC
  或其他无风险桥 representation proxy；
- `COMP-01` 与 `VISCOND-01` 的 caption-NLL / no-pixel proxies 不得复用；
- 不补 `43102/43103` 或 `43202/43203`，不改变 rotation task/ratio/prompt/data
  subset，不搜索 allocation、metric 或 probe。

任何新 readout 必须由本地结果查看前的 architecture/theory 决定，不能从多个 probe
中选择最漂亮者。

## 可证伪文献假设

假设 H：如果 frozen-feature sufficiency / identifiability 是当前可被低成本裁决的
VLM-specific explanation，primary literature 与本地 architecture 之间应存在至少
一条证据链，同时满足：

1. 明确研究 frozen visual representation 向 downstream decoder/task 传递的 signal，
   而非只研究通用 classifier representation；
2. 给出正式 proposition/theorem、architecture-native head，或训练目标唯一指定的
   readout，使 feature location、pooling、hypothesis class、regularization 与 metric
   不需要本地搜索；
3. 说明正 readout 能反驳哪种 representation-absence 命题，以及负 readout 在何种
   assumptions 下才有排除力；
4. 至少一篇 direct VLM/LVLM primary source 用 frozen encoder + matched downstream
   control 同时报告 readout/task signal 与外部或生成式 performance；
5. exact vision encoder/output interface 与本地 MiniMind-V 可只读核实，且
   checkpoint-only test 能区分 representation-absent 与 downstream-unabsorbed。

若文献只表明“linear probes 常有用”、需要遍历 layer/pooling/classifier/rank/
regularization，或负 probe 没有 completeness/impossibility guarantee，则 H 在本轮
严格 identifiability 门下不成立。

## 可证伪预测

若 H 成立，全文核查结束前应能唯一写出一个本地 readout specification，其中 exact
feature interface、pooling、hypothesis class、fit/regularization protocol、metric 与
正/负推断边界均由 architecture/theory 决定。该 specification 应产生方向明确的未查看
预测：

- 若 frozen output 含有 fixed-readout 可访问的 rotation signal，则预注册
  encoder-only held-out performance 应明显高于四分类 chance；
- 同时，已有 end-to-end LVLM near-chance 结果将反驳“signal 完全未进入 frozen
  output”，但仍不能单独裁决 objective competition；
- 若无法在查看本地 readout 结果前唯一写出该 specification，则本轮预测失败，必须
  `NO_CANDIDATE`，不得用实际结果反向选择 probe。

## 推断的不对称边界

本轮预先冻结以下逻辑：

- 在 bridge assumptions 成立时，**正向**固定 readout 可以反驳“该 frozen output
  完全没有该 readout 可访问的任务信号”；
- 正向 readout 加现有 LVLM near-chance 结果，只能定位为 downstream absorption /
  transfer 的证据，不能单独证明 objective competition 是原因；
- **负向**有限 probe 通常不能证明 signal 不存在；只有正式 completeness、
  sufficiency、injectivity/impossibility 结果且 assumptions 与本地 setting 同构时，
  才能赋予 representation-absence 排除力；
- 若没有这种理论，任何未来负结果最多否定当前 readout bridge，不得标记
  `MECHANISM_REJECTED`。

## VLM 特有性与理论边界

有效 bridge 必须连接：

\[
\text{image input}
\rightarrow
\text{实际 frozen visual output}
\rightarrow
\text{projector / autoregressive decoder 可访问性}
\rightarrow
\text{未见任务表现}.
\]

以下内容不能单独成为候选：

- 通用 self-supervised/CLIP linear-probe accuracy；
- 与本地不同 encoder、不同输入分辨率或不同 feature interface 的结果；
- layerwise attention、CKA、feature visualization 或 post-hoc separability；
- 只证明存在某个任意 measurable decoder 的信息论充分性；
- 只证明 linear separability、但未固定具体 readout family/training protocol；
- 通过换 augmentations、task labels 或 benchmark 构造得到的 positive。

任何 theorem/proposition 必须核查 data distribution、loss、representation map、
readout class、sample independence、optimization/estimation assumptions 与 certified
object；名称相似不构成 LVLM bridge。

## 检索协议

### Backend 顺序

遵守 `research-lookup`：

1. 先检查 `sources/` 与 LITMAP-02/03/04、XMC round2 的 saved results/title index，
   不重复付费或相同 query；
2. 检查 `parallel-cli`、`PARALLEL_API_KEY` 与 `OPENROUTER_API_KEY`；
3. backend 可用时，每个科学 query 做 academic-domain 与 general 两次
   `parallel-cli search`，全部用 `-o` 保存到 `sources/`；
4. backend 不可用时保存失败原因，使用 arXiv、OpenAlex、Crossref、
   OpenReview/conference proceedings、ar5iv 与 official repositories；
5. 保存 raw response、exact metadata、正文/appendix、URL/version 与 SHA-256。

不得安装或认证未授权付费 backend；不得只凭标题/摘要、搜索引擎 synthesis 或引用量
作 bridge 决定。

### Query families

首轮严格覆盖以下五族；exact-title verification 不计为新 family：

1. `frozen vision encoder` + `feature sufficiency / identifiability / recoverability /
   information preservation` + `multimodal language model`；
2. `vision-language model` + `linear probe / native readout / representation probing`
   + `frozen encoder / downstream decoder`；
3. `CLIP / SigLIP vision encoder` + `rotation / orientation / spatial relation /
   geometric transformation` + `linear separability / invariance`；
4. `representation sufficiency theorem / usable information / decodable information /
   probing completeness` + `vision / multimodal`；
5. `autoregressive LVLM / MLLM` + `frozen visual features / connector / projector` +
   `matched encoder probe / feature bottleneck / downstream absorption`。

不得扩展为 broad representation survey，也不得因某篇论文方便而切换到新的 task、
encoder 或 probe family。

### 时间与质量范围

- formal foundations 不限年份；direct LVLM evidence 优先 2023–2026；
- 首选 NeurIPS/ICML/ICLR/CVPR/ACL/EMNLP/ECCV 与正式 journal；
- 新预印本只在提供独特 direct control 或 formal bridge 时纳入；
- 目标不超过约 700 raw records，按 normalized title 去重；
- 全文/appendix 核查 8–14 篇决定性 primary sources。

## Evidence / applicability matrix

每篇决定性 source 至少记录：

- title、authors、year、venue/status、DOI/arXiv/version；
- model/encoder family、scale 与 autoregressive/dual-encoder/classifier 类型；
- representation 的 exact location、shape、pooling 与 preprocessing；
- readout hypothesis class、training data、regularization、selection 与 metric；
- readout 是否 architecture/theory 唯一固定，或依赖选择；
- matched encoder/downstream controls、seeds、datasets 与 external performance；
- theorem/proposition assumptions、proof idea 与 certified object；
- positive/negative readout 分别允许什么推断；
- 它支持/反对哪个 competing explanation；
- 它不能推出什么；
- 本地 exact-interface 与资源可行性；
- gate：`DIRECT_IDENTIFIABILITY`、`FORMAL_ADJACENT`、`HEURISTIC_ONLY` 或
  `REJECT_FOR_BRIDGE`。

venue/citation 只用于排序，不能替代全文 applicability 核查。

## 可能混杂

- encoder identity、revision、input resolution、normalization 或 patch/token interface
  与论文不一致；
- 论文 probe 读取的 layer/token 与本地 projector 实际输入不同；
- probe training data 泄漏 held-out 图像身份，或 train/test 只共享近重复图像；
- rotation label 可由边框、插值、EXIF、padding 等 preprocessing artifact 解码；
- 线性可读性来自新训练 probe 的容量，而非当前 projector/decoder 的可访问性；
- 正 probe 与 LVLM 失败使用不同分布、任务接口或评价单位；
- negative probe 被 optimization failure、regularization 或 sample size 限制，却被
  错误解释为 signal absent；
- 文献在多个 layer/pooling/readout 中事后选择最优结果。

任何未被 formal assumptions 与 matched protocol 控制的混杂，都阻止 bridge
升格；不能通过本地 sweep 补救。

## Candidate 接受门

最多保留一个新 candidate，且必须全部满足：

1. ≥1 个 formal primary source 唯一固定 readout 及其推断边界；
2. ≥1 个独立 direct VLM/LVLM primary source 在 frozen visual output 上提供 matched
   readout/downstream evidence；
3. exact representation location、pooling、readout family、training protocol、
   regularization 与 metric 无需本地选择；
4. 本地 MiniMind-V 的 vision encoder identity、preprocessing 与实际
   projector-input interface 可只读核实；
5. checkpoint-only test 能至少反驳 representation-absent 或
   downstream-unabsorbed 中一个解释，而不是只产生新相关指标；
6. 不复用 caption NLL/no-pixel/CKA/CCA/HSIC，不改变 task/prompt/subset，不需要
   layer/rank/pooling/probe/metric sweep；
7. 有尚未查看、方向明确的 readout prediction；若使用既有 LVLM performance 作为
   competing outcome，必须预先固定配对关系；
8. 资源在当前服务器内，且不访问 final confirmation；
9. 若支持，能导出 encoder-side representation repair 与 downstream-side absorption
   intervention 的明确分流原则。

通过只允许登记一个 `NEW` checkpoint-only candidate，并另建 immutable plan；文献
结果本身不得宣布 `PROMISING`。

## 支持标准

必须同时满足：

1. formal readout/identifiability source 门；
2. independent direct VLM/LVLM source 门；
3. unique no-sweep local readout 门；
4. exact local interface/feasibility 门；
5. asymmetric inference boundary 可预先写清；
6. 能区分至少两个 competing explanations 中的一项；
7. 不恢复任何已失败 proxy/instantiation。

满足时结论为 `SELECT_ONE_CANDIDATE`，不是 mechanism 结论。

## 否定标准

任一项成立即拒绝对应 bridge：

1. formal result 只保证任意/无限容量 decoder 的存在，不能固定本地 readout；
2. direct evidence 只来自 classifier/dual encoder，且无 autoregressive-LVLM
   downstream bridge；
3. readout 必须选择 layer、pooling、rank、regularization、probe family 或 metric；
4. positive 与 downstream performance 只是事后相关，无法产生预注册方向；
5. negative probe 没有 completeness/impossibility guarantee 却被用于宣称 signal
   absent；
6. exact encoder/preprocessing/output interface 与本地不匹配；
7. 本地测试必须改变 rotation task/ratio/prompt/subset，或恢复已失败 proxy；
8. readout 不能区分 representation 与 downstream explanations。

若五族都只得到上述证据，记录 `NO_CANDIDATE` /
`BRIDGE_REJECTED`，只否定当前 frozen-feature identifiability bridge；转向
authoritative controlled-coverage literature gate，不制造新 probe。

## 无法判断标准

只限：

- 决定性全文/appendix 无法获得；
- source/version/venue 或 theorem statement 无法核实；
- exact encoder identity/preprocessing/projector-input interface 无法只读确认；
- readout selection/control 细节未公开。

`INCONCLUSIVE` 不自动获得 checkpoint 或训练预算；记录后继续下一 candidate。

## 最小执行

1. 提交本 plan；
2. backend/env preflight 与 existing-source/title dedup；
3. 五族检索，保存全部 raw responses；
4. normalized-title 去重、prior-overlap 与 relevance ranking；
5. 全文/appendix 核查 8–14 篇决定性 primary sources；
6. 写 evidence/applicability matrix；
7. 只读核查唯一 route 的 exact local encoder/interface；
8. 作出 `SELECT_ONE_CANDIDATE` 或 `NO_CANDIDATE`；
9. 同步 canonical state、registries、review/nightly 与 source hashes。

本轮 GPU、checkpoint inference 与训练均为 0。

## 所需资源

- GPU：0；
- CPU/RAM：轻量 API parsing、PDF/HTML extraction 与索引；
- disk：预计 <1 GB；
- final confirmation：不访问；
- checkpoint readout/training：本轮禁止，后续必须另建并提交 immutable plan。
