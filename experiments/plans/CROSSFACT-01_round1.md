# CROSSFACT-01 Round 1 — authoritative crossed-cell gate

**日期**：2026-08-07

**阶段**：阶段三

**类型**：COVER-01 failure-driven primary-source literature / official-schema /
local-lineage gate；不训练、不运行 checkpoint、不访问 final confirmation

**不可变性**：本文件提交后不修改科学问题、crossed-cell 接受门、source-factor
orthogonality、held-out prediction 门或判定标准；修订必须创建新 round。

## 科学问题

`COVER-01` 已证明，LAION/VFLAN、broad domain 和 task-category labels 即使具有
authoritative provenance，也同时编码 acquisition、visual content、task、caption
style、quality、difficulty、output schema 与 target choice，不能构成本地唯一
single-factor coverage intervention。Local IDs 的缺失也不是决定性障碍：保存的
169 个 official ALLaVA caption rows 全部能通过 exact assistant text 回到 local
rows。

本轮只研究一个更窄、直接针对该混杂的问题：

> 是否存在由数据发布者在 outcome 前定义、可版本化重建的 crossed multimodal
> schema，使同一 image/acquisition unit 系统地对应多个 text/task factor values，
> 从而唯一冻结 baseline cells、complementary crossed cells、matched redundancy
> cells 与一个 ordinary held-out crossed cell，并在 generative VLM 上形成
> 单因素、方向明确且本地可行的组合覆盖 prediction？

本轮只裁决 bridge 是否存在，不运行 checkpoint 或训练。若 bridge 成立，只登记一个
新 mechanism-intervention training candidate，并另建 immutable plan。

## 与 COVER-01 的非重复边界

本轮不是把 `COVER-01` 换名重试：

- 不从 LAION/VFLAN、dataset name、broad task categories 或 domain pairs 中挑选
  mixture；
- 不搜索 mixture weight、source ratio、target benchmark 或最优 task subset；
- 不用 pretrained embedding、LLM judge、gradient influence、perplexity、
  representation cluster 或人工浏览定义 factor；
- 不把“同一 image 有 caption 和 instruction”自动视为 factorial design；必须证明
  factor values、cell membership、answer schema、difficulty 与 duplicate identity
  可前瞻固定；
- 不复用 `COMP-01` caption-NLL binding proxy、`VISCOND-01` no-pixel proxy、
  `LITMAP-05` selectable probe 或已失败的 rotation instantiation；
- 不补 `VISSUP-01` roots，不运行 `PROJALLOC-01` roots `43202/43203`。

本轮唯一新增科学内容是：

\[
\text{same authoritative acquisition/image unit}
\times
\text{publisher-defined text/task factor}
\rightarrow
\text{held-out multimodal crossed-cell risk}.
\]

如果 audited schema 仍只是不同 dataset/task/source 的拼接，必须判为当前 bridge
失败，不能退回 broad coverage。

## 可证伪假设

假设 H：如果 source-defined crossed-cell coverage 是当前可被本项目裁决的
VLM-specific data mechanism，则 primary literature、official dataset schema 与
local feasibility 之间应存在至少一条完整证据链，同时满足：

1. 一个 stable acquisition/image unit 由发布者提供 immutable ID、asset hash 或可
   重建 group key；
2. 至少两个 text/task factors 及其 values 由数据发布者在本项目 outcome 前定义，
   不是本项目聚类或事后命名；
3. factor values 在足够多相同 acquisition/image units 上系统 crossing，而不是偶然
   overlap 或不同 dataset 的 sparse union；
4. selected cells 使用共同的 generative answer interface；若 output format 是一个
   factor，必须在 factorial schema 中正交 crossing，不能与唯一 complementary
   condition 共线；
5. baseline、complementary 与 redundancy conditions 可使用 exact group/example
   IDs，在总 image groups、examples、有效 tokens/steps、prompt/answer schema、
   label distribution、quality 与 difficulty 上匹配；
6. 一个 source-defined held-out crossed cell 及方向能在任何新 checkpoint outcome
   查看前唯一冻结；
7. direct autoregressive VLM/LVLM primary evidence 已显示 crossed-cell exposure
   在 matched control 下影响 unseen-cell risk，或 formal compositional result 的
   assumptions 可重新证明并落到当前 generative risk；
8. 当前服务器能合法取得或重建所需 cells，且不访问 final confirmation。

若 same-image annotations 只是不同 task/source/output 的非正交拼接、factor 或 target
仍需人工挑选、或 held-out cell 只能看结果后决定，则 H 在本轮严格门下不成立。

## 可证伪预测

若 H 成立，全文与 schema audit 结束前应能唯一写出一个尚未执行的 local paired
training specification：

- fixed dataset name、revision/license 与 acquisition/image group-key algorithm；
- fixed factor names、values、cell IDs 与 cell-support counts；
- fixed baseline cells 与 exact baseline examples；
- two equal-size additions：
  - **complementary**：来自 baseline 未覆盖、但由 schema 预先定义的 crossed cells；
  - **redundancy**：来自 baseline 已覆盖 cells 的额外 independent image groups；
- 两条件总 image groups、examples、effective tokens、steps、prompt/answer schema、
  label distribution、trainable coordinates 与 scorer 相同；
- fixed ordinary held-out cell，且它不是 train factor 的 duplicate/derivative；
- directional prediction：complementary condition 在该 held-out cell 的
  image-group generative performance 优于 redundancy control，同时不降低预声明
  matched seen-cell control；
- primary outcome 与 support/rejection thresholds 能在查看新 model outcome 前唯一
  写定。

若不能唯一写出上述 specification，结果必须为 `NO_CANDIDATE`；不得运行多个
factorizations、held-out cells、task subsets 或 metrics 后选择最漂亮者。

## VLM 特有性与理论边界

有效对象必须包含一个真正的跨模态 interaction：

\[
I \times T \rightarrow Y,
\]

其中 \(I\) 是 authoritative visual/acquisition factor，\(T\) 是 authoritative
text/task/query factor，held-out object 是未见 \(I\times T\) cell 的 generative
risk，而非单独 image-domain 或 text-template risk。

以下不构成 candidate：

- 只增加 task 数、dataset 数、image 数或 captions 数；
- 相同 images 上由不同 LLM prompts 事后生成多个 task labels；
- image-only class×domain CLIP classification，没有 generative risk bridge；
- 同图多个 QA，但 question type、answer type、difficulty 与 target selection 未
  source-defined 或未正交；
- train/eval task names 相同但 images/acquisition 不共享 group identity；
- 只报告 benchmark average，没有 predeclared held-out cell；
- matrix completion、meta-learning 或 domain-generalization theorem 只在 fixed
  feature/classifier/squared-loss setting 成立，未重证到 autoregressive LVLM；
- 为了得到 signal 搜索 cell、prompt、output normalization、metric 或 model。

同一 image 上 caption/instruction/VQA overlap 只提供 schema inventory；只有完整
crossing、正交 controls 与 direct/formal bridge 同时成立才有因果含义。

## Authoritative crossed-schema 接受门

一个 source schema 只有全部满足时才可进入 exact-design gate：

1. **Publisher-defined factors**：factor name/value 与 semantics 由官方 paper/card/
   annotation protocol 定义；
2. **Versioned**：有 revision、DOI、release、repository commit 或可校验 manifest；
3. **Stable visual unit**：image/acquisition/scenario ID 可跨 factor values 稳定连接，
   不是 URL basename 或模糊 perceptual match；
4. **Example lineage**：每个 selected example 可映射 visual unit、factor tuple、
   prompt/query、answer、split 与 derivative/duplicate group；
5. **Systematic crossing**：不是少量 accidental overlap；所需 train/held-out cells
   有足够 independent visual groups；
6. **Stable semantics**：storage shard、missingness、annotator ID 或 generation
   timestamp 不能充当 scientific factor；
7. **Output control**：answer/prompt format 固定，或作为独立 crossed factor 被正交
   控制；
8. **Difficulty/quality control**：不能把 complementary cell 与唯一更难/更高质量/
   不同 generator 的 examples 共线；
9. **Access/license**：本地可取得或由公开 source 合法重建，所有上游许可边界可记录；
10. **No leakage**：不与 final confirmation 交叉，不用 target outcomes 选择 cells。

任一项失败，该 source 只能记为 schema inventory，不能授权训练。

## Exact crossed-cell contrast 接受门

最多保留一个 contrast，且必须同时满足：

1. exact baseline/complementary/redundancy/held-out factor tuples；
2. exact source IDs 与 independent visual group IDs；
3. train conditions 总 visual groups、examples、tokens、steps、prompt/answer schema、
   label distribution 与 trainable coordinates 匹配；
4. complementary 与 redundancy 唯一差异是新增 cells 是否扩展预声明 factor
   crossing；
5. held-out cell 与 direction 在 checkpoint scoring 前冻结；
6. seen-cell control 与 held-out-cell primary outcome 一起预声明，以区分总体
   regularization/quality effect；
7. source quality、difficulty、generator、resolution、annotation density、
   duplicate/derivative relation 均匹配或由官方 factorial design 正交；
8. 训练能区分“crossed-cell coverage”与“更多同-cell examples”至少两个解释；
9. 第一轮严格 2 conditions × 1 paired seed pilot；positive 后配置完全不变补至
   total 3 seeds，最多 6 trainings；
10. 当前服务器资源内、不访问 final confirmation、不改变统计关系。

只要需要搜索 factorization、cell pair、target cell、sample ratio、prompt
normalization 或 metric，unique contrast 门即失败。

## 检索与 schema 审计协议

### Backend 顺序

1. 先检查已保存 `sources/`、`COVER-01` evidence matrix、official ALLaVA/Vision-Flan
   cards、local manifests 与 title/version duplicates；
2. 检查 `parallel-cli`、`PARALLEL_API_KEY` 与 `OPENROUTER_API_KEY`；
3. backend 可用时，每个 scientific query 做 academic-domain 与 general 两次
   `parallel-cli search`，全部用 `-o` 保存到 `sources/`；
4. backend 不可用时使用 arXiv、OpenAlex、Crossref、OpenReview/conference
   proceedings、official dataset repositories/cards 与 project pages；
5. raw responses、decisive full text/appendix、official schema/license/version、
   access receipts 与 source hashes全部保存。

不得安装或认证未授权付费 backend；不得只凭搜索摘要、标题、benchmark leaderboard
或 dataset marketing language 作 bridge 决定。

### Targeted query families

只覆盖以下五族；exact-title/version/card verification 不计新 family：

1. generative VLM/LVLM + held-out image×task/query combinations + matched training
   exposure；
2. same-image multi-task / multi-question multimodal datasets + authoritative factor
   schema + group IDs；
3. factorial multimodal dataset design + compositional/crossed-cell generalization；
4. visual instruction tuning + systematic task crossing + unseen task-combination
   prediction；
5. current ALLaVA/Vision-Flan/COCO-derived lineage + same-asset caption/instruction/QA
   linkage + local reconstructability。

不扩展为 broad compositional generalization survey，不搜索最佳 dataset mixture，不
把 synthetic task generation 本身当作 source-defined factor。

### 时间与质量范围

- direct generative VLM/LVLM evidence 优先 2023–2026；formal factorial /
  compositional foundations 不限年份；
- 首选 NeurIPS、ICML、ICLR、CVPR、ACL、EMNLP、ECCV 与正式 journal；schema 以
  official paper/card/repository 为准；
- 目标不超过约 500 raw literature records；
- 全文/appendix 核查 8–12 篇决定性 primary papers；
- 只核查 2–4 套进入 exact-schema shortlist 的 official datasets；
- `NEXT<2`，因此本轮是失败证据驱动的 targeted search，不做全领域 broad scan。

## Evidence / applicability matrix

每篇决定性 paper 至少记录：

- title、authors、year、venue/status、DOI/arXiv/version；
- model family、scale、loss 与 generative/contrastive risk object；
- visual acquisition unit、text/task factors、factor semantics 与 publisher origin；
- crossing 是否 systematic，还是 sparse overlap/post-hoc union；
- exact baseline/complementary/redundancy/held-out cells；
- examples/image groups/tokens/steps、prompt/answer schema 与 label distributions；
- quality/difficulty/generator/resolution/duplicate controls；
- target selection、seeds、uncertainty 与 unseen-cell prediction；
- theorem assumptions、proof object、certified risk 与 autoregressive applicability；
- valid inference、invalid inference、algorithmic implication 与 limitation；
- local access/license/lineage/resource feasibility；
- gate：`DIRECT_CROSSED_GENERATIVE`、`FORMAL_ADJACENT`、`SCHEMA_ONLY`、
  `HEURISTIC_ONLY` 或 `REJECT_FOR_BRIDGE`。

每套 authoritative schema 至少记录：

- name/version/revision/DOI/card/repository/license；
- official factor fields 与 stable acquisition/image group key；
- example ID、prompt/query、answer、split、duplicate/derivative lineage；
- crossing support table，只统计 schema，不查看新 checkpoint outcome；
- output/difficulty/quality/generator controls；
- exact local path 或 reproducible acquisition route；
- 能否唯一形成 four-way cell specification；
- missingness、duplicate IDs、ambiguous semantics、access/licensing risks。

## 可能混杂

- 同一 image 的多个 annotations 来自不同 generators/annotators 或不同 quality gates；
- factor value 与 answer type、length、vocabulary、prompt template 或 label leakage
  共线；
- task difficulty 与 held-out cell 唯一绑定；
- repeated annotations 不是 independent visual groups；
- source ID 复用或 duplicate/derived image 造成 train–held-out leakage；
- crossing 只发生在少数易样本，missingness 非随机；
- visual unit 由 URL/filename 猜测而非 authoritative group key；
- same-image caption/instruction pair 共享 target answer，造成直接 leakage；
- CLIP/classification factor result 被无证明外推到 autoregressive generation；
- target cell、metric 或 output normalization 在多个结果中事后选择。

不能由 official factorial schema 或 exact matching 排除的主要混杂，都阻止 candidate
升格；不得用 sweep 补救。

## Candidate 接受门

最多登记一个新 candidate，且必须全部满足：

1. ≥1 个 independent direct autoregressive/generative VLM/LVLM primary source
   提供 matched crossed-cell evidence，或 formal result assumptions 可明确重证到
   current generative risk；
2. ≥1 套 authoritative source-defined crossed schema 通过全部 ten-field gate；
3. stable visual group × factor tuple 的 exact example lineage 可本地重建；
4. unique baseline/complementary/redundancy/held-out specification 通过全部
   single-factor gates；
5. unique ordinary held-out cell、direction、primary outcome 与 seen-cell control
   在新 outcome 查看前冻结；
6. existing checkpoint/artifact 不能回答，而新训练能区分至少两个 explanations；
7. 训练符合 2 conditions × paired-seed pilot、positive 后 total 3 seeds、最多
   6 trainings；
8. 不复用失败 proxy/instantiation，不需要 factor/cell/target/metric sweep，不访问
   final confirmation；
9. 支持时能导出 crossed-cell sampling、factor-balanced curriculum 或 targeted
   task generation principle。

通过只允许登记一个 `NEW` training candidate，并另建 immutable plan。本轮 schema
gate 不能直接标记 `PROMISING`。

## 支持标准

必须同时满足：

1. authoritative crossed-schema 门；
2. stable visual group 与 exact example lineage 门；
3. independent direct/formal generative evidence 门；
4. output/difficulty/quality/source-factor orthogonality 门；
5. unique four-way cell contrast 门；
6. frozen held-out direction、primary outcome 与 seen-cell control 门；
7. local access/license/resource/no-leakage 门；
8. competing-explanation 与 algorithmic-exit 门。

满足时结论为 `SELECT_ONE_CANDIDATE`，不是 crossed-cell mechanism 结论。

## 否定标准

任一项成立即拒绝当前 bridge：

1. factor/cell 只能由 embedding、LLM、gradient、outcome 或人工事后 grouping 产生；
2. visual unit、factor semantics、version、example lineage 或 license 不稳定；
3. crossing 是 sparse overlap/non-random missingness，无法构造支持充分的 exact
   cells；
4. complementary 与 redundancy 同时改变 task/output format、difficulty、quality、
   generator、resolution、labels、tokens/steps 或 duplicate structure；
5. 必须搜索 factorization、cell pair、target cell、sample ratio、prompt normalization
   或 metric；
6. direct evidence 只有 CLIP/dual encoder 且无 generative risk bridge；
7. 无法在 outcome 前固定 held-out cell、direction、primary outcome 与 seen-cell
   control；
8. local exact lineage 不可恢复，或数据无法在当前服务器合法取得；
9. 需要 final confirmation 或明显超出服务器资源。

若五族与 2–4 套 official schemas 均只得到上述证据，记录 `NO_CANDIDATE` /
`BRIDGE_REJECTED`。只否定当前 authoritative-crossed-schema-to-local-generative-
single-factor bridge；不否定跨模态组合覆盖、task diversity 或 compositional
generalization mechanism。

## 无法判断标准

只限：

- 决定性 full text/appendix、official schema/license/version 无法取得；
- stable visual group key、factor semantics 或 example-level lineage 暂时无法核实；
- source access 短期异常，无法区分 permanent absence 与 transient failure；
- exact local artifact 因缺失 manifest 无法只读恢复。

`INCONCLUSIVE` 不自动获得训练或更多资源；记录后继续下一 candidate。

## 最小执行

1. 提交本 plan；
2. backend/env preflight 与 existing source/title/version dedup；
3. 五族 targeted discovery，保存 raw responses；
4. deterministic title normalization 与 relevance index；
5. 全文/appendix 核查 8–12 篇决定性 primary sources；
6. 核查 2–4 套进入 shortlist 的 official schemas；
7. 只读核查 local same-asset lineage 与 exact-cell support；
8. 写 paper/schema applicability matrix 与 source hashes；
9. 最多写出一个 four-way exact cell specification；
10. 作出 `SELECT_ONE_CANDIDATE`、`NO_CANDIDATE` 或 `INCONCLUSIVE`；
11. 同步 canonical state、registries 与 review queue。

本轮 GPU、checkpoint inference 与训练均为 0。任何训练必须等待新的 immutable
training plan 提交。

## 所需资源

- GPU：0；
- CPU/RAM：轻量 API parsing、schema/manifest audit、full-text extraction 与索引；
- disk：预计 <1 GB；
- 网络：official paper/dataset repositories 与公开 search APIs；
- final confirmation：不访问；
- checkpoint inference/training：本轮禁止；
- 后续训练：仅在通过全部门并另建 plan 后，第一轮最多
  `2 conditions × 1 paired seed`。
