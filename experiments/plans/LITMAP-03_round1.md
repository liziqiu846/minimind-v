# LITMAP-03 Round 1 — low-dimensional visual trainability mechanism gate

**日期**：2026-08-07  
**阶段**：阶段三  
**类型**：VISSUP failure-driven primary-source literature/theory gate；不训练、不运行
checkpoint、不访问 final confirmation  
**不可变性**：本文件提交后不修改检索问题、候选接受门或否定门；修订必须新 round。

## 科学问题

VISSUP 的显式 visual-necessary instruction 连 held-out rotation mechanism 都没有进入
4,096-coordinate M2-current。是否存在一个由权威 VLM/MLLM 文献直接支持的机制，
可以区分以下至少两个竞争解释，并由当前项目的唯一最小干预证伪：

1. **frozen-encoder identifiability**：当前 frozen vision encoder 已将 rotation /
   fine visual relation 变成不可线性或低成本读取的信息；
2. **trainable-subspace capacity / module allocation**：4,096 coordinates 的大部分
   有效更新方向没有分配到承担视觉适配的 module；
3. **objective competition / routing**：10,000 caption gradients 主导少量 visual
   task gradients，使视觉 target 即使可表示也没有被优化吸收。

## 失败证据约束

本轮必须同时尊重：

- `VISSUP-01` 的相同 pixels/labels/steps paired pilot 已有效完成；
- visual relative to control 的 rotation accuracy difference 为 `-0.00694`，
  95% CI `[-0.03770,0.02282]`；
- CV-Bench accuracy difference 为 `-0.00139`；
- 不允许把该失败归咎于 seed 后补 `43102/43103`；
- 不允许换 rotation ratio/task/prompt/metric/benchmark；
- `XMC-01` 已禁止 layer/kernel/rank/representation proxy sweep；
- `VISCOND-01` 已禁止 correct/no-pixel proxy rescue；
- `COMP-01` 已否定当前 caption NLL binding bridge。

新 candidate 必须改变真正不同的可干预科学对象，不能把 VISSUP 改名重跑。

## 可证伪文献假设

假设 H：如果低维 visual trainability 是当前失败的主要原因，primary literature 中
应存在至少一条直接生成式 LVLM 证据链，满足：

1. 对 frozen encoder、trainable module allocation 或 objective routing 作
   mechanism-specific intervention；
2. 在 matched data/compute/parameter 条件下排除“只是更多参数/更多 steps/更多图像”
   至少一个简单解释；
3. 报告 visual task 或 held-out vision-centric performance，而非只报告训练 loss /
   embedding 可视化；
4. 可在本项目中用一个预声明二条件实验区分至少两个上述 competing explanations。

若只有 generic LLM PEFT、CLIP/classification、事后 gradient/attention/CKA proxy、
大规模 architecture replacement 或 hyperparameter sweep，则 H 在当前证据门下不成立。

## VLM 特有性与理论边界

有效机制必须涉及 image encoder / projector / language decoder 之间的跨模态更新
可达性、分配或竞争。通用 LoRA intrinsic dimension、普通深网 lottery ticket、
单模态 catastrophic forgetting 或纯参数计数不能单独成为候选。

任何理论必须核查：

- autoregressive LVLM 还是 dual encoder/classifier；
- frozen / trainable modules 与本地设置是否一致；
- theorem 的 loss、data independence、optimization regime 和 certified object；
- 是否给出 downstream generative risk，还是仅表示/训练动力学启发。

不满足同构假设的理论只能标为 `FORMAL_ADJACENT` 或 `HEURISTIC_HYPOTHESIS`。

## 检索协议

### Backend 顺序

遵守 `research-lookup`：

1. 先检查 `sources/` 中 LITMAP-01/02、XMC round2 已保存结果，避免重复；
2. 检查 `parallel-cli`、`PARALLEL_API_KEY`、`OPENROUTER_API_KEY`；
3. 可用时优先 `parallel-cli search`，每个科学 query 同时做 academic-domain 与
   general search，并保存到 `sources/`；
4. 若专用 backend 仍不可用，记录原因后使用 arXiv、OpenAlex、Semantic Scholar
   可公开 API、conference/OpenReview/ar5iv/official repository；
5. 每个响应、失败回执、正文与 citation metadata 都保存到 `sources/` 或
   `experiments/results/LITMAP-03_round1/`，记录 URL/version/SHA。

不得安装或认证未授权付费 backend，不得伪造 citation count 或 venue 状态。

### Query families

至少覆盖以下五族，允许同义词扩展但不得转向无关 PEFT benchmark：

1. `multimodal large language model` + `parameter efficient / LoRA / adapter` +
   `vision module / projector / module selection`；
2. `large vision language model` + `frozen vision encoder` +
   `limitations / task identifiability / fine-grained / spatial`；
3. `MLLM / LVLM` + `gradient conflict / modality competition / gradient routing /
   training dynamics`；
4. `visual instruction tuning` + `which modules to tune / vision tower unfreezing /
   connector capacity`；
5. `visual reconstruction / latent target / auxiliary objective` +
   `parameter efficient / low rank / frozen encoder`。

补充 exact-title verification 只用于首轮命中的关键论文。

### 时间与质量范围

- 优先 2023–2026 autoregressive LVLM/MLLM；
- 首选 ICLR/ICML/NeurIPS/CVPR/ACL/EMNLP/ECCV 及正式 journal；
- 新预印本只有在直接机制控制独特时纳入；
- 早期/通用理论仅作正式相邻桥；
- 目标保存不超过约 800 raw records，normalized 去重；
- 全文/appendix 核查 6–12 篇决定性 primary sources，而非只读摘要。

## Evidence matrix

每篇决定性 source 至少记录：

- title、authors、year、venue/status、DOI/arXiv/version；
- model family 与规模；
- trainable/frozen modules；
- intervention 与 matched control；
- data、compute、parameter 是否匹配；
- seed / backbone / dataset replication；
- mechanism measure 与 held-out performance；
- 它支持哪个 competing explanation；
- 它不能推出什么；
- 本地最小实现成本；
- gate：`DIRECT_MECHANISM`、`FORMAL_ADJACENT`、`HEURISTIC_ONLY` 或
  `REJECT_FOR_BRIDGE`。

引用量与 venue 只用于排序，不替代全文机制核查。

## Candidate 接受门

最多保留一个新 candidate，且必须全部满足：

1. 至少两篇相互独立 primary sources 直接涉及 autoregressive LVLM，其中至少一篇
   有 matched mechanism control；
2. 不复用已失败的生成 NLL/no-pixel/无桥 representation proxy；
3. intervention 只改变 frozen encoder、module allocation 或 objective routing 中
   一个主要因素；
4. 预先明确它同时区分哪两个 competing explanations；
5. 产生方向明确、尚未运行的 mechanism prediction 与外部 performance prediction；
6. checkpoint-only test 不足时，最小训练不超过阶段三标准
   `2 conditions × 1 pilot root`，positive 才补 total 3；
7. 本地现有 A40、约 24 GB disk、M2-current artifacts 可执行；
8. 若成功，能自然导出 module-aware allocation、vision-path tuning 或
   objective-routing 原则，而非仅工程 trick。

通过门只允许登记 `NEW` 并创建新 immutable plan，不得由文献直接宣布
`PROMISING`。

## 支持标准

同时满足以下条件才支持进入新 candidate：

1. ≥2 个独立 direct autoregressive-LVLM sources；
2. ≥1 个 matched parameter/data/compute 或 competing-module control；
3. 唯一最小本地 intervention 能区分至少两个解释；
4. 有尚未检查的 mechanism + external direction prediction；
5. 不需要 layer/rank/ratio/task/metric sweep。

## 否定标准

任一项成立即拒绝对应路线，不以不同名称重引入：

1. 证据止于 CLIP/classification/dual-encoder retrieval 且无生成式 bridge；
2. 只显示某个 module 梯度/attention/CKA 相关，未作干预；
3. improvement 与更多参数、更多 compute、更多图像或 architecture replacement
   混合；
4. 需要事后选择 layer/module/rank/loss weight；
5. 本地测试只能通过换 VISSUP task/ratio/seed 进行；
6. intervention 无法区分至少两个 competing explanations。

若五个 query families 都只得到上述证据，则本 literature gate 记录
`NO_CANDIDATE`，转向 Research Envelope 内其他科学对象，而不是启动无机制训练。

## 无法判断标准

只限：

- 决定性全文/appendix 无法获得且摘要不足；
- source 身份/version/venue 无法验证；
- competing controls 关键实现细节未公开；
- 本地 artifact/resource 可行性无法只读核查。

无法判断不自动获得训练预算；写入 `REVIEW_QUEUE` 后转向下一 route。

## 最小执行

1. 提交本 plan；
2. backend/env preflight 与 existing-source dedup；
3. 五族检索，保存全部 raw responses；
4. title/abstract 去重与 relevance ranking；
5. 全文核查 6–12 篇决定性 sources；
6. 写 evidence/applicability matrix；
7. 只读核查唯一候选的本地 artifact gate；
8. 作出 `SELECT_ONE_CANDIDATE` 或 `NO_CANDIDATE`；
9. 更新 registry/state/nightly，提交 source hashes。

本轮不运行 GPU、checkpoint 或新训练。

## 所需资源

- GPU：0；
- CPU/RAM：轻量 API parsing、PDF/HTML text extraction；
- disk：预计 <1 GB，保存 raw search/primary sources；
- final confirmation：不访问；
- candidate training：本轮禁止，必须另建并 commit plan。
