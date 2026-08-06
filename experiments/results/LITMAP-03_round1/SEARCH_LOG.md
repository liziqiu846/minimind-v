# LITMAP-03 Search Log

## 检索边界

- 检索日：2026-08-07（Asia/Shanghai）。
- 冻结问题：`VISSUP-01` 失败后，区分 frozen-encoder identifiability、
  trainable-subspace/module allocation 与 objective competition/routing。
- 本轮只做 literature/theory gate 与本地只读可行性核查；0 GPU、0 checkpoint
  inference、0 training、未访问 final confirmation。
- 已完整遵守 `research-lookup`。专用 backend 不可用：
  `parallel-cli`、`PARALLEL_API_KEY`、`OPENROUTER_API_KEY` 均不存在；因此按冻结
  fallback 使用 arXiv、OpenAlex、Crossref、ar5iv 与 arXiv PDF。

## 原始检索与去重

五族冻结 query 分别覆盖：

1. MLLM PEFT 与 projector / vision module；
2. frozen vision encoder 的 fine-grained / spatial limitation；
3. MLLM gradient conflict / modality competition / routing；
4. visual instruction tuning 中应训练哪些 modules；
5. visual target / reconstruction 与低秩或 frozen encoder。

保存的五组 arXiv 响应共 41 records，五组 OpenAlex 响应共 500 records，合计
541 raw records。`SEARCH_INDEX.tsv` 对标题做 Unicode NFKD、case-fold 与非字母数字
删除后的确定性去重，得到：

- 480 个 unique titles；
- 45 个标题已存在于先前 LITMAP/XMC 检索；
- 95 个 heuristic relevance score `>=10`。

score 只用于安排阅读顺序，不是证据等级。完整 abstract、DOI、arXiv/OpenAlex ID、
venue、URL、query-family 与 prior-duplicate 标记均保留在索引中。

## 决定性全文

保存并核查 11 篇 primary sources 的正文与附录：

| arXiv | 版本/截至检索日状态 |
|---|---|
| `2406.05130v1` | *Empirical PEFT for MLLMs*；Findings ACL 2024，DOI `10.18653/v1/2024.findings-acl.598` |
| `2406.16860v2` | Cambrian-1；NeurIPS 2024 Oral（arXiv comment） |
| `2408.06610v1` | CROME；preprint |
| `2603.21077v2` | CoVFT；CVPR 2026（arXiv comment） |
| `2405.02246v1` | *What matters when building VLMs?*；NeurIPS 2024，DOI `10.52202/079017-2789` |
| `2403.13447v1` | HyperLLaVA；preprint |
| `2402.10896v2` | PaLM2-VAdapter；technical report |
| `2312.06742v2` | Honeybee；CVPR 2024 camera-ready（arXiv comment） |
| `2411.10928v1` | SPIDER / *Learn from Downstream*；preprint |
| `2505.12884v2` | TinyAlign；Findings ACL 2026，DOI `10.18653/v1/2026.findings-acl.223` |
| `2606.17296v1` | Pareto LoRA；preprint |

ar5iv 成功转换 10 篇；Cambrian-1 的 ar5iv 页面明确报告 fatal conversion，故保留该
失败 HTML，并另存 6.1 MiB arXiv PDF 与本地 PDF text extraction。统一的
`research_litmap03_decisive_arxiv.xml` 核验版本、作者、更新时间及 arXiv comment。

Crossref exact-title 请求成功保存 6 个响应；其余 5 个请求收到 HTTP 429。由于 arXiv
identity 和正文已足以核验，而且 venue 不决定机制 gate，本轮记录 rate limit 后没有
高频重试。

## 本地 artifact gate

- 当前 M2-current 是同一 frozen base 上的 11 个 hashed-LoRA targets，coordinate
  分配为 `vision=582/projector=2327/language=1187`，总数 4,096。
- 已有 private-coordinate constructor 可在不改变 base tensors、target registry、
  mapping rule 或总 coordinate 数时构造任意正整数 module dimensions。
- 唯一无比例搜索的 projector-dominant 极端分配冻结为
  `vision=1/projector=4094/language=1`。保留两个 1-coordinate group 是当前
  constructor 的正维度约束，不是事后选择。
- 对 current 与 projector-dominant 两组 dimensions 的 mapping-only 构造均通过：
  22 个 A/B factor mappings、4,096 total coordinates、无 unused coordinates。
- 现有 VISSUP prepared train、held-out rotation、CV-Bench-2D 与 scorer artifacts
  足够复用；没有 projector-dominant checkpoint，因此 checkpoint-only test 不足。
- 历史 `phase3_module_marginal_budget_v1` 只有未执行的 9-point/3-seed、72-run curve
  infrastructure。其 sweep 违反当前 no-sweep gate，本轮不运行、不把它当证据。
- 既有两次 VISSUP training 合计 956.8 秒、两次 scoring 合计 168.0 秒；新 candidate
  的 paired pilot 预计约 0.31 GPU-hour，positive 后 total three pairs 预计小于
  1 GPU-hour。仓库所在卷剩余约 24 GiB；artifact 增量远小于 1 GiB。
- 服务器有多张 A40/A100；核查时存在其他用户占用，但至少三张 A40 空闲。未启动
  任务。

## 覆盖限制

- 这不是双人 PRISMA systematic review。
- 公开文献没有直接研究“总计恰好 4,096 个 hashed coordinates 如何跨
  vision/projector/language 分配”；本地 prediction 是受文献约束的可证伪迁移，
  不是已证明结论。
- Cambrian-1 与 ACL 2024 对 vision encoder unfreezing 给出相反经验方向，且二者都
  未匹配 trainable parameter count。这个冲突不能靠文献裁决，正是本地固定总容量
  干预的理由。
- 文献中的 attention、gradient magnitude、UMAP 与所谓 “effective mutual
  information” 均未被当作本项目的正式视觉风险或理论证书。
