# 上海交通大学实习——当前研究状态

**版本：v1**  
**日期：2026-08-06**  
**定位：项目的当前工作状态入口。任何新对话、Codex 任务或阶段三研究决策开始前，先读本文。**

---

## 0. 文档职责与优先级

本项目以后固定使用以下四类文档，避免依赖聊天上下文：

1. `docs/project/CURRENT_STATE.md`：**当前状态的最高优先级入口**，回答“我们现在做到哪、下一步是什么”。
2. `docs/theory/VLM泛化理论基线.md`：**理论单一事实来源**，回答“哪些理论已成立、哪些待证明、哪些路线已否定”。
3. `docs/project/DECISION_LOG.md`：关键研究决策及原因，不删除历史。
4. `docs/project/EXPERIMENT_REGISTRY.md`：正式实验、审计、commit、状态和结论索引。

若历史聊天内容与上述文档冲突，以仓库中最新文档为准。

> 注意：理论基线 v1 中的“当前最近一步”反映其冻结时状态；后续最新操作状态以本文为准，不需要为了每次实验频繁改写理论基线。

---

## 1. 项目总目标

项目主线不变：

\[
\boxed{
\text{LLM 泛化理论拓展到 VLM}
\rightarrow
\text{发现真正影响 VLM 泛化的规律}
\rightarrow
\text{MiniMind-V 验证}
\rightarrow
\text{理论导出训练算法}
\rightarrow
\text{提升真实任务泛化}
}
\]

MiniMind-V 只是低成本验证平台，不能反过来定义理论。

当前仍属于**阶段三**。只有当阶段三得到的理论量或认证规律正式用于训练目标、预算分配或模型选择时，才进入阶段四。

---

## 2. 当前已确认的核心经验事实

阶段三 P/S 实验已经稳定暴露出一个核心问题：

> 更短的 checkpoint 描述长度、更小的压缩复杂度惩罚，不保证更好的真实视觉任务泛化。

即存在：

\[
\boxed{\text{编码复杂度下降} \not\Rightarrow \text{真实 VLM 泛化改善}}
\]

因此，单纯继续优化 checkpoint 码长不足以解释或改善当前问题。

---

## 3. 当前理论主线

当前第二层主线是：

\[
\boxed{
\text{新图像泛化}
\rightarrow
\text{图像组级训练数据依赖}
\rightarrow
\text{CMI / 信息论泛化工具}
\rightarrow
\text{训练轨迹上的可计算量}
\rightarrow
\text{训练算法}
}
\]

关键对象优先以独立图像组作为外层统计单位：

\[
G_i=(I_i,\mathcal Y_i).
\]

当前仍需完成的核心桥梁是：

\[
\text{抽象图像组 CMI}
\longrightarrow
\text{合法、稳定、可计算的训练过程代理量}.
\]

CMI 本身没有被当前实验否定。

---

## 4. 第一版图像组敏感性实验

### 4.1 实验身份

- 分支：`stage3-image-group-dependence-sgd-v1`
- 协议实现 commit：`ea1b58d6d82e12d311975fb1facbb624d611f8de`
- MMS2 编码修复 commit：`118a5416bc914d9d4d178e871f63026d97a9291c`
- 12 模型正式结果 commit：`584920421f0e718a9c186d353d704a8ffac003f7`
- 结构：P / S
- budget：2048 / 8192
- model seed：43101 / 43102 / 43103
- 优化器：plain SGD，无 momentum、无 weight decay、无梯度裁剪

实验使用的第一版诊断量为：

\[
D_I=\sum_t\eta_t^2\|g_t-g_t^{ghost}\|_2^2.
\]

其中 ghost 替换完整 `(image, canonical conversation)` 图像组。

### 4.2 已确认的实现事实

以下实现审计通过：

- 训练、ghost、development exact-image 互不重叠；
- 训练图像组 exact image 唯一；
- 同一诊断中 true / ghost 在同一参数状态上计算；
- ghost 替换完整图像组；
- 诊断恢复 gradient、buffer、RNG；
- 诊断开启 / 关闭的正式 SGD 轨迹一致；
- **未发现 implementation bug。**

因此问题不在“公式被代码实现错”。

---

## 5. 第一版 D_I 的正式状态：INVALID_FOR_INFERENCE

原 12 模型预注册结果中，标准 1 通过、标准 2/3/4 失败。但后续独立 infra 审计发现**结构性测量混杂**。

### 5.1 关键混杂 1：model seed 与 probe seed 没有分离

`fixed_index()` 使用：

```text
protocol_id | config_seed | optimizer_step | role
```

因此不同 model seed 同时改变：

- 模型随机映射；
- 被诊断的 train sample；
- ghost sample。

同 budget+seed 的 P/S 使用相同 probe，但 43101 / 43102 / 43103 使用不同 probe。

这意味着跨 seed 的 \(D_I\) 差异不能纯粹归因于模型。

### 5.2 关键混杂 2：probe/sample difficulty 主导测量

审计得到：

- 2048 budget：probe variation 为 structure variation 的 **5.44×（raw-L2）/ 9.19×（log-L2）**；
- 8192 budget：为 **10.44× / 7.95×**。

同 probe 下 P/S 的逐 step \(d_t\) 相关性非常高：Pearson 约 `0.981–0.999`，Spearman 约 `0.945–1.000`。

当前最合理的解释是：

\[
\boxed{\text{第一版 }D_I\text{ 主要受 probe/sample difficulty 影响，而非结构效应。}}
\]

### 5.3 关键混杂 3：诊断 step 太少且贡献高度集中

第一版只使用 11 个诊断 step，每 step 只有一个 train–ghost replacement。

审计发现：

- 最大单 step 占总 \(D_I\)：`22.9%–52.5%`；
- top-3 step 占比：`59.0%–80.9%`。

因此当前 \(D_I\) 是明显高方差的稀疏估计。

### 5.4 raw checkpoint 与 MMS2 量化后性能错位

训练期间的 \(D_I\) 对应 raw checkpoint，但原主相关分析使用 MMS2 解码后的 3-bit 模型性能。

审计发现：

- 中位数 `|Δperformance| = 3.85e-5`；
- 最大 `|Δperformance| = 2.20e-4`；
- 6 个 P/S pair 中有 1 个排序因量化翻转；
- 改用 raw error 后，`Spearman(D_I,error)` 从 `0.5105` 降为 `0.2657`。

因此主性能指标与诊断模型状态没有严格对齐。

### 5.5 正式结论

第一版实验最终分类为：

\[
\boxed{\text{B — MEASUREMENT INFRA CONFOUNDED}}
\]

状态规则：

- 原始数据和结果永久保留；
- 第一版 \(D_I\) 标记为 `INVALID_FOR_INFERENCE`；
- **不能**用它支持 P/S 结构比较；
- **不能**用它支持 \(D_I\) 与真实泛化的相关性；
- **不能**用它判定 CMI 主线或 \(D_I\) 理论代理成功 / 失败。

当前正确表述是：

\[
\boxed{\text{第一版实验不可判定 }D_I\text{，而不是 }D_I\text{ 已被否定。}}
\]

---

## 6. 当前下一步：只设计一次 D_I 最小挽救实验

**状态：PROPOSED / NOT YET FROZEN。现在不能启动正式训练。**

下一份正式工作应是一页以内、可预注册的“DI 最小挽救实验设计”。设计必须至少满足：

1. 只先使用低成本 `budget=2048`；
2. 保留 P/S × 3 model seeds，共 6 条训练轨迹；
3. `model/config_seed` 与 `probe_seed` 完全分离；
4. 所有模型共享完全相同的固定 probe panels；
5. 每条训练轨迹内部评估多个 panel，不把 panel 扩张成新的独立训练；
6. 诊断 step 数明显高于 11，并保存逐 panel、逐 step 贡献；
7. 主相关分析统一使用产生 \(D_I\) 的同一个 **raw checkpoint**；
8. MMS2 只作为独立量化干预分析，不混入 \(D_I\) 主相关结论。

具体 panel 数量、step 数量和计算成本必须先根据现有审计数据估计后再冻结；不得以 `32–64` 之类范围直接进入正式协议。

建议的稳定性判据包括：

- probe panel variance / structure variation；
- 跨 panel ICC 或排序稳定性；
- leave-one-step-out 稳定性；
- 最大单 step 和 top-3 contribution 占比；
- P/S 差异方向是否跨 panel 一致。

### 停止条件

如果在**共同 probe、多 panel、更多诊断 step、raw checkpoint 对齐**之后，仍出现：

- probe variation 明显大于 structure variation；或
- 排序持续由极少数 step 支配；或
- P/S 方向跨 panel 不稳定；

则永久停止把当前 \(D_I\) 作为 P/S 结构解释指标。

这只是否定：

\[
\text{图像组 CMI} \rightarrow D_I
\]

这一座具体“可计算代理桥”，**不等于否定图像组数据依赖 / CMI 理论主线。**

---

## 7. 如果 D_I 最小挽救仍失败

不能回到“继续优化压缩码长”，也不能用 held-out error 自己解释自己。

此时应：

1. 将 raw held-out image-group performance 继续作为**被解释变量**；
2. 回到理论寻找新的、独立于测试性能的训练过程 / 数据依赖机制量；
3. 新量仍必须通过：新科学内容、解释码长—性能脱钩、可导出算法、MiniMind-V 可验证四项筛选。

---

## 8. 当前禁止事项

在 D_I 最小挽救设计正式冻结前：

- 不启动新正式训练；
- 不访问最终独立 confirmation set；
- 不把第一版 \(D_I\) 重新拿来做结构推断；
- 不宣布 CMI 主线失败；
- 不为了救结果事后调整 probe、step 或统计门槛；
- 不把 raw held-out error 当成新的“解释变量”；
- 不提前进入阶段四。

---

## 9. 当前未入库的审计产物

infra 审计当前报告的本地路径包括：

```text
experiments/results/phase3_image_group_dependence_sgd_v1/infra_audit/infra_audit_summary.json
experiments/results/phase3_image_group_dependence_sgd_v1/infra_audit/diagnosis_steps.csv
experiments/results/phase3_image_group_dependence_sgd_v1/infra_audit/raw_vs_mms2.csv
experiments/results/phase3_image_group_dependence_sgd_v1/infra_audit/raw_development/
experiments/results/phase3_image_group_dependence_sgd_v1/infra_audit/gradient_connectivity.json
```

截至本文 v1 写入时，这些 `infra_audit` 产物尚未在远端分支中发现。**在下一轮正式实验前，应先把审计摘要和必要证据冻结入库，并记录 commit。**

---

## 10. 新对话启动模板

以后无需人工重新讲完整历史。新对话第一条只需说：

> 继续上海交通大学实习——VLM 泛化理论项目。请先读取 `docs/project/CURRENT_STATE.md`，再按需读取 `docs/theory/VLM泛化理论基线.md`、`docs/project/DECISION_LOG.md` 和 `docs/project/EXPERIMENT_REGISTRY.md`。仓库文档优先于聊天记忆。

