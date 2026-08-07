# COVER-01 Round 1 — authoritative controlled-coverage gate

**日期**：2026-08-07
**阶段**：阶段三
**类型**：LITMAP-05 failure-driven primary-source literature / data-lineage /
local-interface gate；不训练、不运行 checkpoint、不访问 final confirmation
**不可变性**：本文件提交后不修改科学问题、source/data 接受门、single-factor
contrast、prediction 门或判定标准；修订必须创建新 round。

## 科学问题

`VISSUP-01` 与 `PROJALLOC-01` 两个 training instantiation 均未学会稳定的 held-out
rotation，`LITMAP-04` 与 `LITMAP-05` 又分别缺少唯一 objective intervention bridge
与 frozen-feature identifiability bridge。继续制造 checkpoint proxy 不能区分这些
competing explanations。当前转向一个不依赖 checkpoint readout 的数据侧问题：

> MiniMind-V 当前训练数据及本服务器可取得的 authoritative source data 中，是否
> 存在由来源定义且可复现的 domain / mixture / multimodal-combination strata，使
> “固定总训练预算时增加互补覆盖”相对“增加同域冗余”能够形成唯一
> single-factor contrast、方向明确的 held-out VLM 泛化 prediction，并在当前资源内
> 合法验证？

本轮只裁决是否存在可执行 bridge，不运行本地训练。若 bridge 成立，只登记一个
mechanism-intervention training candidate，并另建 immutable experiment plan。

## 既有失败证据与约束

本轮必须同时尊重：

- `XMC-01=BRIDGE_REJECTED`：不得用 embedding graph、CKA/CCA/HSIC、layer/rank
  sweep 重新定义 coverage；
- `COMP-01=PROXY_REJECTED`：不得复用 caption-NLL binding margin；
- `VISCOND-01=PROXY_REJECTED`：不得复用 correct-image vs no-pixel margin，也
  不能以其 positive gate 启动训练；
- `VISSUP-01=INSTANTIATION_REJECTED`：不换 rotation ratio/task/prompt/metric，
  不补 roots；
- `PROJALLOC-01=INSTANTIATION_REJECTED`：不运行 `43202/43203`，不搜索
  allocation；
- `LITMAP-04=BRIDGE_REJECTED`：不得从已核查 objective methods 中任挑 component
  或 ratio；
- `LITMAP-05=BRIDGE_REJECTED`：不得搜索 layer、token、pooling、classifier、
  regularization、rank 或 metric 来制造新的 frozen-feature proxy。

不得把 raw sample count、随机 cluster、embedding neighborhood、事后 benchmark
category、人工浏览后定义的语义桶或任意 metadata field 直接称为 controlled
coverage。

## 可证伪假设

假设 H：如果 authoritative controlled coverage 是当前可被本项目裁决的
VLM-specific data mechanism，则 primary literature、source dataset documentation 与
本地 data lineage 之间应存在至少一条证据链，同时满足：

1. strata 由数据产生者的 task/domain/acquisition/generator/mixture schema 在查看本地
   outcome 前定义，并有稳定版本、许可证与可重建标识；
2. 每个 example 的 image、text 与 pairing lineage 可追溯到该 stratum，而不是只给
   aggregate dataset name；
3. 可构造相同总 image-text pairs、tokens/steps、label/prompt schema 与训练配置的
   paired contrast，唯一主要差异是新增 examples 来自 source-defined complementary
   stratum 还是已覆盖 stratum 的 redundancy；
4. 至少一个 source-defined target stratum 在训练构造前冻结，提供尚未查看、方向
   明确的 ordinary held-out / development prediction；不使用 final confirmation；
5. 至少一个 direct generative VLM/LVLM primary source 提供 matched mixture /
   coverage control，或 formal data-mixture result 的 assumptions 可重新证明并落到
   当前 autoregressive LVLM 风险对象；
6. 数据可在本服务器获得或由公开、版本化 source 在当前资源内重建，且合法许可允许
   所需研究使用；
7. 若结果成立，能自然导出 coverage-aware sampling、mixture optimization 或
   targeted recaptioning，而不是只产生描述性 dataset statistic。

若 strata 只能由本地 embedding/LLM/人工事后聚类产生，lineage 只到 dataset
aggregate，coverage 与 quality/difficulty/caption length/source license 同时改变，
或 held-out target 只能在看结果后选择，则 H 在本轮严格门下不成立。

## 可证伪预测

若 H 成立，全文与 data-lineage 核查结束前应能唯一写出一个本地 paired training
specification：

- 固定 source dataset version 与 stratum identifiers；
- 固定 baseline examples 和两组等量新增 examples；
- complementary condition 的新增 examples 来自与 frozen held-out target 有
  source-defined关系、但 baseline 未覆盖的 stratum；
- redundancy control 的新增 examples 来自 baseline 已覆盖的 stratum；
- 两条件的总 images/pairs、有效 tokens、steps、prompt/answer schema、optimizer、
  trainable coordinates 与 scorer 完全一致；
- 在查看新模型结果前冻结唯一 ordinary held-out target 与方向：
  complementary condition 在该 target 的 image-group performance 应优于
  redundancy control，同时不得由 source quality、caption leakage 或 label
  distribution 差异解释。

若无法在查看 outcome 前唯一指定 exact examples/strata/held-out target 与 matched
contrast，则本轮 prediction 失败，必须 `NO_CANDIDATE`；不得通过运行多个 mixture、
target 或 coverage definition 后选择最漂亮者。

## VLM 特有性与理论边界

有效对象必须是联合多模态覆盖：

\[
\text{source-defined visual/domain factor}
\times
\text{text/task/prompt factor}
\times
\text{image--text pairing or combination}
\rightarrow
\text{unseen multimodal risk}.
\]

以下内容不能单独成为 candidate：

- 单纯增加 image 数、text token 数或 dataset 数；
- 只在 CLIP retrieval 上验证、没有 generative LVLM risk bridge 的 scaling law；
- image-only class balance 或 text-only lexical diversity；
- 由 pretrained embedding、LLM annotation 或人工事后浏览形成的 cluster；
- 同时改变数据质量过滤、caption model、分辨率、task template 与 mixture；
- 只报告总体 benchmark average、没有预声明 source-defined target stratum；
- 需要重新定义 train / selection / confirmation 关系的构造。

CLIP/dual-encoder 文献只能作为启发或 source schema 证据；若用于因果方向，必须明确
核查其 loss、model family、mixture intervention、held-out risk 与
autoregressive-LVLM bridge。名称中的 diversity、coverage、mixture 或 domain 不
自动构成适用定理。

## Authoritative stratum 接受门

一个 stratum 只有全部满足时才可用于 candidate：

1. **Source-defined**：由数据发布者的固定 schema/metadata 定义，不由本项目 outcome
   或 representation 产生；
2. **Versioned**：有版本、revision、URL/DOI/repository commit 或可校验 manifest；
3. **Example-level lineage**：每个选中 example 可映射到 source ID、image asset、
   text/prompt 与 stratum；
4. **Stable semantics**：字段语义由官方文档或生成协议说明，不把 storage shard、
   URL host、文件名或缺失值当科学域；
5. **Access/licensing**：本服务器当前可访问或可公开重建，许可与研究使用边界可
   记录；
6. **No leakage**：不与 final confirmation 交叉，不通过 target labels 反向选择
   train examples；
7. **Sufficient support**：baseline、complementary、redundancy 与 held-out target
   均有足够独立 image groups，且近重复与同源派生关系可审计。

未通过的 metadata 只能记为 inventory，不能用来启动训练。

## Single-factor contrast 接受门

最多保留一个 contrast，且必须同时固定：

1. baseline、complementary、redundancy 三组 exact source IDs；
2. 两个训练条件的总 image groups、examples、有效 tokens、steps、label/prompt
   schema 与 trainable coordinates；
3. 唯一变化是新增样本来自未覆盖 complementary stratum 或已覆盖 redundancy
   stratum；
4. source quality、caption generator/human source、resolution、task type、answer
   leakage、label distribution 与 acquisition difficulty 要么匹配，要么由 source
   factorial design 正交控制；
5. held-out target 与 direction 在任何新 checkpoint scoring 前冻结；
6. contrast 能区分“互补 coverage”与“更多同域数据”至少两个解释；
7. 第一轮训练严格采用 2 conditions × 1 paired seed pilot；positive 后才在配置
   完全不变时补到 total 3 seeds，最多 6 trainings；
8. 不访问 final confirmation，不改变既有统计关系，不需要超出当前服务器资源。

若需要搜索 mixture weights、domain pairs、target strata、caption method、sample
ratio 或 metric，则 unique contrast 门失败。

## 检索与数据审计协议

### Backend 顺序

遵守 `research-lookup`：

1. 先检查 `sources/`、既有 literature maps、results 与本地 dataset/config
   inventories，按 title/source/version 去重；
2. 检查 `parallel-cli`、`PARALLEL_API_KEY` 与 `OPENROUTER_API_KEY`；
3. backend 可用时，每个科学 query 做 academic-domain 与 general 两次
   `parallel-cli search`，全部用 `-o` 保存到 `sources/`；
4. backend 不可用时保存失败原因，使用 arXiv、OpenAlex、Crossref、OpenReview /
   conference proceedings、official dataset/model repositories 与 project pages；
5. 所有 raw responses、official docs、paper正文/appendix、dataset cards、license、
   version/commit/URL、download/access receipt 与 SHA-256 都保存在仓库。

不得安装或认证未授权付费 backend；不得只凭标题、摘要、搜索 synthesis、leaderboard
或引用量作 bridge 决定。

### Targeted query families

首轮严格覆盖以下五族；exact-title、dataset-card 与 license verification 不计为新
family：

1. generative VLM/LVLM + controlled data mixture / domain composition +
   held-out transfer/generalization；
2. multimodal data diversity / coverage / concept combination + fixed-scale matched
   control；
3. dataset mixture optimization / data selection + autoregressive multimodal model +
   target-domain prediction；
4. source-defined multimodal domains/combinations + example-level metadata /
   provenance / licensing；
5. MiniMind-V 当前训练 source dataset + exact version/schema/manifest +
   local reproducible subset construction。

不得扩展为 broad data-centric AI survey，也不得因某数据方便而切换到新的
post-hoc strata。

### 时间与质量范围

- direct generative VLM/LVLM evidence 优先 2023–2026；formal data-mixture /
  domain-generalization foundations 不限年份；
- 首选 NeurIPS、ICML、ICLR、CVPR、ACL、EMNLP、ECCV 与正式 journal；dataset
  schema 以 official repository/card/paper 为准；
- 目标不超过约 650 raw literature records；
- 全文/appendix 核查 8–14 篇决定性 primary papers，并核查所有进入 local gate 的
  official dataset sources；
- 只在 `NEXT<2` 的 targeted-search需求内执行，不做全领域 broad scan。

## Evidence / applicability matrix

每篇决定性 paper 至少记录：

- title、authors、year、venue/status、DOI/arXiv/version；
- model family、scale、contrastive/generative/autoregressive 类型；
- exact source datasets、versions、mixture units 与 example sampling；
- coverage/diversity/domain 的正式定义，是否 source-defined；
- baseline/complementary/redundancy conditions 的 total examples/tokens/steps；
- 是否只改变 coverage，或同时改变 quality、difficulty、caption、resolution；
- held-out target、selection protocol、seeds 与 uncertainty；
- theorem/proposition assumptions、proof idea、certified object 与 LVLM applicability；
- algorithmic implication、limitations 与不能推出的内容；
- local exact-lineage、access/license、resource feasibility；
- gate：`DIRECT_CONTROLLED_COVERAGE`、`FORMAL_ADJACENT`、
  `SCHEMA_ONLY`、`HEURISTIC_ONLY` 或 `REJECT_FOR_BRIDGE`。

每个 authoritative dataset/source 至少记录：

- official name/version/revision、paper/card/repository URL、license；
- local path 或 reproducible acquisition route；
- example ID、image/text/pair lineage 与 source-defined strata fields；
- duplicate/group identity、split semantics 与 possible confirmation overlap；
- counts only for feasibility，不查看新 checkpoint outcome；
- 能否形成 exact complementary/redundancy/held-out mapping；
- 缺失、歧义、访问阻断与不可恢复风险。

## 可能混杂

- domain/stratum 与数据质量、caption style、annotator/generator、resolution、
  task difficulty 或 label distribution 共线；
- complementary condition 含有 held-out answer、template 或 near-duplicate image；
- redundancy control 的有效 token 数、unique image 数或 update frequency 不匹配；
- dataset source 名被误当语义域，但内部本身是混合分布；
- official metadata 是 acquisition/storage 字段，不是稳定科学因素；
- train 与 held-out 共享 derived image、caption family、generator seed 或 scene
  template；
- CLIP/dual-encoder result 被无证明外推到 autoregressive generation；
- mixture improvement 来自质量过滤或 caption 重写，而非 coverage；
- target 或 metric 在多组结果中事后选择；
- 本地 current training manifest 缺失，无法重建 exact baseline lineage。

任何不能由 source factorial schema 或 exact matching 控制的主要混杂，都阻止
candidate 升格；不能通过 mixture/target sweep 补救。

## Candidate 接受门

最多登记一个新 candidate，且必须全部满足：

1. ≥1 个 independent direct generative VLM/LVLM primary source 提供 matched
   mixture/coverage evidence，或 formal result 的 assumptions 可明确重证到当前
   generative risk；
2. ≥1 套 authoritative source-defined strata 通过 version、example-lineage、
   semantics、access/license 与 leakage 门；
3. 当前 MiniMind-V baseline data 的 exact source/example lineage 可重建；
4. 唯一 complementary-vs-redundancy contrast 通过全部 single-factor 门；
5. 唯一 ordinary held-out target 与 directional prediction 在新 outcome 查看前
   可冻结；
6. existing checkpoint/artifact 不能回答，而新训练能直接区分至少两个 competing
   explanations；
7. 训练处于阶段三 2 conditions × paired-seed pilot 与当前资源范围；
8. 不复用失败 proxy/instantiation，不需要 domain/mixture/metric sweep，不访问
   final confirmation；
9. 支持时能导出明确的 coverage-aware sampling / mixture optimization /
   recaptioning principle。

通过只允许登记一个 `NEW` mechanism-intervention candidate，并另建 immutable
training plan；本轮 gate 结果本身不得宣布 `PROMISING`。

## 支持标准

必须同时满足：

1. authoritative source-defined stratum 门；
2. exact baseline/example-level lineage 门；
3. independent direct/formal evidence 门；
4. unique single-factor contrast 门；
5. frozen held-out directional prediction 门；
6. local access/license/resource 与无泄漏门；
7. competing-explanation 与算法出口门。

满足时结论为 `SELECT_ONE_CANDIDATE`，不是 coverage mechanism 结论。

## 否定标准

任一项成立即拒绝当前 bridge：

1. strata 只能由 random/embedding/LLM/manual post-hoc grouping 产生；
2. official metadata 无稳定语义、版本、example-level lineage 或许可证；
3. 当前 baseline 只能识别 aggregate dataset name，无法重建 exact source examples；
4. complementary 与 redundancy 同时改变 quality、difficulty、caption、task、
   resolution、label leakage、tokens/steps 或其他主要因素；
5. 必须搜索 domain pair、mixture weight、target stratum、sample ratio 或 metric；
6. direct evidence 只来自 CLIP/dual encoder，且无 generative LVLM risk bridge；
7. 无法在 outcome 前固定 ordinary held-out target 与方向；
8. 数据不可在当前服务器合法取得/重建，或需要 final confirmation；
9. 训练明显超出当前服务器资源。

若五族与本地 data-lineage 都只得到上述证据，记录 `NO_CANDIDATE` /
`BRIDGE_REJECTED`。只否定当前 authoritative-data-to-local-single-factor-coverage
bridge；不否定数据覆盖、多样性、mixture 或跨模态组合结构会影响泛化的上位机制。

## 无法判断标准

只限：

- 决定性正文/appendix、dataset card、license 或 version manifest 无法取得；
- official field semantics、example IDs 或 source lineage 无法核实；
- 当前 baseline 的 exact data manifest 因缺失 artifact 而无法只读恢复；
- 数据访问状态暂时异常，无法区分永久不可用与短期系统故障。

`INCONCLUSIVE` 不自动获得训练或更多数据预算；记录后继续下一 candidate。

## 最小执行

1. 提交本 plan；
2. backend/env preflight、existing-source/title/version dedup；
3. 只读核查当前 MiniMind-V training config、manifests 与 local datasets；
4. 五族 targeted literature search，保存全部 raw responses；
5. normalized-title 去重与 relevance ranking；
6. 全文/appendix 核查 8–14 篇决定性 primary papers；
7. 核查进入 local gate 的 official dataset cards、licenses、versions 与
   example-level lineage；
8. 写 literature/data applicability matrix 与 exact local feasibility receipt；
9. 最多写出一个完整 complementary/redundancy/held-out specification；
10. 作出 `SELECT_ONE_CANDIDATE`、`NO_CANDIDATE` 或 `INCONCLUSIVE`；
11. 同步 canonical state、registries、review/nightly 与 source hashes。

本轮 GPU、checkpoint inference 与训练均为 0。任何训练必须等待新的 immutable
plan 提交。

## 所需资源

- GPU：0；
- CPU/RAM：轻量 API parsing、metadata/manifest audit、PDF/HTML extraction 与索引；
- disk：预计 <1 GB；
- 网络：official paper/dataset repositories 与公开 search APIs；
- final confirmation：不访问；
- checkpoint inference/training：本轮禁止；
- 后续训练预算：仅在通过全部门并另建 plan 后，第一轮最多
  `2 conditions × 1 paired seed`。
