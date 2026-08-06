# VISSUP-01 Round 2 — variable-choice schema rescue

**日期**：2026-08-07  
**阶段**：阶段三 mechanism-intervention training；不是阶段四  
**类型**：round1 pre-model schema confound 的唯一 rescue  
**不可变性**：本文件提交后不得修改；本 candidate 不再获得新的 measurement
rescue、prompt、ratio、metric、panel、seed 或 task。

## Round1 失败与允许的唯一修改

`VISSUP-01_round1` 在训练或模型评分前按 gate 停止。官方
`nyu-visionx/CV-Bench@bc284db50d036958861cb60cdd7b77612052ce0d` 的 2D split
不是计划误写的统一四选一，而是：

- 1,438 rows；
- choices：2 选 650、4 选 493、5 选 156、6 选 139；
- gold labels：A 509、B 507、C 169、D 167、E 63、F 23；
- tasks：Count 788、Relation 650；
- sources：ADE20K 633、COCO 805。

因此 round1 为 `PANEL_INELIGIBLE`，0 training、0 model outputs。round2 只允许把
外部 scorer 从写死 A–D 改为使用每题官方完整 A–F choice inventory；不删除任何题，
不改变 panel、训练干预、primary metrics 或效应阈值。

## 科学问题

在结构、base caption draws、rotated pixels、rotation labels、target format 与算力
相同时，少量必须看图的 autoregressive rotation instruction 是否比文本泄露 label
的 control 更能形成可迁移视觉能力，并改善未见 CV-Bench-2D？

## 假设与可证伪 prediction

若 caption-only supervision 没有充分迫使 4,096-coordinate MiniMind-V 吸收视觉
结构，则 `visual-necessary` 相对 `label-revealed` 应同时：

1. 提高 held-out rotation A–D forced-choice accuracy；
2. 提高完整 CV-Bench-2D 的 per-row variable-choice accuracy；
3. 提高 CV-Bench-2D gold-vs-distractor NLL margin。

如果 root `43101` 在预注册机制门或外部方向/效应门任一项失败，candidate 立即
`REJECT_IDEA`；不得再改 scorer 或训练。

## VLM 特有性与术语边界

两个训练条件使用相同 rotated pixels、gold label、assistant target、模型和训练
compute，只改变 user prompt 的 hint token 是否揭示视觉 label。它直接干预
autoregressive training sample 是否必须使用图像。

结果只能称为：

> visually necessary rotation supervision 在当前 M2-current MiniMind-V 上的
> 操作性干预效应。

ROSS、ASVR、JARVIS、LaVer、V-GIFT 是机制/设计来源；`Words or Vision` 只提供
相邻 mixture-risk 理论。不得把本轮经验量称为互信息、正式视觉风险、一般规律或
正式泛化界。

## 冻结二条件训练

除下面重述内容外，训练构造严格继承已提交的
`experiments/plans/VISSUP-01_round1.md`：

- base parquet：
  `/home/lizhaohui/lzq/minimind-v-stage2-rerun-20260721/dataset/stage2_confirm_v2_seed2028/train.parquet`
- base SHA-256：
  `3c3d90c525f43200d35ebd5b4ac1719c8336d278aecbf7e929997c8401b1d5ce`
- 10,000 caption rows 全部原样保留；
- normalized pixel SHA 按
  `SHA256("VISSUP01_IMAGE_ORDER_V1\\0" || pixel_sha256)` 排序；
- 前 1,008 个独立图像作为 rotation training injection，后 1,008 个作为 disjoint
  held-out rotation panel；
- 每组按 index modulo 4 确定 `0/90/180/270°`，各 252；
- clockwise label 固定 `0°→A, 90°→B, 180°→C, 270°→D`；
- total rows `11,008`，augmentation/base `10.08%`，mixture share `9.16%`；
- model `M2-current`，coordinates
  `language=1,187/projector=2,327/vision=582`；
- root `43101` pilot；positive 后才补 `43102/43103`；
- exact-zero coordinates，train seed `2026`，LR `0.05`，AdamW；
- 3 epochs，micro batch 4，accumulation 4，effective batch 16；
- 688 steps/epoch，total 2,064，原 cosine 公式固定到新终点；
- single GPU、bfloat16、gradient clip 1，全部 base parameter frozen。

两个 injection prompt 仍只有 hint token 不同：

```text
<image>
The image was rotated clockwise from its natural orientation.
Hint code: {X_or_gold_letter}.
Select the applied rotation:
A. 0 degrees
B. 90 degrees
C. 180 degrees
D. 270 degrees
Answer with the option letter only.
```

- `visual-necessary` 使用 `X`；
- `label-revealed` 使用对应 `A/B/C/D`；
- assistant 均为 gold letter；
- frozen tokenizer 下 `X/A/B/C/D` 必须各为一个 user-span token；
- 两条件逐样本 sequence length、assistant target、image tokens、rotated bytes、
  labels、permutation 和 optimizer steps 必须一致。

不得改变 prompt、ratio、rotation mapping、learning rate、epoch 或任一 subset。

## Held-out rotation mechanism panel

- 使用未进入 rotation training injection 的第二组 1,008 个独立 base images；
- 评分时应用其预分配 rotation，并统一使用 `Hint code: X`；
- 逐题对 A–D 的 letter+EOS teacher-forced mean NLL 做 argmin，tie 为
  `A<B<C<D`；
- accuracy 为主机制量，gold-vs-three-distractors mean NLL margin 为辅助量；
- paired image bootstrap 10,000 次、seed `20260807`。

这些图像仍作为原始 caption rows 出现在两条件训练中，因此只称 held-out rotation
task transfer，不称 unseen-image generalization。

## CV-Bench-2D variable-choice panel

冻结来源：

- repository：`nyu-visionx/CV-Bench`；
- revision：`bc284db50d036958861cb60cdd7b77612052ce0d`；
- file：`test_2d.parquet`；
- bytes：`184,906,137`；
- SHA-256：
  `33196034ef4bf3265cae4a7ff5c4071b2ff1cc21123e8e285c6a91393897ecbc`；
- config / split：`2D / test`；
- official rows：`1,438`。

### Panel gate

1. schema 必须与 round1 audit 一致；
2. 每行 choices 数只能为 2–6，且 `answer` 必须唯一指向该行 official choice；
3. 所有 1,438 张/行图像必须可解码并规范化为 EXIF-transposed RGB；
4. 对完整 10,000-row base train 计算 normalized pixel-SHA exact overlap；
5. exact-overlap 图像对应题目必须在任何模型评分前删除并记录；剩余独立图片组少于
   official 2D 的 90% 时 `PANEL_INELIGIBLE`；
6. 不按 question length、choices 数、task、source、model output 或 difficulty
   选择 subset；
7. 不访问 validation/final confirmation。

### Variable-choice scorer

对每一行按原 official `prompt` 顺序标记：

- 2 choices：A–B；
- 4 choices：A–D；
- 5 choices：A–E；
- 6 choices：A–F。

在 official prompt 后追加：

```text
Answer with the option letter only.
```

每个合法 label 单独构造 assistant `letter + EOS`，计算 teacher-forced mean NLL。
prediction 为该行所有合法 labels 中 NLL 最小者，tie 按字母序。row gold margin 为：

\[
\frac{1}{K-1}\sum_{a\ne y}L(a)-L(y),
\]

其中 \(K\) 是该行 2–6 个 official choices。不得对不存在的 label 打分，也不得因
choice 数不同重新加权 row。

主外部量：先在 normalized pixel-SHA 内平均 row correctness，再对独立图片组等权的
accuracy。共同方向量：同样 image-group weighted 的 gold margin。官方
question-weighted accuracy、Count/Relation 与 ADE20K/COCO 分层只报告。

paired bootstrap 以独立 image group 为单位，10,000 次、seed `20260807`。

## 最小执行顺序

1. 先提交本 plan；
2. 完成 CV-Bench decode、answer、exact-overlap gate；
3. 实现 deterministic data builder、training runner、rotation/variable-choice
   scorer 与一次性 analyzer；
4. 运行 token、pixels、labels、disjoint split、same-order、synthetic NLL、
   frozen-parameter tests；
5. 每条件最多 2 samples 做非科学 smoke；
6. 固定顺序完整训练 `43101`：先 `label-revealed`，再
   `visual-necessary`；两者完成前不评分；
7. 两者都完成后一次性评分并判定；
8. 仅 `PILOT_POSITIVE` 才补完全相同的 `43102/43103`；
9. total 3 roots 后一次性最终判定。

## Pilot escalation 标准

root `43101` 必须同时满足：

1. 两 run 结构、初始 frozen hash、base rows、rotated-pixel hash、label order、
   optimizer steps 和 permutation receipt 匹配，且 loss/gradient finite；
2. rotation：
   `accuracy_visual - accuracy_revealed >= 0.050`，paired bootstrap 95% CI
   lower `>0`，且 `accuracy_visual >=0.300`；
3. CV-Bench-2D：
   `accuracy_visual - accuracy_revealed >=0.010` 且
   `margin_visual - margin_revealed >0`。

全部满足才补 roots；这不是科学结论。

## 最终支持标准

total 3 roots 必须同时满足：

1. 三个 root 的 rotation accuracy difference 全部 `>0`；
2. 至少 2/3 roots 的 rotation difference `>=0.050` 且各自 bootstrap 95% CI
   lower `>0`，三 root 等权 mean `>=0.050`；
3. 三个 root 的 CV-Bench-2D accuracy difference 全部 `>0`；
4. 至少 2/3 roots 的 CV-Bench difference `>=0.010`，三 root 等权 mean
   `>=0.010`；
5. 三 root 等权 mean CV-Bench gold-margin difference `>0`；
6. Count 与 Relation 的三 root 等权 mean accuracy difference 均 `>0`。

全部满足只记 `PROMISING` / `REVIEW_QUEUE`，不得宣布阶段四或正式算法。

## 否定标准

有效运行时以下任一项即 `REJECT_IDEA`：

1. root `43101` 未满足全部 pilot 标准，包括方向为正但小于阈值；
2. rotation difference `<=0`；
3. CV-Bench accuracy difference `<=0` 或 margin difference `<=0`；
4. total 3 roots 后任一最终支持项失败；
5. direction 不稳定、效应太小或只由一个 task family 驱动。

这些均是科学证据，不得通过调参、加 seed、换 task/panel/proxy 或只保留 subset
rescue。

## 无法判断标准

只限：

1. `DATA_INELIGIBLE` 或 `PANEL_INELIGIBLE`；
2. base / CV-Bench / tokenizer / processor / model asset 无法通过 hash 与
   deterministic gate；
3. 明确 implementation bug、corrupted data、wrong checkpoint、preprocessing
   mismatch、metric error 或 job failure导致 paired run 不能完成。

round2 已消耗唯一 schema rescue；无法判断不自动获得 round3 或更多资源。

## 可能混杂

- visual condition 比 revealed control 更难，positive 仍可能是 hard-example pressure
  或 rotation-specific inductive bias；
- held-out rotation images 在 base caption rows 中出现；
- natural orientation 对对称/近景图片含噪，但不得事后删；
- variable choice 的 chance level 随 row 改变；paired comparison使用完全相同行，
  但 absolute accuracy 不应与统一 25% chance 比；
- CV-Bench 含 COCO/ADE20K，exact pixel audit 不排除 unknown pretraining 或
  near-duplicate；
- label NLL 不完全等于自由生成；
- frozen vision encoder 与低维 coordinates 可能形成共同上限。

这些限制约束 positive 的措辞，不改变预注册判定。

## 所需资源

- pilot：2 trainings，约 0.4 GPU-hour；
- positive 后上限：2 conditions × 3 roots = 6 trainings，约 1.2 GPU-hours；
- 单张空闲 A40 顺序运行；不并行扩大预算；
- RAM 充足；工作盘计划时约 24 GB available，artifacts 低于 2 GB；
- stable training 后每 10–20 分钟检查；
- final confirmation：不访问。
