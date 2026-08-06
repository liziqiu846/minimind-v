# Nightly Research Report

## 1. 今晚覆盖范围

完成数据、表示、训练及相邻理论四组系统 scoping map：OpenAlex broad 360 条、
title verification 160 条、arXiv 258 条，正文核查 18 篇关键论文；生成并登记 5 个
candidate。没有训练、没有访问 final confirmation set，GPU 用时 0。

## 2. Candidate summary

| Idea | Status | 最关键理由 |
|---|---|---|
| `XMC-01` | `PROMISING` / `REVIEW_QUEUE` | 有直接 MMCL 正式理论与数据算法证据；6/9 P/S 实际数据/permutation 相同，纯数据版本在这些 pair 内不足 |
| `COMP-01` | `NEW` | 同词反事实可最低成本证伪，hard-negative 有算法出口；缺生成式 LVLM 理论桥 |
| `VISCOND-01` | `NEW` | 最贴近生成式 LVLM，但当前主要是经验机制，不能退化为无桥视觉 proxy |
| `OBJ-01` | `NEW` / `REVIEW_QUEUE` | joint objective 有算法证据；因果判别需要今晚禁止的新训练 |
| `COVER-01` | `NEW` / `REVIEW_QUEUE` | 受控域/组合覆盖证据明确；现有同数据 checkpoint 不能验证 |

## 3. 被淘汰的 idea

- 单独使用 raw modality-gap distance：方向不单调、任务依赖强。
- 把通用 compression/CMI/stability 换名为 VLM 新机制：VLM 特有性不足。
- 没有理论桥梁、靠历史 P/S 反复试相关性的视觉 proxy：违反预注册与独立验证要求。

## 4. 最有希望的 1–2 个 idea

### `XMC-01`

- **VLM-specific novelty**：图文非对称共现图、配对语义一致性及模型对其谱方向的保持。
- **最关键证据**：Zhang et al. 2023 的 MMCL 正式桥；DataComp/DFN/BLIP 的算法证据；
  本轮 6/9 P/S data/permutation equality。
- **当前最大缺口**：定理止于 spectral contrastive dual encoder + linear probe；
  3 个 current-budget manifest 缺失，模型保持版本尚未验证。

### `COMP-01`

- **VLM-specific novelty**：对象/词边际信息相同但图文关系、属性绑定或顺序不同。
- **最关键证据**：Winoground、ARO、SugarCrepe；composition-aware hard negatives。
- **当前最大缺口**：benchmark 文本偏差与 CLIP→生成式 LVLM 外推。

## 5. Prediction tests

- 已预注册后执行：`XMC-01_round1` 的 manifest prediction audit；6/9 支持数据图一致，
  3/9 缺实际回执，整体按原标准为 `DATA_GRAPH_IDENTITY_NOT_AUDITABLE`。
- 尚无真正的“未查看模型/条件性能”prediction test。
- 待验证 prediction：冻结 P/S checkpoint 在 text-bias-controlled、same-word
  counterfactual pairs 上，较差模型应有更小的正确-vs-反事实 forced-choice NLL margin。

## 6. 当前绝对不能推出什么

- 不能推出共现谱已经解释 P/S 性能排序。
- 不能把 CLIP 分类/linear-probe 定理直接用于 MiniMind-V 生成风险。
- 不能把 correct-vs-mismatch 差称为互信息或正式视觉风险。
- 不能宣称任何 candidate 已达到 `CONCLUSION_CANDIDATE`。
- 不能进入阶段四或启动正式训练算法主实验。

## 7. REVIEW_QUEUE

- `XMC-01`：恢复/核查 3 个 current-budget training manifest，并审查生成式 LVLM
  理论桥。
- `OBJ-01` / `COVER-01`：需要新训练才能因果验证，保持冻结。

## 8. 唯一推荐下一步

创建 `COMP-01_round1` immutable plan：先核查冻结 checkpoint 可用性与标准外部
counterfactual panel 的独立性，再做同词、关系交换 forced-choice NLL
checkpoint-only prediction test；不训练。

## 9. Git / artifact 状态

- commits：
  - `ba55681` literature-map immutable plan；
  - `c68b2d0` literature map、raw search records、figure、candidate registry；
  - `1624428` XMC-01 immutable plan；
  - `1c3678c` XMC-01 audit result、queue、state。
- uncommitted files：本报告生成前为 0；本报告在 finalization commit 中提交。
- push status：既有 `origin/stage3-image-group-dependence-sgd-v1` 自动同步成功，
  已确认推送至 `1c3678c`；本报告在 finalization 后再次同步。
- hard stop：`false`。

## 10. 持续日志：COMP-01 panel gate

- Winoground 冻结 revision 仅做 access check，结果 `blocked_by_access`，没有运行模型；
  按 immutable plan 转入固定 fallback：What’sUp controlled panel。
- 已核查 Kamath et al.（EMNLP 2023）正文、官方仓库 commit
  `7c1f2550eace32e7b8c77de5a792347c402960d1`、MIT license、annotation/archive
  SHA；完整 panel 为 820 张 annotation 引用图片、205 个四图对象组、410 个对立关系
  pair。archive 中 9 张未引用图片被明确忽略。
- 项目 v2 历史 53,071 张与 adapter train 10,000 draws 均无 exact SHA overlap。
  第一遍保守 pHash screen 发现 5 个半径命中并阻止评分；在任何模型 inference 前，
  仅检查来源为 `train` 的对应项，确认分别是吉他线描、红头巾人物、卡通水果篮和
  帆板，与外部 dog/table、cap/cup、cup/remote、plate/cup 图像均为不同场景。
  256-bit pHash 距离 98–116、dHash 距离 21–37，故记录为 64-bit pHash 粗布局
  false positive。
- 未读取 validation/final confirmation，未运行 COMP-01 模型输出；panel 已通过
  collision adjudication，下一状态为单模型 deterministic smoke。
- `M2-current-seed-43101` 在 manifest 首个 pair 上完成两次 deterministic smoke：
  四格 NLL 全部有限、两次 raw-row SHA 完全相同、未保存 raw 值、未作科学聚合；
  peak CUDA allocation 约 0.80 GB。下一步为单 GPU 顺序评分冻结的 18 个模型。

## 11. 持续日志：COMP-01 round1 判定

- 18/18 冻结模型、410/410 pair 全部评分完成；单卡 wall time 815.7 秒，模型运行
  receipt 合计约 0.20 GPU-hour。未训练、未访问 final confirmation。
- 一次性预注册判定为 `REJECT_IDEA`：sign concordance `5/9`，预测方向 CI 不跨 0
  仅 `1/9`；low/current/high budget 分别 `1/3,3/3,1/3`，不能事后只保留 current。
- `ΔR>0` 的 4 pair 中 `3/4` 有 `ΔG<0`，且三个 relation family 的
  prediction-oriented 平均效应为正；但联合支持标准未满足，且已触发 `≤5/9`
  否定项。
- 所有模型 image accuracy 约 0.50、group accuracy 仅 0.2%–2.9%；95.4%–99.8%
  pair 的两张图偏好同一 caption，说明当前生成式 NLL bridge 强烈受语言偏好支配。
- COMP-01 已冻结为 `REJECTED` 并进入 `REVIEW_QUEUE`；不做 rescue，ACTIVE 转为
  `XMC-01` model-retention bridge。

## 12. 持续日志：XMC-01 round2 理论 gate

- arXiv/OpenAlex 定向检索完成；Parallel CLI 因服务器未认证不可用，按既定
  `paper-lookup` fallback 保存 7 份原始查询响应。
- 下载并全文/appendix 核查 13 篇 primary sources，PDF 版本与 SHA-256 已记录；
  没有运行 checkpoint、没有训练、没有访问 final confirmation。
- `2505.24134` 的 generative 解释属于 dual-encoder induced conditional，解析定理
  限 linear Gaussian；`2605.02116` 的 calibration 只控制 contrastive retrieval
  AUC；`2607.08194` 明确限定为机制解释而非定量 bound。
- 其余理论止于 MMCL linear probe、identifiability、CLIP zero-shot prediction、
  pair alignment、给定 cost 的几何保持或经验 subspace/Jacobian diagnostics。
- 没有理论同时固定 autoregressive LVLM representation、唯一无 sweep statistic
  与 held-out semantic-risk direction；继续只能事后选择 proxy，触发预注册否定。
- `XMC-01` 已标记 `REJECTED` 并进入 `REVIEW_QUEUE`；ACTIVE 转为 `VISCOND-01`。

## 13. 持续日志：VISCOND-01 round1 外部 prediction test

- 官方 MMStar revision、41.8 MB parquet SHA、schema、图片解码、A/B/C/D inventory
  与答案 token gate 均通过。排除 3 个超过冻结 450-token 上限的题目和 1 个官方缺
  D 选项的题目后，完整 eligible panel 为 1,496 题、1,426 个独立像素组。
- 18/18 冻结 MMS2 checkpoint 全部评分；正确图像与 no-pixel 共用同一 VLM、
  question、option target 和 image-pad token 位置。逐题 raw values 保留在 runtime，
  analysis receipt 绑定 checkpoint、panel、scoring commit、18 个 receipt 和 raw SHA。
- 一次性预注册聚合为 `REJECT_IDEA`：pooled \(V=-0.221182\) bits/token，图片组
  bootstrap 95% CI `[-0.306740,-0.134830]`，仅 `2/18` 模型为正，触发构念否定。
- 9 对风险排序有 `6/9` 方向一致、`4/9` 预测方向 CI 不跨 0；三个 budget 各
  `2/3`，`ΔR>0` 的 4 对中 `3/4` 为预测方向，6 个类别有 5 个平均方向为正。这些
  局部条件不能覆盖已触发的 pooled/positive-model 否定项。
- correct-image accuracy 为 `0.2099–0.2934`，no-pixel 为 `0.2025–0.3135`；
  accuracy gain 为 `-0.0869–0.0261`。结果更像当前 answer-letter 构造上的视觉输入
  分布/任务适配问题，而不是稳定正向视觉增量；该解释尚非新结论，也不允许通过换
  prompt 或 proxy rescue。
- 18 个 receipt 合计 1,929.725 秒，即 0.536 GPU-hour；本 cycle 累计约 0.75
  GPU-hour。未训练，未访问 final confirmation set。
- `VISCOND-01` 已冻结为 `REJECTED` 并进入 `REVIEW_QUEUE`。原 `OBJ-01` 的
  VISCOND-positive 启动门未满足，禁止直接训练；ACTIVE 转为 `LITMAP-02`
  primary-source gate，目标是生成真正不同的训练时跨模态监督/优化候选。
