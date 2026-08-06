# 上海交通大学实习——当前研究状态

**版本：v2**  
**日期：2026-08-06**  
**定位：项目的当前工作状态入口。任何新对话、Codex 任务或阶段三研究决策开始前，先读本文。**

---

## 0. 文档职责与优先级

本项目固定使用以下四类文档，避免依赖聊天上下文：

1. `docs/project/CURRENT_STATE.md`：**当前状态的最高优先级入口**，回答“我们现在做到哪、下一步是什么”。
2. `docs/theory/VLM泛化理论基线.md`：**理论单一事实来源**，回答“哪些理论已成立、哪些待证明、哪些路线已否定”。
3. `docs/project/DECISION_LOG.md`：关键研究决策及原因，不删除历史。
4. `docs/project/EXPERIMENT_REGISTRY.md`：正式实验、审计、commit、状态和结论索引。

若历史聊天内容与上述文档冲突，以仓库中最新文档为准。

> 理论基线只有在理论定义、定理状态或主路线发生实质变化时更新；普通实验状态变化优先记录在本文、DECISION_LOG 和 EXPERIMENT_REGISTRY。

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

阶段三 P/S 实验已经稳定暴露出：

\[
\boxed{\text{编码复杂度下降} \not\Rightarrow \text{真实 VLM 泛化改善}}
\]

因此，单纯继续优化 checkpoint 描述长度不足以解释或改善当前问题。

---

## 3. 当前理论主线

当前第二层主线仍是：

\[
\boxed{
\text{新图像泛化}
\rightarrow
\text{图像组级训练数据依赖}
\rightarrow
\text{CMI / 信息论泛化工具}
\rightarrow
\text{合法、稳定、可计算的训练过程量}
\rightarrow
\text{训练算法}
}
\]

外层统计单位优先使用独立图像组：

\[
G_i=(I_i,\mathcal Y_i).
\]

当前真正未完成的桥梁仍然是：

\[
\text{抽象图像组 CMI}
\longrightarrow
\text{可计算、可训练、并具有经验稳定性的训练过程量}.
\]

**CMI / 图像组数据依赖主线没有被当前实验否定。**

---

## 4. 第一版图像组 replacement sensitivity：历史结论

第一版诊断量为：

\[
D_I=\sum_t\eta_t^2\|g_t-g_t^{ghost}\|_2^2.
\]

实验身份：

- branch：`stage3-image-group-dependence-sgd-v1`
- protocol commit：`ea1b58d6d82e12d311975fb1facbb624d611f8de`
- MMS2 fix：`118a5416bc914d9d4d178e871f63026d97a9291c`
- formal results：`584920421f0e718a9c186d353d704a8ffac003f7`
- P/S × {2048,8192} × 3 seeds
- plain SGD

实现审计没有发现 bug，但发现三个关键测量问题：

1. `config_seed` 同时决定 model mapping 与 train/ghost probe，导致 model seed 与 probe seed 混杂；
2. probe variation 明显大于 structure variation：2048 为 5.44× / 9.19×，8192 为 10.44× / 7.95×；
3. 只有 11 个 diagnostic steps，最大单 step 占 22.9%–52.5%，top-3 占 59.0%–80.9%；
4. \(D_I\) 来自 raw checkpoint，但原相关分析混入 MMS2 量化后性能，且出现 1/6 P/S 排序翻转。

因此第一版正式分类：

\[
\boxed{\text{B — MEASUREMENT INFRA CONFOUNDED}}
\]

状态：`INVALID_FOR_INFERENCE`。第一版结果不得用于 P/S 结构比较、\(D_I\)-performance 相关性或 CMI 理论成败判断。

---

## 5. crossed checkpoint-only pilot：已完成

为了判断第一版失败究竟只是 probe 基础设施问题，还是当前 \(D_I\) 测量本身不稳定，执行了一个**不重新训练模型**的 crossed diagnostic pilot。

### 5.1 Pilot 固定设计

- budget：2048
- 现有 6 个 raw checkpoints：P/S × 3 model seeds
- shared probe panels：K=3
- 每 panel probes：T=33
- 总 diagnosis：6 × 3 × 33 = 594
- model seed 与 probe seed 完全分离
- 所有六模型使用逐项完全一致的 99 个 probe
- 未使用 MMS2
- 未访问 final confirmation set
- 未做性能相关性分析

shared-probe identity audit：**PASS**。99 个 panel/slot 的 train/ghost group、图像哈希、conversation 哈希、预处理和选中位置在六模型间逐项一致。

### 5.2 Pilot 关键结果

T=33 时：

- ICC(A,1)：raw `0.084`，log `0.160`；
- panel 间 Pearson：raw `0.775–0.836`，log `0.880–0.933`；
- panel 间 Spearman：raw `0.771–0.943`，log `0.829–0.943`；
- 最低 P/S bootstrap 符号保持率：T=11/22/33 分别为 `0.566 / 0.584 / 0.497`。

随着 K=1→2→3，probe/structure ratio 会下降：

- raw：T=33 时 `1.372 → 0.996 → 0.815`；
- log：T=33 时 `1.036 → 0.742 → 0.609`。

随着 T=11→22→33：

- bootstrap CV 从 `0.084–0.194` 降到 `0.059–0.106`；
- 最大单 probe 占比从 `12.3%–26.6%` 降到 `5.7%–10.2%`；
- top-3 占比从 `36.0%–48.3%` 降到 `16.2%–23.7%`。

说明增加 probes / panels **确实改善了贡献集中和总体方差**。

但核心 P/S 结构信号仍不稳定：

- seed 43101：三个 panel 为 `P>S / P<S / P>S`，存在方向翻转；
- seed 43102、43103：三个 panel 均为 `P<S`；
- 最低 bootstrap P/S 符号保持率在 T=33 时仅 `0.497`；
- ICC 很低，说明绝对测量跨 panel 一致性不足。

Pilot 最终结论：

`DI_MEASUREMENT_STILL_UNSTABLE`

---

## 6. 当前 D_I 路线的正式状态

根据预先规定的停止规则，**不再继续增加 panel、probe 或重新训练来挽救当前 \(D_I\)**。

正式停止的是下面这座具体代理桥：

\[
\boxed{
\text{图像组 CMI}
\not\Rightarrow
\text{当前 }\sum_t\eta_t^2\|g_t-g_t^{ghost}\|^2\text{ replacement sensitivity 代理}
}
\]

更准确地说：当前实验没有证明二者理论上“不可能有关”，而是证明了**当前这一具体、可计算的 gradient replacement sensitivity 测量不足以稳定承担 P/S 结构解释指标的角色，因此项目停止继续使用它作为主代理。**

这**不等于否定**：

- 图像组 CMI；
- 图像组训练数据依赖；
- 信息论泛化主线；
- 未来其他训练轨迹可计算量。

---

## 7. 当前下一步：回到理论层寻找新的 CMI → 可计算量桥梁

现在不再做 D_I 的正式 rescue training。

下一步首先是**理论工作**，而不是新的 MiniMind-V 训练：

1. 重新检查标准 CMI / SGD 信息论泛化结果中真正进入上界的训练过程量，不能再只抽取一个局部梯度差项；
2. 判断是否需要保留局部平滑、虚拟扰动、最终输出敏感性等完整结构；
3. 寻找一个与测试性能独立、可低成本估计、跨 probe 稳定的候选量；
4. 新候选必须同时满足四项筛选：
   - 有超出已有压缩界 / 标准 CMI 的新科学内容；
   - 有可能解释码长—真实性能脱钩；
   - 能自然导出训练算法或训练决策；
   - 能在 MiniMind-V 上低成本验证并具有一般 VLM 含义。

在提出下一项 Codex 实验前，仍必须先给出 ≤1 页科学设计并经用户确认。

---

## 8. 当前禁止事项

- 不继续给当前 \(D_I\) 加 panel / probe / step 来“救结果”；
- 不重新运行当前 \(D_I\) 正式训练；
- 不访问 final confirmation set；
- 不把第一版 confounded \(D_I\) 拿回做结构推断；
- 不把 crossed pilot 写成“CMI 已失败”；
- 不回到只优化 checkpoint 码长；
- 不用 held-out error 自己解释自己；
- 不提前进入阶段四。

---

## 9. 仓库同步状态

Codex 报告 crossed pilot 产物位于：

```text
experiments/results/phase3_di_crossed_probe_pilot_v1/
```

并报告本地 commit：

```text
b1205ae42bb2af2e0658d440d90799db3ed43ced
```

但截至本文 v2 更新时，通过 GitHub 远端接口：

- 未能解析上述 commit；
- 未发现 `experiments/results/phase3_di_crossed_probe_pilot_v1/`；
- 仍未发现上一轮 `phase3_image_group_dependence_sgd_v1/infra_audit/`。

因此当前应把这些产物视为**Codex 已完成、但尚未确认推送到远端仓库**。在下一次正式 Codex 实验前，应先把 pilot 与 infra audit 必要产物 push / freeze，并把真实远端 commit 回填到 `EXPERIMENT_REGISTRY.md`。

---

## 10. 新对话启动模板

新对话第一条只需说：

> 继续上海交通大学实习——VLM 泛化理论项目。先读取 GitHub `docs/project/CURRENT_STATE.md`，仓库文档优先于聊天记忆。请先核对当前 D_I proxy 的停止状态和仓库同步状态，再继续理论主线。
