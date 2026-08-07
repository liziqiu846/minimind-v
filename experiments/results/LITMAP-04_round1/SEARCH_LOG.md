# LITMAP-04 Search Log

## 检索边界

- 检索日：2026-08-07（Asia/Shanghai）。
- 冻结问题：objective competition / gradient routing、task-specific absorption 与
  frozen-feature–autoregressive-objective mismatch。
- 失败约束：不换 VISSUP task/ratio/prompt，不搜索 PROJALLOC allocation，不补
  seed，不复用 caption-NLL/no-pixel 或 layer/kernel/rank proxy。
- 本轮只做文献/theory gate；GPU、checkpoint inference、training 均为 0。

## Backend preflight

按 `research-lookup` 先检查本地 sources 与 title index，再检查 specialized backend：

- `parallel-cli`：不可用；
- `PARALLEL_API_KEY`：不存在；
- `OPENROUTER_API_KEY`：不存在。

因此使用并保存以下 fallback：

1. arXiv Atom API；
2. OpenAlex REST API；
3. ar5iv HTML；
4. arXiv source archive；
5. 已归档的 LITMAP-02/03 primary full text。

没有安装或认证新的付费 backend。所有路线决定均基于正文/appendix，不基于搜索摘要。

## 冻结 query families 与保存响应

五族 frozen queries 及为召回率添加的同义扩展保存在：

| Query family | arXiv | OpenAlex |
|---|---|---|
| objective competition / modality imbalance | `sources/research_litmap04_objective_competition_arxiv.xml` | `sources/research_litmap04_objective_competition_openalex.json` |
| objective competition / gradient expansion | `sources/research_litmap04_objective_competition_gradient_expansion_arxiv.xml` | — |
| visual token credit / language dominance | `sources/research_litmap04_visual_credit_arxiv.xml` | `sources/research_litmap04_visual_credit_openalex.json` |
| visual credit / supervision expansion | `sources/research_litmap04_visual_credit_supervision_expansion_arxiv.xml` | — |
| task-specific transfer / overfitting | `sources/research_litmap04_task_transfer_arxiv.xml` | `sources/research_litmap04_task_transfer_openalex.json` |
| frozen feature / objective match | `sources/research_litmap04_frozen_objective_match_arxiv.xml` | `sources/research_litmap04_frozen_objective_match_openalex.json` |
| auxiliary visual objective / routing | `sources/research_litmap04_auxiliary_objective_arxiv.xml` | `sources/research_litmap04_auxiliary_objective_openalex.json` |

决定性 exact-ID metadata 另存
`sources/research_litmap04_decisive_arxiv.xml`。

## 去重与排序

`experiments/phase3/build_litmap04_search_index.py` 对 title 作 normalization，合并
family/backend/ID/DOI/URL，并与既有 `research_*.xml/json` 去重标记。确定性输出：

- raw records：555；
- unique normalized titles：523；
- prior-search duplicates：81；
- heuristic relevance score `>=10`：56。

输出：

`experiments/results/LITMAP-04_round1/SEARCH_INDEX.tsv`

索引只用于 routing；heuristic score、venue 和 citation count 不作为 mechanism
证据。

## 正文 / appendix 核查

共核查 14 篇决定性 primary sources：

| ID | Source | 状态 / 本轮作用 |
|---|---|---|
| `2407.20454v2` | CoMMIT | direct component optimization；generic convergence，不是 held-out risk |
| `2412.12359v2` | MoReS / LLaVA Steering | direct representation steering；依赖 attention proxy、rank/layer choices |
| `2509.14735v1` | DPA | proxy LLM + image/text token weighting；多阶段且复用 blind/no-image family |
| `2603.14493v1` | Fine-tuning MLLMs Without Forgetting | controlled task-specific overfitting；需要 dataset/mixture-ratio choice |
| `2605.26656v1` | DV-SFT | direct visual-token labels；OCR-specific、loss weight/smoothing |
| `2606.22043v1` | visual-shortcut RLVR dynamics | dose/timing controls；单一 video model、RLVR、proxy/sweep |
| `2606.26387v1` | VIGIL | matched seeing/blind DPO；多组件且 MI/causal bridge 过强 |
| `2608.05131v2` | OPD-V | double-teacher on-policy token routing；4×H200、多组件/operation choice |
| `2410.09575v2` | ROSS，ICLR 2025 | latent visual denoising；额外 tokenizer/denoiser/objective choices |
| `2506.09040v2` | ASVR | semantic visual-token autoregression；额外 tokenizer/head/loss |
| `2512.15885v1` | JARVIS | masked latent prediction；target-layer choice |
| `2512.06281v1` | LaVer | EMA teacher + masking + alignment，多 component |
| `2604.12966v1` | V-GIFT | 原最小 route；本地 `VISSUP-01` instantiation 已失败 |
| `2606.17296v1` | Pareto LoRA | formal adjacent；依赖本地不存在的 image-generation objective |

OPD-V 的 ar5iv 保存页是不完整的中间响应，未据此作结论；随后获取并核查完整
`sources/litmap04_primary_2608_05131_source.tar` 中的 `main.tex`、method、实验、
ablation、hyperparameters 与 compute。没有把损坏/不完整响应当作全文证据。

## Coverage / limitations

- 本轮是 failure-driven gate，不是双人 PRISMA review。
- 14 篇中多数 2025–2026 工作仍是预印本；唯一已明确正式发表的复用关键来源是
  ROSS（ICLR 2025）。新颖性不能替代 control/bridge 核查。
- 多数 paper 以 2B–72B 模型、full/LoRA/DPO/OPSD 或额外 visual modules 为对象；
  对 4,096-coordinate MiniMind-V 的迁移必须由本地可证伪 plan 决定。
- 文献共同支持“objective/credit/task template 会改变 autoregressive MLLM
  behavior”，但没有唯一、低成本、无需权重/layer/task/data sweep 的本地
  intervention。
- 不可得全文没有导致 `INCONCLUSIVE`；决定性 sources 均有正文/appendix 或 source
  archive 可核查。

## Search decision

`NO_CANDIDATE`。当前 objective-routing literature-to-local-experiment bridge
不通过；这不是 `MECHANISM_REJECTED`。下一轮应转向新数据/表示对象，而不是以不同
名称恢复 gradient proxy、visual ablation、loss-weight 或 mixture sweep。
