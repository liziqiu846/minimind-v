# 2026-08-07 VLM 泛化机制文献检索日志

## 范围与检索日

- 检索日：2026-08-07（Asia/Shanghai）
- 时间范围：2018-01-01 至 2026-08-07；更早工作仅在属于理论基础时纳入。
- 主题：跨模态数据质量/结构、跨模态表示与视觉依赖、多模态训练目标与动力学，
  以及 compression/PAC-Bayes、Rademacher、information-theoretic
  generalization、stability、spectral/identifiability、zero-shot/compositional
  generalization 等相邻理论。
- 排除：仅讨论工程规模、与未见数据泛化无关、不能区分 VLM 与普通 LLM/神经网络
  问题，或只是同一已否定路线改名的工作。

## 数据库与端点

| 数据库 | 端点 | 查询数 | 原始记录 | 去重后 |
|---|---|---:|---:|---:|
| OpenAlex broad search | `GET /works?search=...` | 12 | 360 | 285 |
| OpenAlex title verification | `GET /works?search.exact=...`，失败项改用 `search` 重试 | 32 | 160 | 146 |
| arXiv | `GET /api/query?search_query=...` | 11 | 258 | 253 |
| Semantic Scholar | `GET /graph/v1/paper/search` | 6 | 0 | 0 |

Semantic Scholar 的 6 次无密钥请求均返回 HTTP 429，因此没有把该库计入有效覆盖。
`parallel-cli`、`PARALLEL_API_KEY` 与 `OPENROUTER_API_KEY` 均不可用；没有为绕过限制
而反复重试。原始 OpenAlex JSON 与 arXiv Atom XML 均保存在本目录的 `raw/`。

## Broad-search 主题

OpenAlex broad search 的 12 组主题：

1. image-text pairing quality / data selection；
2. multimodal diversity / compositional coverage / long tail；
3. synthetic captions / recaptioning；
4. cross-modal alignment / modality gap；
5. language shortcuts / modality imbalance / visual grounding；
6. visual retention / forgetting / collapse；
7. compositional and shared/private representation；
8. contrastive versus generative objectives；
9. instruction tuning / optimization / curriculum / stability；
10. spectral multimodal contrastive theory；
11. information-theoretic / PAC-Bayes / stability；
12. OOD and compositional generalization。

arXiv 查询补充了 compositional generalization、modality gap、language bias、visual
instruction tuning、visual information、training objectives、multimodal contrastive theory、
data filtering，以及仓库理论基线列出的三篇直接理论论文。

## 筛选流程

```text
OpenAlex broad records (n=360) + arXiv records (n=258)
    -> 数据库内去重并按题名/摘要筛选
    -> 定向题名核查 OpenAlex records (n=160)
    -> 18 篇关键论文 PDF 正文核查
    -> 24 篇进入主题证据地图
    -> 5 个 candidate mechanisms
```

OpenAlex broad search 的相关性排序噪声较大，故没有把高引用排序直接当作纳入依据。
18 篇关键论文 PDF 仅下载到临时目录用于核查正文，没有写入仓库。正文核查重点是：
理论对象、数据生成假设、损失、下游任务、正式定理、实验干预与作者声明的限制。

## 已知覆盖限制

1. 这是一轮面向机制选择的系统 scoping map，不是双人筛选的完整 PRISMA systematic
   review。
2. Semantic Scholar 因限流缺失；没有 Google Scholar 专有索引覆盖。
3. 2025–2026 年结果很多仍是预印本，证据权重低于已发表顶会工作。
4. 现有正式理论主要针对 CLIP 式双编码器、谱/InfoNCE 类损失、线性 probe 或零样本
   分类；不能直接迁移为生成式 LVLM 的自回归泛化定理。
5. 历史 P/S artifact 仅作为研究动机，没有用于从同一数据中挑选“最好相关”的 proxy。

