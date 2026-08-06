# 上海交通大学实习——当前研究状态

**版本：v3**  
**日期：2026-08-06**  
**定位：项目当前工作状态的最高优先级入口。任何新对话、Codex 任务或阶段三研究决策开始前，先读本文。**

---

## 0. 文档职责与优先级

1. `docs/project/CURRENT_STATE.md`：当前状态最高优先级入口。
2. `docs/theory/VLM泛化理论基线.md`：理论单一事实来源。
3. `docs/project/DECISION_LOG.md`：关键研究决策，只追加历史。
4. `docs/project/EXPERIMENT_REGISTRY.md`：正式实验、审计、commit、状态与结论索引。
5. `docs/project/ACTIVE_RESEARCH_QUESTION.md`：人工冻结的一级科学问题与 Research Envelope。
6. `docs/project/IDEA_REGISTRY.md`：candidate idea 的长期登记与淘汰记录。
7. `docs/project/REVIEW_QUEUE.md`：不停机的异步人工审查队列。
8. `docs/project/AUTONOMOUS_LOOP_STATE.md`：跨调用恢复所需的最小机器状态。
9. `docs/project/NIGHT_POLICY.md`：预授权夜间自治规则。

若聊天记忆与仓库最新文档冲突，以仓库为准。

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

当前仍属于**阶段三**。只有当阶段三得到的理论规律正式用于训练目标、预算分配或模型选择时，才进入阶段四。

---

## 2. 当前已经确认的经验事实

阶段三 P/S 实验稳定暴露出：

\[
\boxed{\text{编码复杂度下降} \not\Rightarrow \text{真实 VLM 泛化改善}}
\]

因此，单纯继续优化 checkpoint 描述长度不足以解释或改善当前问题。

---

## 3. 当前研究对象的边界

任务书要求研究的是一般意义上的 **VLM 泛化**，即模型在未见数据上的表现。

此前“新图像条件泛化”是一个合法、清晰的子问题，但**不能与全部 VLM 泛化等同**。未见数据还可能涉及新图文组合、新问题/指令、新域、组合泛化等。

因此当前阶段不再把项目整体锁死为“只研究新图像泛化”。新图像条件泛化保留为重要子问题和可能的理论落点。

---

## 4. 当前大方向共识：先找 VLM 相比 LLM 真正新增的泛化因素

当前不再一头扎进某个单一 proxy 或局部公式。先在任务书大方向下系统比较 VLM 泛化的主要来源。

### 4.1 数据侧

研究图像、文本及图文关系本身如何影响泛化，例如：

- 图文配对质量与噪声；
- 数据多样性、覆盖和共现结构；
- 图像、文本、图文组合的层次化统计结构；
- 域变化、组合变化等 VLM 特有分布因素。

目标不是得出“图像和文本都重要”这种显然结论，而是寻找**可定量、可预测、可用于数据选择或训练的规律**。

### 4.2 模型 / 表示侧

研究 VLM 的跨模态结构是否学到了真正可迁移的联合表示，例如：

- 视觉与语言信息如何融合；
- 模态失衡 / 模态坍塌；
- 跨模态共享表示、组合表示与可迁移结构；
- 为什么某些参数共享或压缩可以减少码长，却不改善真实性能。

### 4.3 训练侧

研究训练算法如何决定 VLM 最终泛化，例如：

- 对具体训练样本的数据依赖；
- 优化稳定性与训练轨迹；
- 正则化、采样和训练目标；
- 能否从泛化理论直接推出新的训练机制。

### 4.4 三条方向的关系

三者不是互斥路线。最终更可能形成：

\[
\boxed{
\text{数据结构}
\rightarrow
\text{模型/表示如何吸收信息}
\rightarrow
\text{训练过程如何形成最终模型}
\rightarrow
\text{泛化}
}
\]

当前任务是先比较三条大方向的科学价值与理论可行性，再决定阶段三主攻点。

---

## 5. CMI / 图像组数据依赖的当前定位

CMI 与图像组数据依赖**没有被否定**，但不再预设为整个项目唯一的第二层主线。

当前定位：

- 它属于**训练侧**的重要理论工具；
- 图像组 CMI 仍可用于研究“模型对具体训练图像身份的依赖”；
- 是否继续作为主攻方向，要和数据侧、模型/表示侧一起比较；
- 不再为了维护 CMI 路线而强行寻找新的单标量 proxy。

---

## 6. 当前 gradient replacement \(D_I\) 路线的正式状态

第一版：

\[
D_I=\sum_t\eta_t^2\|g_t-g_t^{ghost}\|_2^2
\]

经 infra audit 判定：

\[
\boxed{\text{B — MEASUREMENT INFRA CONFOUNDED}}
\]

crossed checkpoint-only pilot 在解耦 model seed / probe seed、增加 shared probes/panels 后，最终仍得到：

\[
\boxed{\text{DI\_MEASUREMENT\_STILL\_UNSTABLE}}
\]

因此正式停止：

\[
\boxed{
\text{图像组 CMI}
\rightarrow
\text{当前 gradient replacement }D_I\text{ 代理}
}
\]

不再增加 panel、probe、step，也不启动正式 rescue training。

这只否定当前具体代理，不否定 CMI、图像组数据依赖或其他信息论/训练稳定性理论。

---

## 7. 本轮理论讨论中形成但尚未升格为主线的内容

本轮讨论过“图像外层 + 条件文本内层”的层次化风险/梯度分解，以及 Neu 类 SGD 信息论工具。

这些内容目前只保留为**候选理论工具 / 基础引理方向**，原因是：

- “VLM 同时受图像和文本影响”本身科学新意不足；
- “固定预算如何分配图片与文本”尚未由任务或现有理论必然导出，不应拍脑袋升格为主线；
- 任何梯度方差、CMI、稳定性量都必须先证明其增加了真正的 VLM 科学内容，而不是重新命名已有理论。

---

## 8. 当前下一步

**先做大方向理论与文献筛选，不开新实验。**

下一步应围绕一个总问题：

\[
\boxed{\text{VLM 相比 LLM，泛化问题到底“新”在哪里？}}
\]

具体任务：

1. 以任务书和两篇核心论文为主干；
2. 按需补充可靠的 VLM / CLIP 泛化理论、跨模态表示、模态失衡、数据结构与训练算法文献；
3. 系统比较**数据侧、模型/表示侧、训练侧**三条大方向；
4. 每条方向必须回答：
   - 是否有真正 VLM 特有的新科学内容；
   - 是否可能解释“码长—真实性能脱钩”；
   - 是否能自然导出训练算法或训练决策；
   - 是否能在 MiniMind-V 上低成本验证并具有一般 VLM 含义；
5. 比较完成后，再冻结阶段三新的主攻科学问题。

在此之前，不启动新的 Codex 实验。

---

## 9. 当前禁止事项

- 不继续挽救当前 \(D_I\)；
- 不把 crossed pilot 写成“CMI 已失败”；
- 不回到只优化 checkpoint 码长；
- 不因为已经研究过 CMI 就默认它必须继续成为唯一主线；
- 不把“图像和文本都影响泛化”这种显然事实包装成主要创新；
- 不先拍脑袋提出具体数据分配、正则项或 proxy，再反过来找理论；
- 不访问 final confirmation set；
- 不提前进入阶段四。

---

## 10. 仓库同步状态

Codex 曾报告 crossed pilot 本地产物：

```text
experiments/results/phase3_di_crossed_probe_pilot_v1/
```

本地 commit：

```text
b1205ae42bb2af2e0658d440d90799db3ed43ced
```

截至 v3 更新时，GitHub 远端仍未解析到该 commit，也未发现 crossed pilot 与上一轮 `infra_audit/` 目录。

因此在**下一次正式 Codex 实验前**，仍需先完成这些证据的 push / freeze，并回填 `EXPERIMENT_REGISTRY.md`。

---

## 11. 新对话启动模板

> 继续上海交通大学实习——VLM 泛化理论项目。先读取 GitHub `docs/project/CURRENT_STATE.md`，仓库文档优先于聊天记忆。当前仍处于阶段三；gradient replacement `D_I` 路线已停止。现在不要先钻入某个具体 proxy 或实验，请以任务书和两篇核心论文为主干，按需补充最新可靠文献，系统比较 VLM 泛化的**数据侧、模型/表示侧、训练侧**三条大方向，先回答“VLM 相比 LLM，泛化问题到底新在哪里”，再决定新的主攻理论方向。
