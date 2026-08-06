# XMC-01 Round 2 — 生成式 LVLM 跨模态表示保持理论桥 gate

**日期**：2026-08-07  
**阶段**：阶段三  
**类型**：定向 primary-literature + theorem applicability audit；本 round 不训练、
不运行 checkpoint、不访问 final confirmation set  
**不可变性**：本文件提交后不修改判定标准；若 gate 支持后需要 prediction test，
另建严格验证 round，不在本文件事后补 statistic、dataset 或阈值。

## 科学问题

现有关于 multimodal contrastive learning / 图文共现谱的正式理论，能否为
MiniMind-V 这类 autoregressive generative LVLM 定义一个不依赖生成 caption 语言
偏好的“模型保持跨模态对应结构”对象，并导出方向明确、可在未查看外部数据上验证
的泛化 prediction？

## 假设

假设 H：至少存在一个可核查的正式理论对象或可在本项目中自洽重推的桥，使

> 图文联合分布的任务相关跨模态方向  
> → 冻结 LVLM 中可识别的表示保持量  
> → 未见数据语义风险方向

三者在明确假设下连接；该桥不能把 dual-encoder contrastive loss、linear-probe
risk 或经验相似度直接改名为 autoregressive generation risk。

若所有可核查理论都止于 contrastive dual encoder / linear probe，或只能提出没有
方向保证的经验 representation proxy，则 H 在当前 Research Envelope 下不成立，
`XMC-01` model-retention bridge 不得进入 checkpoint scoring。

## VLM 特有性

对象必须依赖图像—文本联合分布、配对对应或跨模态表示算子；单模态 hidden-state
范数、通用压缩量、checkpoint code length 或普通语言 likelihood 不满足本 gate。

## 可证伪预测

本 round 的 prediction 是理论可用性 prediction：

> 若 XMC 是当前可执行的科学机制，则 primary sources 或一段显式项目内推导应给出
> 至少一个方向固定的 representation-retention quantity，并允许在不查看旧
> SugarCrepe++ / What’sUp 模型输出来选择 statistic 的前提下，预先指定新的外部
> test。

如果定向检索和逐项假设映射后仍不能得到该对象，则 model-retention 版本被当前
证据否定；“以后也许能找到某个 proxy”不属于支持。

## 最小实验

1. 检查已有 `sources/` 与 `docs/project/literature/`，避免重复检索；
2. 定向检索 2022–2026 primary papers，范围只包括：
   - multimodal contrastive / cross-modal spectral theory；
   - generative LVLM 表示与视觉 token 利用的正式分析；
   - paired cross-modal representation 的 identifiability、CCA/kernel operator、
     linear-probe 或 downstream-risk bridge；
3. 对每个最相关 primary source 完整核查 theorem statement、数据对象、loss、
   architecture、downstream risk、独立性和需要重证明的环节；
4. 形成 theorem applicability matrix，并只保留一个最强 bridge；
5. 若 gate 支持，写出唯一 statistic 的数学定义、新外部未查看对象、方向预测和
   最小资源；本 round 不运行该 test；
6. 若 gate 否定，立即记录并转向 `VISCOND-01`，不得用多个 representation proxy
   exploratory sweep 营救。

## 支持标准

必须同时满足：

1. 至少一个 primary source 含正式 theorem / proposition，或项目内给出完整、
   可审计的有限假设推导；
2. 明确区分 source theorem 的 contrastive / probe 对象与 MiniMind-V
   autoregressive risk，并列出桥接所需附加假设；
3. quantity 能由冻结 checkpoint 和未查看的非-final 外部数据唯一计算，不从多个
   kernel、layer、pooling、CCA rank 或相似度中择优；
4. 给出方向明确的 M2/M3 paired prediction；
5. prediction 不与已否定的 What’sUp caption-NLL margin 同义；
6. 若 prediction 成立，能够自然导出数据筛选、表示保持正则或训练目标原则。

## 否定标准

满足任一项即 `REJECT_IDEA`（model-retention bridge）：

1. 所有正式结果仅覆盖 contrastive dual encoder + linear probe，迁移到
   autoregressive LVLM 需要当前无法证明的核心假设；
2. 候选 quantity 只是 post-hoc correlation、CKA/CCA/HSIC/相似度等经验量，理论
   不固定其 layer、pooling、kernel、rank 或方向；
3. 最小合法验证必须先查看多个 proxy / layer 再选最好者；
4. quantity 与 `COMP-01` 已否定的生成 likelihood binding margin 本质同义；
5. 在 MiniMind-V 当前 artifact 上无法计算，且补齐需要超出当前资源或改变统计
   对象。

## 无法判断标准

只限：

1. 关键 primary paper 正文或 theorem appendix 无法合法获取；
2. theorem statement 内部依赖缺失补充材料，无法核查；
3. 当前 checkpoint artifact 缺少 theorem 明确要求且不可重建的表示。

`INCONCLUSIVE` 不自动获得 proxy sweep 或新训练预算。

## 可能混杂

- linear probe 的可分性不等价于生成风险；
- CCA/CKA/HSIC 对 layer、centering、kernel 和 sample size 敏感；
- frozen SigLIP2 已带有外部预训练对应结构，adapter retention 与 base capability
  可能混合；
- text representation 选择可能重新引入语言偏好；
- 同一数据训练的 M2/M3 只能检验模型保持，不检验数据共现因果；
- 经验谱相关不能被描述为正式泛化界。

## 所需资源

- 文献：primary paper/appendix 与官方代码；所有新检索保存到 `sources/`；
- CPU/RAM：仅文本、公式和 artifact schema 审计；
- GPU：0；
- 训练：0；
- final confirmation：禁止访问；
- 若 gate 支持，后续 prediction test 必须另建 plan 并 commit。
