# COMP-01 Round 1 — 外部双图双描述组合绑定 prediction test

**日期**：2026-08-07  
**阶段**：阶段三  
**类型**：标准外部 benchmark protocol audit + frozen-checkpoint forced-choice
prediction test；不训练；不访问 final confirmation set  
**不可变性**：本文件提交后不修改判定标准；如需修订，创建新 round。

## 科学问题

在相同训练数据、预算和 seed 的 MiniMind-V M2/M3 模型中，较短的共享坐标模型
若表现更差，是否同时表现出更弱的跨模态组合绑定，而不是只表现为 checkpoint
描述长度变化？

## 假设

假设 H：现有 development-only SugarCrepe++ 总语义风险较低的模型，在一个此前
未对这些模型评分、文本边际得到成对抵消的标准外部组合 benchmark 上，应有更高的
正确关系绑定 margin。

对每个 `(budget, seed)` M2/M3 pair，记已有总语义风险差为

\[
\Delta R = R_{\mathrm{M3}}-R_{\mathrm{M2}},
\]

新外部组合绑定 margin 差为

\[
\Delta G = G_{\mathrm{M3}}-G_{\mathrm{M2}}.
\]

预测是非零差异满足

\[
\operatorname{sign}(\Delta G)=-\operatorname{sign}(\Delta R).
\]

若合法外部 panel 上该方向不能跨预算/seed 稳定出现，则“组合绑定解释
码长—真实性能脱钩”至少在当前模型家族和测试总体上不成立。

## Why now?

1. `XMC-01_round1` 已排除已审计 6 对 P/S 的纯数据共现差异，下一步必须检查模型
   保留了什么跨模态关系；
2. Winoground、ARO、SugarCrepe 的 primary literature 指出 bag-of-words /
   order-insensitive shortcut 是现有 VLM 的真实失败机制；
3. 已有 SugarCrepe++ 风险只作为预先存在的 development 性能排序，不再从中选择
   新 proxy；新结果来自此前未对 18 个模型查看的外部 panel；
4. 若 H 成立，可自然导出 composition-aware hard negatives；若不成立，应立即降低
   COMP-01 优先级而不是继续制造组合 proxy。

## VLM 特有性

测试对象是两张只改变对象关系的图像与两条对应描述之间的交叉绑定。对象和词的
边际信息在 group 内固定，必须利用图像—文本关系才能同时完成两项匹配；这不是
单模态 LLM 容量或普通 checkpoint 复杂度的重命名。

本轮 \(G\) 只称为：

> 外部成对反事实上的操作性组合绑定 margin。

不得称为互信息、正式视觉风险、无偏估计量或已证明的泛化界。

## Panel 选择与访问门

1. registry 原先预声明的首选是 Hugging Face 冻结 revision
   `facebook/winoground@b400e173549071916ad1b3d449293bc8d8b4b763`。在本计划
   创建前只做了 access check，结果为 `blocked_by_access`；没有查看任何模型输出。
2. round1 固定 fallback 为 Kamath et al., *What’s “up” with vision-language
   models?*（EMNLP 2023）的官方 controlled panel。
3. scoring 前必须核查 primary paper 正文和官方 repository，并同时满足：
   - 官方数据与 annotation 可公开、确定性获取；
   - evaluation unit 能形成两图、两条语法正常描述的关系反转 group；
   - group 内对象身份/词边际固定，正确关系随图像改变；
   - 使用完整 eligible controlled panel，不按模型结果选择 subset；
   - 图片不属于项目 final confirmation set，且本轮不读取 final confirmation；
   - 18 个 checkpoint 在本次 benchmark access 前已经冻结。
4. 若任一项不满足，结论固定为 `PANEL_INELIGIBLE`，不评分、不临时改用 ARO 或
   SugarCrepe++，而是创建新的 round 做 targeted literature search。

## 冻结模型与既有比较量

- 模型：M2/M3 × `{low,current,high}` × seeds `{43101,43102,43103}`，共 18 个；
- pair：相同 budget、相同 seed 的 M2/M3，共 9 对；
- checkpoint 状态：与现有 development risk 一致的 MMS2 decoded frozen model；
- 既有比较量：
  `experiments/phase3_risk_v1/results/budget_trend_18_models/model_summary.csv`
  中的 `empirical_total_semantic_risk`；
- 该风险是 `development-only`、`certified=false` 的操作性性能量，不是 final
  confirmation 结果。

不得根据新 binding 结果更换 model subset、既有风险、checkpoint 状态或预算。

## 操作性指标

对每个 eligible group 的图像 \(I_0,I_1\) 与正确描述 \(C_0,C_1\)，用冻结
`Describe the image in one sentence.` 模板计算 caption+EOS 的 teacher-forced
mean token NLL（bits/token），记为 \(L(I,C)\)。

group binding margin 固定为：

\[
g=\frac{
L(I_0,C_1)+L(I_1,C_0)-L(I_0,C_0)-L(I_1,C_1)
}{2}.
\]

模型主量 \(G\) 是所有独立 eligible group 的等权平均 \(g\)。\(G>0\) 表示正确关系
组合总体比交叉错配具有更低 NLL。该交叉差分代数抵消只依赖 caption 的加性语言
偏好和只依赖 image 的加性难度，但不证明消除了所有非加性交互混杂。

辅助审计量预先固定为：

- group accuracy：两张图都给正确 caption 更低 NLL 的 group 比例；
- image accuracy：单图正确 caption NLL 更低的比例；
- 每个 M2/M3 pair 的 group bootstrap 95% percentile CI；
- 完整 panel 的 relation/category 分层结果，仅用于检查方向是否由单一类别支配，
  不改变主判定。

bootstrap 固定为 10,000 次、seed `20260807`，重采样单位为官方独立 group。

## 最小实验

1. 核查 primary paper、官方 repository、license、数据 schema 和 panel gate；
2. 冻结下载 URL / revision、文件 SHA-256、eligible group 数和拒绝原因；
3. 写最小 scorer，复用已有 tokenizer、caption template、MMS2 loader 和 model
   construction；先用 synthetic group 单元测试 margin 方向与 caption/image 交换；
4. 先对 1 个模型做不读取聚合结论的运行 smoke，验证有限 NLL、完整四格评分、
   deterministic rerun 和 GPU 内存；
5. gate 与 smoke 通过后，顺序评分 18 个模型；保存逐 group 原始四格 NLL、模型
   汇总、pair 差异、bootstrap 与运行 receipt；
6. 只在全部预声明模型完成后执行一次主判定。

## 支持标准

必须同时满足：

1. 9 个 M2/M3 pair 中至少 7 个满足
   `sign(ΔG) = -sign(ΔR)`；
2. 其中至少 5 个 pair 的 bootstrap 95% CI 不跨 0 且方向与预测一致；
3. 三个 budget 各自至少 2/3 seeds 方向一致；
4. 在所有 `ΔR>0`（共享模型更短但语义风险更高）的 pair 中至少 75% 满足
   `ΔG<0`；
5. 主方向不能由单一 relation/category 独占，至少两个 relation family 的平均方向
   与总体一致。

满足时，COMP-01 进入 `PROMISING`，但不是正式理论规律；下一轮必须做理论 bridge
或尚未查看条件上的 prediction。

## 否定标准

panel 与运行有效时，满足任一项即 `REJECT_IDEA`：

1. pair sign concordance 不超过 5/9；
2. 任一 budget 的 3 seeds 全部与预测相反；
3. 所有模型的 \(G\) 接近 0 / group accuracy 接近随机，且没有预注册方向；
4. 方向完全由一个 relation/category 驱动，其余 family 为零或相反；
5. `ΔR>0` 的 decoupled pairs 中预测方向比例低于 50%。

效应小、相关性不佳、seed 不一致或结果不符合预期均不是 rescue 理由。

## 无法判断标准

只限以下情况：

1. `PANEL_INELIGIBLE` 或官方数据不可确定性获取；
2. eligible 独立 group 少于 primary paper controlled panel 的 90%；
3. checkpoint、base asset、preprocessing 或 metric implementation 无法通过 hash /
   deterministic audit；
4. 运行因明确工程故障未完成，且一次合法修复后仍失败。

无法判断不自动增加本 candidate 的 scoring/training 预算；创建新 round 或转向
NEXT candidate。

## 可能混杂

- 小型生成式 LVLM 的 caption NLL 未必等价于 CLIP retrieval score；
- teacher-forced prompt 与 benchmark 原始 discriminative protocol 不同；
- frozen SigLIP2 可能在大规模预训练中见过相似图片；
- \(G\) 可抵消加性文本偏好，但不能排除所有 caption 长度和非加性交互；
- 既有 development risk 是 post-hoc operational metric，不能形成正式认证；
- 不同预算改变模型行为的机制可能不是组合绑定。

## 所需资源

- 训练：0；
- GPU：checkpoint-only sequential scoring，优先空闲 A40 GPU 1 或 5；
- CPU/RAM：32 physical cores、约 437 GB available；数据可内存处理；
- 磁盘：计划时约 49 GB available，禁止复制 base checkpoint 或保存重复视觉
  features，只保存 compact NLL/result artifacts；
- 数据：官方 controlled panel；不访问 final confirmation set；
- 预计 scoring 输出远小于 1 GB。
