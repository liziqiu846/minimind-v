# VISCOND-01 Round 1 — MMStar correct-image vs no-pixel prediction test

**日期**：2026-08-07  
**阶段**：阶段三  
**类型**：历史 artifact 构念效度审计后的外部 benchmark frozen-checkpoint
prediction test；不训练；不访问 final confirmation set  
**不可变性**：本文件提交后不修改判定标准；如需修订，必须创建新 round。

## 科学问题

在相同训练数据、坐标预算和 seed 的 MiniMind-V M2/M3 模型中，已有
development-only 总语义风险更高的模型，是否系统性地从任务相关正确图像获得更少
的条件判别增量，而更多依赖同一模型的 no-pixel language prior？

## 历史 artifact gate

本计划创建前仅核查已有 artifact 和外部资源可达性，结论固定如下：

1. Phase 3 v5 已在 SugarCrepe++ 上比较 correct-image 与 no-pixel caption Brier
   margin；current-budget 三个 M2/M3 pair 的点估计方向均为 M2 视觉增量更大。
   但是该指标明确是在查看 v4 Formal 后形成的事后分析，且这些输出现在已经被
   查看，因此只能作为假设来源，不能作为本轮 prediction evidence。
2. Phase 3 v6 / risk-v1 已在同一 SugarCrepe++ panel 上使用五个固定随机 donor；
   9 个跨预算 M2/M3 pair 中，随机错配视觉增量与已有总语义风险排序仅有 `5/9`
   符号一致。该实验的 donor 不保证题目视觉必要，项目原记录也明确将
   `coupled_mismatch_donors` 和 `post_hoc_metric_design` 标为正式认证失效原因。
   它不能支持 VISCOND，也不能被删除或只保留 current budget。
3. 因而，本轮不是在旧输出上选择一个表现更好的 proxy，而是只允许一次具有更强
   构念效度的新鲜检验：使用在模型评分前已由 benchmark 作者按视觉必要性和泄漏
   风险筛选的完整 MMStar panel，并固定同一 VLM、同一 token 模板下的
   correct-image vs no-pixel 差分。
4. 若本轮未达到预注册支持门，禁止改用错配 donor、模糊图、不同 prompt、答案
   文本 NLL、subset、额外 benchmark 或新增 seed 来 rescue `VISCOND-01`。

## 假设

假设 H：若“较差模型更少利用任务相关图像条件”是码长—性能脱钩的主要机制，则在
此前未对这 18 个 checkpoint 评分的 MMStar 完整视觉必要 panel 上，模型的
correct-image 相对 no-pixel 的正确答案判别增量 \(V\) 应随已有总语义风险变差而
下降。

对每个相同 `(budget, seed)` 的 M2/M3 pair，冻结已有风险差

\[
\Delta R = R_{\mathrm{M3}}-R_{\mathrm{M2}},
\]

以及本轮视觉条件增量差

\[
\Delta V = V_{\mathrm{M3}}-V_{\mathrm{M2}}.
\]

对非零差异的方向预测固定为

\[
\operatorname{sign}(\Delta V)=-\operatorname{sign}(\Delta R).
\]

若完整外部视觉必要 panel 上该方向不能跨预算和 seed 稳定出现，则 H 至少在当前
冻结模型家族中不成立。

## VLM 特有性与术语边界

本轮只改变是否向同一个 autoregressive VLM 提供题目对应的真实图像像素；问题、
四个选项、prompt、token 序列、checkpoint 和 decoder 均保持不变。该差分针对图像
条件对生成式答案判别的增量影响，是单模态 LLM 不具有的干预。

本轮 \(V\) 只能称为：

> MMStar 视觉必要样本上的 correct-image 相对 no-pixel 操作性判别增量。

不得称为互信息、正式视觉风险、因果中介量、无偏估计量或泛化界。no-pixel
差分抵消同一模型、同一问题和答案标签的加性语言偏好，但不证明消除了所有
图像-token 缺失造成的非加性交互。

## 外部 panel 与访问门

数据固定为 Hugging Face 官方镜像：

- repository：`Lin-Chen/MMStar`
- revision：`bc98d668301da7b14f648724866e57302778ab27`
- config / split：`val / val`
- file：`mmstar.parquet`
- expected bytes：`41,798,712`
- expected LFS SHA-256：
  `29afd74b0134cfab083a8909b5358577ab18fd41c1e612031577cfb3635531c2`
- expected rows：`1,500`
- expected core capabilities：6，每类 250 条

提交本计划前只读取了官方 README、repository tree 和 revision，没有下载 parquet、
查看样本内容或运行任何 checkpoint。

执行时必须先通过以下 gate：

1. schema 精确包含 `index, question, image, answer, category, l2_category,
   meta_info`；
2. `index` 唯一，行数为 1,500，6 个 core category 各 250；
3. 每题恰有四个可解析选项标签 `A/B/C/D`，gold answer 恰为其中一个；
4. 所有图片可解码，规范化 RGB 像素 SHA-256 可确定性重算；
5. 使用完整 eligible panel，不按模型输出、类别难度、问题类型或历史结果筛 subset；
6. 数据不属于项目 final confirmation set，本轮不读取 final confirmation；
7. 18 个 checkpoint 在数据评分前均已冻结。

若 schema 与官方当前发布格式不相容、有效样本少于 1,350（90%）或任一资源无法
确定性核查，则记为 `PANEL_INELIGIBLE`，不临时改用 POPE、MMBench 或旧
SugarCrepe++。

若同一规范化图片对应多题，主统计先在像素 SHA-256 内等权平均，再对独立图片组
等权平均，避免重复图片虚增样本量。

## 冻结模型与既有比较量

- 模型：M2/M3 × `{low,current,high}` × seeds
  `{43101,43102,43103}`，共 18 个；
- pair：相同 budget、相同 seed 的 M2/M3，共 9 对；
- checkpoint：与 risk-v1 development 指标对应的冻结 MMS2 decoded models；
- 既有 \(R\)：
  `experiments/phase3_risk_v1/results/budget_trend_18_models/model_summary.csv`
  的 `empirical_total_semantic_risk`；
- \(R\) 是 `development-only`、`certified=false` 的操作性真实性能量，不是
  final confirmation 结果。

不得根据 MMStar 输出更换模型、risk 字段、预算、seed 或 checkpoint。

## 唯一操作性指标

固定 prompt 为：

```text
<image>
{official_question_with_options}
Answer with the option letter only.
```

对每个答案标签 \(a\in\{A,B,C,D\}\)，计算标签加 assistant EOS 的
teacher-forced mean token NLL（bits/token），记为 \(L_h(c,a)\)。correct-image
条件使用官方图像；no-pixel 条件使用完全相同的 VLM token 序列和 image-pad
位置，但令 `pixel_values=None`。不得改用 M0 checkpoint 代表同一模型的语言先验。

若 gold label 为 \(y\)，条件 \(c\) 下的正确答案判别 margin 为

\[
m_h(c)=\frac{1}{3}\sum_{a\ne y}L_h(c,a)-L_h(c,y).
\]

逐题视觉条件增量为

\[
v_h=m_h(\mathrm{correct})-m_h(\mathrm{no\mbox{-}pixel}).
\]

模型主量 \(V_h\) 是先按规范化图片 SHA-256 聚合、再对独立图片组等权平均的
\(v_h\)。\(V_h>0\) 表示真实图像总体提高了 gold 相对 distractor 的判别。

以下仅为预声明审计量，不替代主量：

- correct-image 与 no-pixel forced-choice accuracy，tie 按 `A<B<C<D`；
- 每个模型 \(V_h\) 和每个 pair \(\Delta V\) 的图片组 bootstrap 95% percentile
  CI；
- 6 个 core category 的方向；
- image-pad、token mask、有限 NLL、deterministic rerun 和 M0-like
  no-pixel invariance 单元测试。

bootstrap 固定为 10,000 次、seed `20260807`，共享重采样索引用于同一 pair 的
M2/M3 差异。

## 最小实验

1. 下载并 hash 官方 parquet，完成 schema、category、option、图片与重复组审计；
2. 创建 panel manifest，只保存必要文本、gold label、图片组 hash 和来源字段；
3. 复用现有 MMS2 loader、MiniMind-V image preprocessing 和 Phase 3 causal
   teacher-forced scorer，实现唯一的 correct/no-pixel label margin；
4. 用 synthetic logits 检查 margin 符号、答案置换、correct=no-pixel 时
   \(v=0\)，再用一个模型和不超过 2 个样本做 smoke；smoke 不聚合、不作科学判断；
5. gate 和 smoke 通过后顺序评分全部 18 个模型，保存逐题四标签双条件 NLL、
   model / pair / category summary、bootstrap 和 run receipt；
6. 只有 18/18 完成后执行一次预注册判定。

本轮 checkpoint-only test 足以区分 H，不启动训练。

## 支持标准

必须同时满足：

1. pooled 18-model mean \(V\) 的图片组 bootstrap 95% CI 下界大于 0，且至少
   12/18 模型的 \(V\) 点估计为正，证明 panel 对当前家族不是纯语言任务；
2. 9 个 M2/M3 pair 中至少 7 个满足
   `sign(ΔV) = -sign(ΔR)`；
3. 至少 5 个 pair 的 95% CI 不跨 0 且方向与预测一致；
4. low、current、high 三个 budget 各至少 2/3 seeds 方向一致；
5. 所有 `ΔR>0` 的 decoupled pair 中至少 75% 满足 `ΔV<0`；
6. 6 个 core category 中至少 4 个的 9-pair prediction-oriented 平均差为正。

全部满足时，`VISCOND-01` 标记为 `PROMISING`，不是理论结论；下一轮必须产生一个
尚未查看的 mechanism intervention prediction，而不能在 MMStar 上继续调 proxy。

## 否定标准

panel 与运行有效时，满足任一项即 `REJECT_IDEA`：

1. pair sign concordance 不超过 5/9；
2. 任一 budget 的 3 个 seeds 全部与预测相反；
3. pooled 18-model mean \(V\) 不为正，或少于 9/18 模型的 \(V\) 点估计为正；
4. `ΔR>0` pair 中预测方向比例低于 50%；
5. 方向只出现在至多 2/6 core categories，其余类别为零或相反。

效应小、CI 跨零、seed 不一致或结果不符合预期都不是工程 rescue 理由。

## 无法判断标准

只限：

1. `PANEL_INELIGIBLE`；
2. 有效独立图片组少于 1,350；
3. checkpoint、processor、prompt、token mask、图片或 deterministic audit 无法
   通过；
4. 明确 implementation / corrupted data / wrong checkpoint / preprocessing /
   metric error 或 job failure 经一次合法修复后仍无法完成；
5. sign concordance 恰为 6/9，未触发其他否定项但也未满足全部支持门。

`INCONCLUSIVE` 不自动获得新的 benchmark、prompt、proxy、seed 或训练预算。

## 可能混杂

- MiniMind-V 主要按 captioning 训练，单字母 answer likelihood 未必等于自由生成
  VQA 能力；
- no-pixel 保留 image-pad token 而删除像素，可能产生训练外输入；
- mean token NLL 与官方 exact-match decoding 不完全相同；
- MMStar 虽经作者筛选，仍可能存在 residual language cues 或 base pretraining
  overlap；
- 同一冻结 SigLIP2 视觉编码器可能成为所有 adapter 的共同上限；
- \(R\) 是事后 development operational risk，不能形成正式认证；
- 模型的图像利用差异可能是性能结果而非单一因果中介。

这些限制约束结论措辞，但不得在看到结果后通过换 prompt、答案文本、图像干预或
subset 修正。

## 所需资源

- 训练：0；
- GPU：18 个冻结 checkpoint 顺序评分，优先当前空闲 A40 GPU 1、5 或 7；
- 数据下载：约 42 MB；
- 输出：紧凑 parquet/JSONL/CSV/Markdown，预计远小于 1 GB；
- 磁盘：计划时约 49 GB 可用，不复制 base model，不持久化重复视觉 features；
- final confirmation：不访问。
