# LITMAP-02 Search Log

## 检索边界

- 检索日：2026-08-07（Asia/Shanghai）。
- 冻结问题：训练时跨模态监督信息/优化机制；不是重新搜索生成 NLL、no-pixel
  ablation 或任意 representation proxy。
- 先复用 `LITMAP-01` 和 `XMC-01_round2`，只补三类定向检索：
  1. autoregressive LVLM 的 visual under-utilization / language dominance；
  2. visually grounded instruction / self-supervised visual targets；
  3. modality competition / training-dynamics theory。
- `parallel-cli`、`PARALLEL_API_KEY`、`OPENROUTER_API_KEY` 均不存在；按
  `research-lookup` fallback 使用 arXiv、OpenAlex、Hugging Face 官方公共 API。
  OpenReview exact-title 请求返回 HTTP 403，仅记录失败，不反复重试。

## 原始检索

所有成功响应完整保存在仓库 `sources/`。主要 query family：

1. `large vision language model` + `language bias / dominance / visual dependence`；
2. `multimodal large language model` + `training dynamics / gradient conflict /
   modality imbalance`；
3. `vision language model` + `visual instruction tuning / image grounded /
   visual token`；
4. `multimodal learning` + `gradient starvation / modality competition /
   optimization imbalance`；
5. `large vision language model` + `visual representation / modality imbalance`
   + `training / collapse`；
6. `masked image modeling / visual reconstruction / self-supervised visual`
   + `MLLM / VLM`；
7. exact-title verification：`Reconstructive Visual Instruction Tuning` 与
   `Words or Vision: Do Vision-Language Models Have Blind Faith in Text?`；
8. official CV-Bench dataset access check。

arXiv 共返回 164 条，OpenAlex 共返回 404 条；合计 568 records、532 个 normalized
unique titles。OpenAlex 的 broad total count 与相关性噪声很大，未把排序或引用量
直接作为机制证据。

## 正文核查

通过 ar5iv 保存并阅读全文/附录的 6 篇决定性 primary sources：

| arXiv | 版本/状态（截至检索日） | 作用 |
|---|---|---|
| `2410.09575v2` | ROSS；ICLR 2025 | 同数据/架构下 latent reconstructive visual instruction；已发表主要证据 |
| `2503.02199v1` | Words or Vision；CVPR 2025，DOI `10.1109/CVPR52734.2025.00366` | text/multimodal mixture 的受控实证与有界-loss ERM theorem |
| `2506.09040v2` | ASVR；arXiv preprint | semantic vs appearance reconstruction 的机制对照 |
| `2512.15885v1` | JARVIS；arXiv preprint | masked latent prediction vs unmasked alignment 对照 |
| `2512.06281v1` | LaVer；arXiv preprint | masked image modeling / EMA teacher 路线 |
| `2604.12966v1` | V-GIFT；arXiv preprint | 三 seed、多 backbone、matched-compute 与 single-image 控制的最直接数据干预 |

正文 hash 见 `SOURCE_SHA256.txt`。这些论文中的 attention、TVI、visual
reconstruction loss 均未被当作本项目的正式视觉风险或互信息。

## 本地 artifact gate

- 冻结训练数据：10,000 draws，parquet SHA
  `3c3d90c525f43200d35ebd5b4ac1719c8336d278aecbf7e929997c8401b1d5ce`；
  公开读取的仅是 train，不是 final confirmation。
- schema 含 canonical conversation、原始 image bytes、image SHA 和冻结 token
  records；抽查显示为 256×256 自然图像与长 caption，能够从同一 draw
  确定性构造 90° 倍数 rotation instruction。
- M2-current 训练结构为固定 4,096 coordinates（language 1,187、projector 2,327、
  vision 582），3 epochs、1,875 optimizer steps；历史单 run 约 715 秒 A40。
- 现有 checkpoint 没有 visually necessary instruction intervention，不能回答因果
  问题；最小二条件 paired pilot 预计约 0.4 GPU-hour，完整 3 pairs 约 1.2
  GPU-hours，位于现有服务器资源等级。
- 官方 `nyu-visionx/CV-Bench` revision
  `bc284db50d036958861cb60cdd7b77612052ce0d` 公开、Apache-2.0、非 gated，可作为
  新模型尚未查看的外部 vision-centric prediction panel；真正下载/评分仍需下一
  immutable plan。

## 覆盖限制

- 这是 failure-driven mechanism gate，不是双人 PRISMA systematic review。
- V-GIFT、ASVR、JARVIS、LaVer 均为较新预印本；V-GIFT 的 MMStar 增益只有
  `+0.2` 至 `+1.1` points，且正文虽称三 seed 平均但未报告方差。
- 现有正式 theorem 控制 text/multimodal mixture 的 ERM risk decomposition，
  不直接证明 rotation instruction 或 MiniMind-V 的泛化改善。
- 本地 MiniMind-V 只训练低维 coordinates；从 7B full/LoRA 结果向该模型迁移必须
  由 paired pilot 否证，不能靠文献宣布成立。
