# PROJALLOC-01 Round 1 — fixed-total projector allocation paired pilot

**日期**：2026-08-07
**阶段**：阶段三 mechanism-intervention training；不是阶段四正式算法主实验
**类型**：从零训练的固定总容量二条件干预 + 新模型方向 prediction test
**不可变性**：本文件提交后不得修改 allocation、data、mapping roots、optimizer、
steps、panel、metric、effect threshold 或判定标准；修订必须创建新 round，且只允许
明确的 implementation / data / metric confound rescue。

## 科学问题

在 frozen base、11 个 target tensors、总 4,096 trainable coordinates、
visual-necessary training data、optimizer steps 与评分方式完全相同时，把低维更新容量
集中到跨模态 projector，能否比当前 vision/projector/language allocation 更有效地
吸收 visual cue，并改善未见 task 的真实表现？

本轮只裁决：

> 当前 VISSUP visual signal 没有进入模型，是否主要因为 fixed-total trainable
> subspace 在 module 间的 allocation 不利，而 projector bridge 容量不足。

不同时研究 vision-heavy allocation、objective routing、rotation ratio 或新 proxy。

## 可证伪假设与 competing explanations

假设 H：frozen vision encoder 已保留可由当前模型利用的 rotation / spatial cues，
但 current allocation `vision=582/projector=2327/language=1187` 给跨模态 projector
的低维容量不足。若 H 成立，在总 coordinate 数固定为 4,096 时，把分配改成
`vision=1/projector=4094/language=1` 应同时：

1. 明显提高 held-out rotation accuracy，证明 intervention 改变了预期 mechanism；
2. 方向性提高 CV-Bench-2D accuracy 与 gold margin，证明变化不只拟合 rotation
   training task。

该实验区分：

- **projector-allocation bottleneck**：frozen features 可读，但 current projector
  subspace 容量不足；
- **non-projector limitation**：增加 projector allocation 后仍不能吸收 visual cue，
  因而 frozen-feature identifiability、objective competition 或其他机制仍可能是
  上限。

若 projector-dominant 没有同时达到预注册 mechanism 与 external 门，则 H 至少在
当前 frozen-base、hashed-coordinate、visual-necessary setting 下被否定。不得改成
vision-heavy、折中比例或运行旧 9-point sweep 来营救。

## VLM 特有性与理论边界

projector 是把视觉 encoder features 映射到 autoregressive LLM token space 的跨模态
桥；在 fixed-total trainable subspace 内改变其 allocation，是生成式 VLM 特有的
训练可达性干预，而不是仅比较通用参数量。

LITMAP-03 的 ACL 2024 PEFT、CROME 与 Cambrian-1 只证明 module trainability 值得
干预，并对 connector-vs-encoder 给出冲突经验方向。公开文献没有固定总计恰好
4,096 个 hashed coordinates，也没有给出本实验 held-out risk 的正式定理。因此 H
是：

> 受 primary literature 约束的启发性机制假说。

不得把本轮结果称为正式泛化界、互信息、已证明因果中介或普适 projector 定律。

## 为什么 existing checkpoint 不足

- VISSUP root `43101` 的两个 checkpoint 都使用 current
  `582/2327/1187` allocation；
- 历史 M2/M3 checkpoints 没有 projector-dominant `1/4094/1` 条件；
- 旧 `phase3_module_marginal_budget_v1` 只有未执行的
  9-point × 3-seed / 72-run sweep infrastructure，违反本轮 no-sweep gate；
- checkpoint-only representation、no-pixel 与 caption-NLL routes 已分别被
  XMC-01、VISCOND-01、COMP-01 否定，不能换名作为 allocation test。

因此必须新训练两个 matched conditions，且不得复用旧 root `43101` current 模型作
control。

## 冻结训练数据

两个条件逐字节复用 VISSUP-01 round2 的同一个 `visual-necessary` parquet，不重新
生成、不使用 `label-revealed`：

- path：
  `/home/lizhaohui/lzq/phase3_runtime/vissup01/prepared_round2/train_visual_necessary.parquet`
- SHA-256：
  `52cd2672a60c1dcf834ad8795585412b8f0c96ac9f921d83bfd353e1e5628ee5`
- rows：`11,008`；
- base：10,000 caption draws；
- rotation injection：1,008 rows；
- mixture share：`9.16%`；
- prompt：固定 `Hint code: X` 的 VISSUP visual-necessary prompt；
- assistant target：对应 A/B/C/D gold letter；
- base parquet SHA-256：
  `3c3d90c525f43200d35ebd5b4ac1719c8336d278aecbf7e929997c8401b1d5ce`。

审计 artifacts 固定为：

- `data_audit.json` SHA-256
  `26999a4451bc094ce6e148bcb1481d44efc5f9da58d9c727609d3b67d7400bea`；
- `train_injection_manifest.json` SHA-256
  `aca223f139f5e16c76a2a70b4fe71e8c85d6db44b3fa7eb883fd3b9aed1df8d7`；
- `heldout_rotation_manifest.json` SHA-256
  `131be931c243b863b91121664b8e60db817d82a234d4fe3c26d206531f8311cf`；
- `cvbench_manifest.json` SHA-256
  `32b9b6212e2e3578e447d9d73c33e08d8296ab7038f4b7c6e8be0e7c750f2949`。

任一 runtime artifact 与冻结 SHA 不符即停止模型运行，记为 asset/implementation
failure；不得重新抽样数据。

## 冻结二条件 allocation

### Control：`current-allocation`

- language：`1,187`；
- projector：`2,327`；
- vision：`582`；
- total：`4,096`。

### Intervention：`projector-dominant`

- language：`1`；
- projector：`4,094`；
- vision：`1`；
- total：`4,096`。

`1/4094/1` 是现有 constructor 要求三个 module dimension 均为正整数时的唯一
projector 极端；不是从结果中选择。两个条件都保留完全相同的 11 个 wrapped target
tensors 和 frozen base，不删除 vision/language targets。禁止测试 `0/4096/0`、
vision-heavy、50/50、折中比例或任何 additional point。

## 冻结 mapping roots 与训练配置

- model group：`M2` / M2-current target registry；
- Stage 2 protocol SHA-256：
  `4a15ae6697081098973998f7340702368403fa81f39d6c8ed43172b74a55b5b3`；
- pilot mapping root：`43201`；
- 只有 pilot positive 才补完全相同的 `43202`、`43203`；
- roots `43102/43103` 继续属于被拒绝的 VISSUP，不得运行；
- 每个 paired root 的两个 conditions 使用相同 mapping root；
- 每个 run 从 exact-zero coordinates 开始；
- train seed：`2026`；
- learning rate：`0.05`；
- optimizer：Stage 2 原 AdamW 设置；
- epochs：`3`；
- micro batch：`4`；
- gradient accumulation：`4`；
- effective batch：`16`；
- steps：每 epoch `688`，total `2,064`；
- schedule：与 VISSUP round2 相同、终点 `T=2,064` 的 cosine schedule；
- bfloat16 autocast；
- global gradient clipping：`1`；
- single GPU；
- 全部 base parameters frozen；
- 两条件逐 epoch permutation、image/token rows、labels、steps 完全相同。

paired root 控制 deterministic mapping generator 的 root，但不同 dimensions 必然
产生不同 module-specific mapping。它不能使两个 function-space bases 相同；这属于
allocation intervention 的限制，必须在结论中保留。

## Held-out rotation mechanism panel

逐字节复用 VISSUP-01 round2 的 1,008-image manifest、rotated files、prompt 和
scorer：

- images 与 rotation injection 的 normalized pixel SHA 不重叠；
- 0/90/180/270° 各 252；
- 统一使用 `Hint code: X`；
- 对 A–D 的 `letter + EOS` teacher-forced mean NLL 做 argmin；
- tie 按 `A<B<C<D`；
- primary mechanism metric：1,008 独立图像等权 accuracy；
- directional diagnostic：mean gold-vs-three-distractors NLL margin；
- paired bootstrap：图像单位、10,000 次、seed `20260807`。

这些图片在 base caption rows 中出现过，只称 held-out rotation task transfer，不称
unseen-image generalization。

## CV-Bench-2D external panel

复用已冻结的官方完整 variable-choice panel：

- repository：`nyu-visionx/CV-Bench`；
- revision：`bc284db50d036958861cb60cdd7b77612052ce0d`；
- file SHA-256：
  `33196034ef4bf3265cae4a7ff5c4071b2ff1cc21123e8e285c6a91393897ecbc`；
- official 2D rows：`1,438`；
- independent normalized-pixel groups：`1,438`；
- choices：2–6，按每行 official A–F inventory；
- 与完整 10,000-row base train 的 exact normalized-pixel overlap：`0`。

每行对所有合法 `letter + EOS` 计算 teacher-forced mean NLL，prediction 为最小
NLL label，tie 按字母序。row gold margin 为其他合法 labels 平均 NLL 减 gold NLL。
primary external metric 先在 pixel group 内平均 correctness，再对独立 image groups
等权；gold margin 同样 image-group weighted。paired bootstrap 以 image group 为
单位、10,000 次、seed `20260807`。

CV-Bench 已用于 VISSUP-01 的 ordinary held-out selection 判定，因此不是新的独立
final confirmation set；但 root `43201/43202/43203` 的两个 allocation conditions
尚未训练，更没有任何该 candidate 的 model output。方向和阈值在查看新模型前冻结。
不得访问项目 final confirmation，也不得把本轮结果称为独立最终确认。

## 最小执行顺序

1. 提交本 immutable plan；
2. 实现 candidate-specific custom-dimension trainer、scorer 与 analyzer；不修改旧
   VISSUP 原始结果；
3. 运行 asset SHA、dimension sum、22 mapping、zero-unused-coordinate、
   same-data/permutation、frozen-parameter、synthetic metric 与 analyzer unit tests；
4. 每条件最多 2 samples 做非科学 smoke，只检查 forward/backward、finite
   loss/gradient、frozen hashes 与 receipt，不聚合科学结果；
5. 固定顺序完整训练 root `43201`：先 `current-allocation`，再
   `projector-dominant`；
6. 两个训练都完成前不运行任何 scientific scoring；
7. 两模型完成后统一评分 held-out rotation 和完整 CV-Bench-2D，并一次性判定；
8. 只有 `PILOT_POSITIVE` 才补完全相同的 roots `43202`、`43203`；
9. total 3 paired roots 后执行一次最终判定。

不得只训练 intervention，不得在 current 训练后先看分数，不得复用 root `43101`
control，不得运行旧 9-point curve。

## Pilot escalation / 支持标准

root `43201` 必须全部满足：

1. 两 run 的 frozen base、11 target names、total coordinates、data SHA、
   row/permutation SHA、labels、optimizer steps 与 train seed 匹配；初始/final
   frozen parameter hash 相同且所有 loss/gradient finite；
2. mapping gate：两条件各 22 个 A/B factor mappings、0 unused coordinates，
   recorded dimensions 分别严格等于 `1187/2327/582` 与 `1/4094/1`；
3. held-out rotation：
   `accuracy_projector - accuracy_current >= 0.050`，paired-bootstrap 95% CI lower
   `>0`，且 `accuracy_projector >=0.300`；
4. CV-Bench-2D：
   `accuracy_projector - accuracy_current >=0.010`，且
   `margin_projector - margin_current >0`。

全部满足才记 `PILOT_POSITIVE` 并补两个 roots。等于 accuracy effect threshold 视为
满足；CI lower 与 margin 必须严格为正。pilot positive 不是科学结论。

## Total 3 roots 最终支持标准

若 pilot positive，保持全部配置不变补足 roots `43202/43203`，并要求：

1. 三个 root 的 rotation accuracy difference 全部 `>0`；
2. 至少 2/3 roots 的 rotation difference `>=0.050` 且各自 paired-bootstrap
   95% CI lower `>0`，三 root 等权 mean `>=0.050`；
3. 三个 root 的 CV-Bench accuracy difference 全部 `>0`；
4. 至少 2/3 roots 的 CV-Bench difference `>=0.010`，三 root 等权 mean
   `>=0.010`；
5. 三 root 等权 mean CV-Bench gold-margin difference `>0`；
6. Count 与 Relation 的三 root 等权 mean accuracy difference 均 `>0`。

全部满足只标记 `PROMISING` / `REVIEW_QUEUE`，不得宣布阶段四或正式训练算法。

## 否定标准

有效运行时任一项成立即 `REJECT_IDEA`：

1. root `43201` 未满足全部 pilot 标准，包括方向为正但小于阈值；
2. rotation difference `<=0`、CI lower `<=0` 或 projector absolute accuracy
   `<0.300`；
3. CV-Bench accuracy difference `<0.010` 或 margin difference `<=0`；
4. total 3 roots 后任一最终支持项失败；
5. 方向不稳定或效果只由一个 task family 驱动。

effect 小、CI 跨零、seed 不支持、training loss 不漂亮均是科学证据。不得换比例、
换 metric/proxy、换 task/subset、追加 seed、改变 LR/epoch 或只保留 favorable root。

## 无法判断标准

只限：

1. 冻结 data/panel/model/tokenizer/processor artifact 无法通过 SHA 或 decode gate；
2. 明确 implementation bug、corrupted data、wrong checkpoint、preprocessing
   mismatch、metric implementation error 或 job failure；
3. 外部系统终止导致 paired condition 缺失且无法从合法 checkpoint 恢复；
4. 实验实现被证明没有真正隔离 allocation，例如 total coordinates 或训练 rows
   不匹配。

最多允许一次由上述已证明 confound 触发的新 round rescue。统计能力不足、effect
太小或 prediction 失败不属于 rescue；`INCONCLUSIVE` 不自动获得更多训练预算。

## 可能混杂与结论限制

- 相同 coordinate count 不等于两个 module allocation 具有相同 function-space
  volume、conditioning、update norm 或实际 checkpoint 描述 overhead；
- `1/4094/1` 是极端构造；positive 只说明当前 setting 下 projector-dominant
  allocation 有效，不证明它全局最优；
- positive 仍可能来自 projector 的尺度/敏感度而非可解释的视觉语义 bottleneck；
  后续需要新 prediction 区分，但本轮不追加 proxy；
- negative 不能单独证明 frozen encoder 不可读或 objective competition 成立，只能
  否定当前 projector-capacity explanation；
- held-out rotation images 仍以 caption rows 出现在训练中；
- CV-Bench 已进入 ordinary selection history，不是 final confirmation；
- exact pixel audit 不能排除未知预训练或 near-duplicate；
- forced-choice letter NLL 不完全等于自由生成真实性能。

## 所需资源

- pilot：2 trainings + 2 models scoring，按既有 VISSUP receipt 预计约
  `0.31 GPU-hour`；
- pilot positive 后总上限：2 conditions × 3 roots = 6 trainings，预计 `<1
  GPU-hour`；
- 单张空闲 A40 顺序运行，不多卡扩大预算；
- runtime 新目录：
  `/home/lizhaohui/lzq/phase3_runtime/projalloc01/`；
- 复用 285 MiB prepared data，不复制 base model；新增 coordinates、receipts、
  raw scores 与 logs 预计远小于 1 GiB；
- stable training 后每 10–20 分钟检查一次；
- 等待期间可做不接触新模型输出且不改变判定的理论/文献工作；
- final confirmation：不访问。
