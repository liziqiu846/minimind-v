# Autonomous Research Idea Registry

本表记录 Research Envelope 内所有 candidate idea。Agent 提出新 idea 前必须先检查
本表，避免用不同名称重新引入已经否定的机制。

Failed ideas must never be deleted.

允许状态：

- `NEW`
- `TESTING`
- `REJECTED`
- `INCONCLUSIVE`
- `PROMISING`
- `CONCLUSION_CANDIDATE`

## Dynamic backlog

| Queue | Candidate | Why now? |
|---|---|---|
| `ACTIVE` | `VISCOND-01` | `XMC-01` 的 13 篇 theorem audit 未找到 autoregressive-risk bridge；视觉条件利用是最直接的生成式 LVLM 特有 competing mechanism |
| `NEXT` | `OBJ-01` | 若冻结视觉条件 test 形成机制证据，可设计最小 objective intervention；否则按失败证据继续搜索新 candidate |
| `BACKLOG` | `COVER-01` | 需要受控数据 mixture 训练；现有同数据模型不能作因果判别 |

| ID | Candidate mechanism | Category | VLM-specific novelty | Literature relation | Why it may explain code/performance decoupling | Falsifiable prediction | Cheapest valid test | Future algorithmic implication | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| XMC-01 | 跨模态共现图/配对语义一致性，以及模型对主要跨模态谱方向的保持 | Data + representation | 图文联合分布和非对称共现图是单模态 LLM 不具有的对象 | Zhang et al. 2023 给出 spectral MMCL→共现矩阵分解→linear-probe bound；DataComp/DFN/BLIP 提供数据算法证据 | 码长不决定配对语义误差、图连接性或模型是否保留对应谱方向；压缩可降低复杂度同时增加表示近似误差 | 在预声明的关系保持/关系破坏图文对上，真实性能较差的同数据模型应有更小的正确配对 margin；若纯数据统计在同数据 P/S 间不变且无模型保持差异，则不能解释 P/S | 先审计现有 artifact 是否支持冻结 checkpoint 的 pair-margin / representation test；不对历史结果试多个 proxy | semantic-pair filtering、coverage-aware sampling、谱/低秩保持正则 | round1：6/9 P/S 实际数据/permutation 相同，3/9 缺 manifest；round2：完整核查 13 篇 primary theory，最强结果分别止于 contrastive linear probe/retrieval、Gaussian dual-encoder conditional 或机制性 UFM，均无唯一 autoregressive LVLM statistic→semantic-risk bridge；禁止 proxy/layer/rank sweep rescue | REJECTED |
| COMP-01 | 跨模态组合绑定相对 bag-of-words / language shortcut | Representation + data | 保持对象/词边际信息但丢失图文关系和顺序，是跨模态组合问题 | Winoground、ARO、SugarCrepe；ARO 提供 composition-aware hard-negative 证据 | 更短/更共享的模型可能维持普通 NLL，却在关系交换、属性绑定和词序反事实上退化 | 同词集合、只改变关系/顺序的预声明反事实对上，较差模型的正确-vs-反事实 margin 应更小 | 冻结 checkpoint 对标准外部双图双描述 panel 做 forced-choice NLL；交叉差分抵消加性文本偏好 | 组合感知 hard negatives、relation-balanced sampling | round1 完整 What’sUp 410 pairs：sign concordance `5/9`、预测方向 CI `1/9`、budget concordance low/current/high=`1/3,3/3,1/3`；95.37%–99.76% pairs 两图偏好同一 caption；触发预注册否定且禁止 rescue | REJECTED |
| VISCOND-01 | 任务相关视觉条件信息的保持与利用，而非语言先验替代 | Representation | 需要区分语义预测风险与图像条件增量，属于生成式 LVLM 特有问题 | Eyes Wide Shut、MMStar、POPE、VCD | 结构压缩可保留语言能力却损伤视觉表示或图像对输出的条件影响，因此码长和真实性能脱钩 | 较差模型在预声明的视觉必要样本上应表现出更小的 correct-image 相对 counterfactual-image 增益，且不能由 language-only baseline 解释 | 冻结模型、固定视觉必要样本与单一预声明操作性代理；不得称互信息或正式视觉风险 | 视觉保持辅助目标、vision-aware sampling、视觉对比解码/正则 | `EMPIRICAL_MECHANISM` + `ALGORITHMIC_EVIDENCE`；无正式生成风险桥 | NEW |
| OBJ-01 | contrastive / generative / next-token 监督对视觉关系学习的不平衡 | Training | 图文对齐、生成和语言建模目标竞争是跨模态训练特有结构 | CoCa、SigLIP、MM1、Prismatic、LLaVA-1.5 | 参数压缩不保证视觉监督足够；next-token loss 可由语言捷径降低而视觉关系未学好 | 固定数据/算力下增加预声明视觉关系辅助目标应改善视觉必要/组合泛化，且不以码长变化解释 | 今晚只能冻结最小训练设计；真正判别需要新训练 | joint contrastive-captioning、visual-dependency weighting、objective-balanced curriculum | `ALGORITHMIC_EVIDENCE`; causal LVLM validation absent | NEW |
| COVER-01 | 图文域与组合覆盖，而非样本量本身 | Data | 联合覆盖对象是“域×视觉概念×文本表达”的跨模态组合 | Kempf et al. 2025、DataComp、MM1 | 短码模型仍可能在未覆盖组合上失败；简单规模/码长无法编码覆盖关系 | 受控增加互补域/组合应改善预声明 OOD 方向，而增加冗余同域数据不应有同等收益 | 今晚只能核查现有数据清单；合法测试需控制数据 mixture 后重训 | coverage-aware sampling、dataset mixture optimization、targeted recaptioning | `EMPIRICAL_MECHANISM`；CLIP→LVLM bridge 未完成 | NEW |
