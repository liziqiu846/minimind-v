# VISSUP-01 Round 1 — visually necessary rotation supervision paired pilot

**日期**：2026-08-07  
**阶段**：阶段三 mechanism-intervention training；不是阶段四正式算法主实验  
**类型**：从零训练的最小二条件因果干预 + 尚未评分的外部 prediction test  
**不可变性**：本文件提交后不得修改数据、task、prompt、ratio、模型、学习率、
训练步数、metric 或判定标准；需要修订只能创建新 round。

## 科学问题

在模型结构、原始 caption draws、rotated pixels、rotation label distribution、
optimizer steps 和 target token format 相同时，使少量 autoregressive instruction
必须依赖图像，而不是在文本中直接泄露答案，能否使 4,096-coordinate MiniMind-V
学到可迁移的视觉结构并改善未见 vision-centric task？

## 假设

假设 H：caption-only next-token training 允许当前低维 MiniMind-V 主要拟合语言统计，
没有充分迫使可训练坐标吸收视觉结构。若 H 在当前模型上成立，则：

1. `visual-necessary` rotation mix 相对等 pixels / labels / compute 的
   `label-revealed` control，应提高未作为 rotation instruction 训练样本的图像上的
   rotation forced-choice accuracy；
2. 该变化不应只停留在训练 task，而应方向性提高此前未对任何 intervention 模型
   评分的 CV-Bench-2D group-weighted forced-choice accuracy 与 gold margin。

若机制量不变，或外部 vision-centric 方向不为正，则 H 至少在当前 M2-current
MiniMind-V、固定 9.16% mixture share 和 rotation intervention 下不成立。

## VLM 特有性与文献边界

干预只改变多模态 user instruction 中的一个 hint token 是否携带图像 rotation label；
同一张 rotated image、同一 label、同一 assistant token、同一 autoregressive loss 和
同一可训练坐标用于两个条件。只有视觉语言模型才存在“文本是否足以完成本来可由
图像回答的同一 instruction”这一监督关系。

LITMAP-02 中的 ROSS、ASVR、JARVIS、LaVer 和 V-GIFT 只作为机制与实验设计来源。
`Words or Vision` 的 bounded-loss mixture-risk theorem 是相邻理论，不证明本
intervention。任何本轮差异只能称为：

> visually necessary rotation supervision 在当前低维 MiniMind-V 上的操作性训练
> 干预效应。

不得称为互信息、正式视觉风险、一般视觉信息定律、无偏估计量或已证明因果中介。

## 为什么已有 checkpoint 不足

现有 18 个 M2/M3 checkpoint 全部由相同 caption-only parquet 训练，没有
visually necessary instruction，也没有与之 matched 的 label-revealed control。
`COMP-01`、`XMC-01` 和 `VISCOND-01` 的生成 NLL、representation/no-bridge 与
correct-image vs no-pixel proxy 均已冻结失败；在旧 checkpoint 上再换 proxy 不能
区分训练监督机制。因此本轮符合阶段三最小 mechanism-intervention training 门。

## 冻结训练条件

### Base model 与可训练结构

- model group：`M2-current`；
- Stage 2 protocol：`experiments/stage2_protocol_v2.json`；
- coordinate dimensions：language `1,187`、projector `2,327`、vision `582`，
  total `4,096`；
- frozen language / projector / vision base parameters 不更新；
- 每个 run 从 exact-zero coordinates 开始；
- pilot mapping root：`43101`；
- pilot positive 后才可运行 `43102`、`43103`，不得选择 best root；
- train seed：`2026`，两个条件和三个 root 均相同；
- learning rate：`0.05`；
- optimizer：Stage 2 原 AdamW 设置；
- epochs：`3`；
- micro batch：`4`，gradient accumulation：`4`，effective batch：`16`；
- 每条件 rows：`11,008`，每 epoch `688` optimizer steps，总计 `2,064`；
- cosine schedule 仅把原公式的固定终点改为 `T=2,064`，两个条件完全相同；
- bfloat16 autocast、global gradient clipping `1`、单 GPU、deterministic
  permutation 与 frozen-parameter hash audit 保持 Stage 2 语义。

训练不是原 Stage 2 confirmation rerun，因此不得把结果称作 Stage 2 formal
confirmation。不得访问 validation 或 final confirmation split。

### Base caption draws

- path：
  `/home/lizhaohui/lzq/minimind-v-stage2-rerun-20260721/dataset/stage2_confirm_v2_seed2028/train.parquet`
- frozen SHA-256：
  `3c3d90c525f43200d35ebd5b4ac1719c8336d278aecbf7e929997c8401b1d5ce`
- rows：`10,000`；
- 两个条件保留全部 base rows 的 image bytes、conversation、token records 与顺序，
  不删 caption、不改 caption target。

### Rotation injection 的确定性构造

1. 规范化每个 base image 为 EXIF-transposed RGB，按规范化像素 SHA-256 去重；
2. 以字节串 `VISSUP01_IMAGE_ORDER_V1\0 || pixel_sha256` 的 SHA-256 升序排列；
3. 前 `1,008` 个独立图像用于 training injection；接下来的 `1,008` 个独立图像
   只用于 held-out rotation mechanism panel，不加入 rotation training rows；
4. 两个集合不得有 pixel-SHA overlap；若不足 `2,016` 个独立图像则
   `DATA_INELIGIBLE`；
5. 每个集合按冻结顺序的 `index mod 4` 分配 clockwise rotation
   `0/90/180/270`，恰好各 `252` 张；实现必须记录原图、rotated pixels 和编码 bytes
   SHA；
6. rotation 必须用无插值的 90-degree transpose；同一 injection 在两个训练条件
   中的 rotated image bytes 必须逐字节相同；
7. `1,008` injection rows 追加到相同 `10,000` base draws 后，再由固定
   `train_seed=2026+epoch_index` 的全数据 permutation 产生每 epoch 顺序。

augmentation 相对 base draws 为 `10.08%`，在 `11,008`-row mixture 中的占比为
`9.16%`。不得改为 3%、5%、10% mixture share，不得替换 rotation task 或筛掉
“难/模糊”图片。

### 两个唯一训练条件

rotation label 固定为 `0°→A, 90°→B, 180°→C, 270°→D`。每个注入样本保留原
system turn，user/assistant 固定为：

`visual-necessary`

```text
user:
<image>
The image was rotated clockwise from its natural orientation.
Hint code: X.
Select the applied rotation:
A. 0 degrees
B. 90 degrees
C. 180 degrees
D. 270 degrees
Answer with the option letter only.

assistant:
{gold_letter}
```

`label-revealed`

```text
user:
<image>
The image was rotated clockwise from its natural orientation.
Hint code: {gold_letter}.
Select the applied rotation:
A. 0 degrees
B. 90 degrees
C. 180 degrees
D. 270 degrees
Answer with the option letter only.

assistant:
{gold_letter}
```

`X` 与 `A/B/C/D` 必须各自被 frozen tokenizer 编为一个 user-span token，两个条件
的完整 VLM sequence length、assistant target IDs、target length和 image-token
位置必须逐样本相同。若 token gate 不成立，记为 `IMPLEMENTATION_INELIGIBLE`；
不得在看到训练或评分结果后换 prompt。

control 的训练 loss 预期更容易，不要求 loss 相等；它控制的是 pixels、labels、
token budget、steps 和 compute，而不是 example difficulty。该残余差异限制最终
解释。

## Held-out rotation mechanism panel

- 使用上述第二组 `1,008` 个 base-train 独立图像；它们仍作为原始 caption base rows
  出现在两条件训练中，但从未作为 rotation instruction row；
- 只在评分时施加预先分配的 rotation，并使用 `visual-necessary` 的 `Hint code: X`
  prompt；
- 对 `A/B/C/D` 各计算 gold letter + EOS 的 teacher-forced mean NLL；
- forced-choice prediction 为 NLL 最小的 letter，tie 按 `A<B<C<D`；
- gold margin 为三个错误 letter 平均 NLL 减 gold NLL；
- 主机制量是 1,008 个独立图像等权的 accuracy；辅助量为 mean gold margin；
- paired bootstrap 以图像为单位，10,000 次，seed `20260807`。

该 panel 检查“intervention 是否改变预期 mechanism”，不是独立外部泛化结论。由于
图片在 base caption 训练中出现过，不得称为 unseen-image generalization。

## 外部 prediction panel

唯一主外部 panel 固定为官方：

- repository：`nyu-visionx/CV-Bench`；
- revision：`bc284db50d036958861cb60cdd7b77612052ce0d`；
- license：Apache-2.0，非 gated；
- config：官方 `2D`；
- split：官方 `test`；
- 范围：下载后通过 gate 的完整 CV-Bench-2D，不使用 3D config。

本计划提交前只查过 repository metadata 和 revision；未下载 parquet、未查看样本，
也不存在任何 VISSUP model output。

评分前必须：

1. 固定 README、repository tree、parquet bytes 与 SHA-256；
2. 核查 schema、row count、图片可解码、question/options、gold answer 和官方 2D
   category inventory；
3. 每题必须确定性规范化为 `A/B/C/D` 四选一；不得丢弃模型答错或长度较长的题；
4. 计算与完整 10,000-row base train 的规范化 pixel-SHA overlap，删除 exact-overlap
   图像对应题目；若剩余独立图片组少于官方 2D 的 90%，记为
   `PANEL_INELIGIBLE`；
5. 若同一图片对应多题，先在 pixel-SHA group 内平均，再对独立图片组等权；
6. 不访问项目 validation/final confirmation set，也不按训练结果更换 benchmark。

prompt 为官方 question 与 options 后追加：

```text
Answer with the option letter only.
```

只提供 correct image，不计算 no-pixel 或 mismatch。主量为独立图片组等权的
forced-choice accuracy；共同方向审计量为 gold-vs-distractor mean NLL margin。官方
question-weighted accuracy 与官方 2D category 分层只作报告，不替代主量。

## 最小执行顺序

1. 提交本 immutable plan；
2. 下载并审计 CV-Bench-2D，不运行模型；
3. 实现两条件 dataset builder、training runner、rotation/CV-Bench scorer 和一次性
   analyzer；
4. 运行 tokenizer、pixel identity、balanced-label、disjoint-panel、permutation、
   synthetic metric 与 frozen-parameter unit tests；
5. 每条件最多 2 个样本做训练 smoke，只检查 forward/backward、loss finite、
   gradient 与 output receipt，不聚合科学结果；
6. 先后完整训练 root `43101` 的 `label-revealed` 与 `visual-necessary`；在两者都
   完成前不作科学评分或判定；
7. 两模型均完成后评分 rotation panel 和 CV-Bench-2D，并执行一次 pilot 判定；
8. 只有 `PILOT_POSITIVE` 才保持所有配置不变，补 root `43102`、`43103`；
9. total 3 roots 完成后执行一次最终 round 判定。

不得运行只有 intervention 没有 control 的模型；不得在 pilot 后换 ratio、task、
prompt、学习率、epoch、metric、subset 或新增 root。

## Pilot escalation 标准

root `43101` 必须同时满足：

1. 两个训练 run 的结构、初始 frozen hash、base rows、rotated-pixel hash、label
   order、optimizer steps 和 permutation receipt 全部匹配，且 loss/gradient finite；
2. held-out rotation：
   `accuracy_visual - accuracy_revealed >= 0.050`，paired bootstrap 95% CI 下界
   `> 0`，且 `accuracy_visual >= 0.300`；
3. CV-Bench-2D：
   `accuracy_visual - accuracy_revealed >= 0.010`，且
   `margin_visual - margin_revealed > 0`。

全部满足才记为 `PILOT_POSITIVE` 并补两个 root。accuracy 恰好等于阈值视为满足；
margin 必须严格为正。pilot positive 只是升级门，不是科学结论。

## 最终支持标准

total 3 paired roots 完成后，必须同时满足：

1. 三个 root 的 held-out rotation accuracy difference 全部 `>0`；
2. 至少 `2/3` roots 的 rotation difference `>=0.050` 且各自 paired bootstrap
   95% CI 下界 `>0`，三 root 等权 mean difference `>=0.050`；
3. 三个 root 的 CV-Bench-2D accuracy difference 全部 `>0`；
4. 至少 `2/3` roots 的 CV-Bench-2D accuracy difference `>=0.010`，三 root等权
   mean difference `>=0.010`；
5. 三 root 等权 mean CV-Bench gold-margin difference `>0`；
6. 官方两个 2D task family 的三 root 等权 mean accuracy difference 均 `>0`，
   排除全部方向由单一 family 独占。

全部满足时 `VISSUP-01` 标记为 `PROMISING` 并进入 `REVIEW_QUEUE`，不是
`CONCLUSION_CANDIDATE`。下一轮必须在不访问 final confirmation 的前提下提出一个
新的、尚未查看的 prediction 或更强 competing-explanation test；不得直接进入阶段四。

## 否定标准

panel 与实现有效时，以下任一情况即 `REJECT_IDEA`：

1. root `43101` 未满足全部 pilot escalation 标准，包括效应为正但小于预注册门；
2. held-out rotation difference `<=0`，说明 intervention 未改变预期机制；
3. CV-Bench-2D accuracy difference `<=0` 或 gold-margin difference `<=0`；
4. 补足三 root 后，任一最终支持项不满足；
5. 训练方向不稳定、effect 太小、category 方向只由一个 family 驱动。

effect 小、CI 跨零、seed 不支持、训练 loss 不漂亮或外部方向不符合预期均是科学
证据，不是 rescue 理由。不得通过加 seed、换 proxy、换 subset 或改变阈值维持
candidate。

## 无法判断标准

只限：

1. `DATA_INELIGIBLE`、`IMPLEMENTATION_INELIGIBLE` 或
   `PANEL_INELIGIBLE`；
2. base asset、CV-Bench revision、checkpoint、processor 或 tokenizer 无法通过
   hash / deterministic audit；
3. 明确 implementation bug、corrupted data、wrong checkpoint、preprocessing
   mismatch、metric error 或 job failure 经最多一次合法修复后仍无法完成；
4. 外部系统终止导致 paired condition 缺失，且当前资源下不能恢复。

`INCONCLUSIVE` 不自动获得更多训练、benchmark、prompt 或 round 预算。

## 可能混杂与结论限制

- `visual-necessary` 比 label-revealed control 更难；positive 可能来自
  hard-example pressure 或 rotation-specific inductive bias，不能直接推广为“一切
  visually necessary data 都改善泛化”；
- held-out rotation images 在 base caption rows 中出现过，只检验 task transfer；
- rotation 的自然 upright orientation 对部分对称/近景图片可能含噪；不得事后删题；
- CV-Bench-2D 仍可能与 base pretraining 有未知语义重叠，exact pixel audit 不能排除
  near-duplicate 或概念重叠；
- label-letter teacher forcing 不完全等于自由生成；
- frozen SigLIP2 vision encoder 和 4,096-coordinate adapter 可能形成共同上限；
- V-GIFT 是较新预印本，不能把其结果当成本项目 replication guarantee。

因此即使满足最终支持门，也只能得到一个具体、可重复的 mechanism candidate。

## 所需资源

2026-08-07 资源快照（`.claude_resources.json` SHA-256
`cf84a0a9132aea26d6fedd8f8b77c2bea337831763340ba7cbade46e1445a5fc`）：

- CPU：32 physical / 64 logical cores；
- RAM：约 442.7 GB available；
- GPU：8 张可见，检测时 A40 `1/5/7` 空闲；
- working filesystem：仅约 24.5 GB available。

资源策略固定为：

- 单张空闲 A40 顺序训练/评分，不多卡并发；
- paired pilot 最多 2 trainings，预计约 `0.4 GPU-hour`；
- pilot positive 后总上限 `2 conditions × 3 roots = 6 trainings`，预计约
  `1.2 GPU-hours`；
- training artifacts 只保存 coordinate state、必要 receipt 和紧凑 raw scores；
- dataset / CV-Bench cache 与全部结果预计低于 2 GB，不复制 base model；
- 长任务确认稳定后每 10–20 分钟低频检查；
- 不访问 final confirmation set。
