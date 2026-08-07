# LITMAP-04 Round 1 — objective routing and task-specific absorption gate

**日期**：2026-08-07
**阶段**：阶段三
**类型**：PROJALLOC failure-driven primary-source literature/theory gate；不训练、
不运行 checkpoint、不访问 final confirmation
**不可变性**：本文件提交后不修改 targeted question、query families、candidate
接受门或判定标准；修订必须创建新 round。

## 科学问题

在相同 pixels/labels/steps 的 visual-necessary intervention 与 fixed-total
projector-dominant allocation 都未改善 held-out mechanism 或外部任务后，是否存在
由 direct autoregressive-LVLM primary evidence 支持的训练动力学机制，能够区分：

1. **frozen-feature mismatch**：vision encoder 输出不包含当前任务可由 projector/
   decoder 使用的充分结构，或其几何与 autoregressive token objective 不匹配；
2. **task-specific absorption without transfer**：训练只吸收当前 target/prompt 的
   shortcut，未形成能迁移到 held-out rotation 或 CV-Bench 的跨模态结构；
3. **objective competition / gradient routing**：caption/language token gradients
   在共享低维更新空间中压制、冲突或稀释 visual-dependent gradients；
4. **optimization incapacity outside projector allocation**：问题在 objective-level
   update geometry、target construction 或跨模态 credit assignment，而非把更多
   coordinates 分给 projector。

本轮只寻找一个能以单一主要因素干预、同时给出 mechanism 与 external prediction
的新 candidate；不直接选择算法、不训练模型。

## 失败证据约束

本轮必须同时尊重：

- `VISSUP-01` 的 paired visual-necessary vs label-revealed pilot 有效完成，但
  held-out rotation difference=`-0.00694`、CV-Bench difference=`-0.00139`；
- `PROJALLOC-01` 的 paired invariants 全通过，但 projector-dominant 的 rotation
  difference=`+0.01290`、95% CI 跨 0、absolute accuracy=`0.26389`，CV-Bench
  difference=`-0.01391` 且 margin difference=`-0.05817 bits/token`；
- 禁止补 `43102/43103` 或 `43202/43203`、搜索 allocation、改变 rotation
  task/ratio/prompt、换 metric/proxy 或重复相近实验；
- `COMP-01` 已否定 caption+EOS NLL relation bridge；
- `VISCOND-01` 已否定当前 correct-image vs no-pixel 构念；
- `XMC-01` 已禁止 layer/kernel/rank/representation proxy sweep。

新路线必须解释这些失败暴露的区分问题，不能将已有 candidate 换名 rescue。

## 可证伪文献假设

假设 H：如果 objective competition、gradient routing 或 task-specific absorption
是当前值得优先检验的 VLM-specific explanation，primary literature 中应存在至少一条
可迁移证据链，同时满足：

1. 研究对象是带 autoregressive language decoder 的 LVLM/MLLM，而非仅 CLIP、
   dual encoder 或 classifier；
2. 对 objective、gradient flow、token/sample credit assignment 或 visual-language
   representation matching 作 mechanism-specific intervention；
3. 有 matched control，至少排除更多 data、parameters、steps/compute、不同
   backbone 或完整 architecture replacement 中的一项简单解释；
4. 同时报告 intervention 对预期机制或 in-domain visual learning 的影响，以及
   held-out/外部 vision-centric performance；
5. 可转成当前 MiniMind-V 上一个无需 loss-weight/rank/layer/task sweep 的预声明
   二条件实验，并区分上述至少两个 competing explanations。

若检索只得到 attention/gradient visualization、训练 loss 相关、通用 multitask
gradient surgery、CLIP/classification、更多视觉数据/参数或事后挑选 loss weight，
则 H 在当前证据门下不成立。

## VLM 特有性与理论边界

有效机制必须依赖图像表示进入 autoregressive decoder 后的跨模态 credit assignment、
visual-dependent token supervision、共享参数更新冲突或 representation/objective
matching。通用多任务优化、单模态 catastrophic forgetting、普通 language-model
token reweighting或参数量规律不能单独成为候选。

每项形式或机制主张必须核查：

- autoregressive LVLM、dual encoder 还是 classifier；
- frozen/trainable modules 与数据流；
- loss/objective 的单位、gradient 定义与 independence 假设；
- intervention 是否真的操纵 claimed mechanism；
- certified object 是 optimization dynamics、representation alignment、training
  risk 还是 held-out semantic risk；
- 外部任务改善是否与 mechanism measure 同时出现。

不能同构迁移的理论只标记为 `FORMAL_ADJACENT` 或 `HEURISTIC_HYPOTHESIS`，不得
当作当前风险定理。

## 检索协议

### Backend 顺序

遵守 `research-lookup`：

1. 先检查 `sources/` 中 LITMAP-02/03 与 XMC round2 的保存结果和 title index；
2. 检查 `parallel-cli`、`PARALLEL_API_KEY`、`OPENROUTER_API_KEY`；
3. 可用时对每个科学 query 执行 academic-domain 与 general 两次
   `parallel-cli search`，全部用 `-o` 保存到 `sources/`；
4. 专用 backend 不可用时，保存失败原因，再使用 arXiv、OpenAlex、Crossref、
   ar5iv/OpenReview/conference proceedings 与 official repository；
5. 保存原始响应、exact metadata、全文/appendix、URL/version 和 SHA-256。

不得安装或认证未授权付费 backend；不得只凭搜索摘要作决定，也不得伪造 citation、
venue 或 peer-review 状态。

### Query families

首轮严格覆盖以下五族；同义词扩展可以加入，但不得转向 broad PEFT survey：

1. `autoregressive multimodal large language model` + `gradient conflict /
   modality imbalance / modality competition / optimization dynamics`；
2. `visual instruction tuning` + `visual token gradient / language token dominance /
   loss contribution / credit assignment / gradient routing`；
3. `large vision-language model` + `task-specific overfitting / visual shortcut /
   transfer / generalization after instruction tuning`；
4. `frozen vision encoder` + `autoregressive objective alignment / feature mismatch /
   representation alignment / connector bottleneck`；
5. `multimodal LLM` + `auxiliary visual objective / gradient balancing / objective
   routing / visual representation distillation` + `matched control / ablation`。

exact-title verification 只用于首轮命中的决定性论文，不计作新发现 query family。

### 时间与质量范围

- 优先 2023–2026 autoregressive LVLM/MLLM；
- 首选 ICLR/ICML/NeurIPS/CVPR/ACL/EMNLP/ECCV 及正式 journal；
- 新预印本仅在提供独特 mechanism intervention/control 时纳入；
- 通用理论只作 formal-adjacent bridge；
- 目标不超过约 750 raw records，并按 normalized title 去重；
- 全文/appendix 核查 8–14 篇决定性 primary sources。

## Evidence matrix

每篇决定性 source 至少记录：

- title、authors、year、venue/status、DOI/arXiv/version；
- model family、scale 与 autoregressive/dual-encoder 类型；
- frozen/trainable modules；
- objective、gradient/credit mechanism 与 intervention；
- matched control 及 data/compute/parameter/backbone 是否匹配；
- seed、backbone、dataset replication；
- mechanism/in-domain measure 与 held-out/external performance；
- 支持或反对哪个 competing explanation；
- theorem/proposition 的 assumptions、proof idea 与 certified object（若有）；
- 它不能推出什么；
- 本地单一最小实现与资源成本；
- gate：`DIRECT_MECHANISM`、`FORMAL_ADJACENT`、`HEURISTIC_ONLY` 或
  `REJECT_FOR_BRIDGE`。

venue/citation 只用于排序，不能替代全文 mechanism/control 核查。

## Candidate 接受门

最多保留一个新 candidate，且必须全部满足：

1. 至少两篇相互独立 primary sources 直接研究 autoregressive LVLM，其中至少一篇
   有 matched mechanism control；
2. 至少一项证据同时观察 mechanism/in-domain change 与 held-out/external
   vision-centric direction，而非只有训练 loss 或可视化；
3. intervention 只改变 objective routing、gradient interaction、visual target
   credit 或 frozen-feature/objective matching 中一个主要因素；
4. 能区分至少两个 competing explanations，并有明确 falsifier；
5. 不复用 rotation task/ratio/prompt rescue、projector allocation search、追加
   seed、caption NLL/no-pixel 或无桥 representation proxy；
6. 产生尚未运行、方向明确的 mechanism prediction 与 external performance
   prediction；
7. 不需要 loss weight、layer、rank、module、task、data subset 或 metric sweep；
8. checkpoint-only test 不足时，本地最小训练不超过
   `2 conditions × 1 paired pilot root`，positive 后才可补 total 3；
9. 当前 A40、M2-current artifacts 与可用磁盘能够执行；
10. 若成功，能自然导出 objective-routing、gradient-balancing、visual-credit 或
    representation-matching 原则，而不是一次性 engineering trick。

通过只允许登记 `NEW` 并另建 immutable experiment plan，不得由文献直接宣布
`PROMISING`。

## 支持标准

必须同时满足：

1. ≥2 个独立 direct autoregressive-LVLM sources；
2. ≥1 个 matched mechanism control；
3. ≥1 项 source 同时提供 mechanism/in-domain 与 held-out/external evidence；
4. 唯一最小干预能区分至少两个解释；
5. 有未查看的 mechanism + external direction prediction；
6. 不需要 sweep 或恢复已失败 candidate。

## 否定标准

任一项成立即拒绝对应路线，不以不同名称重引入：

1. 证据止于 CLIP/classification/dual-encoder 或通用 multitask optimization；
2. 只有 attention、gradient norm/cosine、CKA 或 loss correlation，没有机制干预；
3. improvement 与更多 data/parameters/steps、不同 backbone 或 architecture
   replacement 混杂；
4. 只能事后选择 loss weight、layer、module、rank、task、subset 或 proxy；
5. 本地测试必须换 VISSUP task/ratio/prompt、PROJALLOC allocation 或加 seed；
6. 只改善训练/in-domain task，未提供可预注册的 external transfer prediction；
7. intervention 不能区分至少两个 competing explanations。

若五族都只得到上述证据，则记录 `NO_CANDIDATE`，把失败写入 registry/review，并
转向 Mission Envelope 内新的数据或表示对象；不得无机制启动 `OBJ-01`。

## 无法判断标准

只限：

- 决定性全文/appendix 无法获得且摘要不足；
- source identity/version/venue 无法核实；
- matched control 或实现细节未公开；
- 本地 artifact/resource feasibility 无法只读确认。

`INCONCLUSIVE` 不自动获得训练预算；记录后继续其他 candidate search。

## 最小执行

1. 提交本 plan；
2. backend/env preflight 与 existing-source/title dedup；
3. 五族检索并保存全部 raw responses；
4. normalized title 去重、prior-overlap 标注与 relevance ranking；
5. 全文/appendix 核查 8–14 篇决定性 sources；
6. 写 evidence/applicability matrix；
7. 只读核查唯一候选的 local feasibility；
8. 作出 `SELECT_ONE_CANDIDATE` 或 `NO_CANDIDATE`；
9. 更新 registry/state/active question/review/nightly，提交 source hashes。

本轮 GPU、checkpoint inference 与训练均为 0。

## 所需资源

- GPU：0；
- CPU/RAM：轻量 API parsing、PDF/HTML extraction 与索引；
- disk：预计 <1 GB；
- final confirmation：不访问；
- candidate experiment：本轮禁止；后续必须另建并 commit immutable plan。
