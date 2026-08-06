# XMC-01 Round 1 — 历史 P/S 图文训练图一致性审计

**日期**：2026-08-07  
**阶段**：阶段三  
**类型**：read-only artifact/protocol audit；不读取 final confirmation set；不训练  
**不可变性**：本文件提交后不修改判定标准。

## 科学问题

`XMC-01` 的纯数据版本（图文配对语义误差与共现图结构）能否解释历史 P/S
同预算、同 seed 的码长—性能脱钩，还是它在 P/S 间实际不变，因而必须引入
“模型保留跨模态结构的程度”这一表示层机制？

## 假设

假设 H：历史 P/S 同预算、同 seed 配对使用相同的训练样本身份、图文关系、顺序/
采样配置和数据预处理协议。因此数据侧的配对误差与共现图在该配对内不变，纯数据
版本的 `XMC-01` 不能单独解释 P/S 性能排序。

若 P/S manifest 显示训练样本图或采样关系存在实质差异，则 H 不成立，数据差异是
必须先排除的混杂。

## VLM 特有性

审计对象不是参数量或普通训练 seed，而是图像节点、文本节点及其配对/采样边构成的
跨模态训练图。该对象在单模态 LLM 中不存在。

## 可证伪预测

对每个可审计的 `(budget, seed)` P/S pair：

- 训练数据来源、训练/选择 split、采样 seed、训练样本数、协议 hash 与任何可用的
  样本/图文清单 hash 应完全一致；
- 唯一允许不同的是结构参数化、模型/优化状态及其派生产物。

任何一个影响实际图文训练边的字段出现 P/S 差异，都会否定对应 pair 的预测。

## 最小实验

1. 只读取 `phase3_risk_v1` / `phase3_private_vs_shared_v1` 已有配置、protocol、
   training manifest 和 run receipt；
2. 自动发现 P/S 同预算同 seed 配对；
3. 规范化并比较所有可识别的数据身份、split、sampler、shuffle、seed、步数、样本数、
   manifest/protocol hash 字段；
4. 输出逐 pair equality/difference 与字段覆盖率；
5. 不重新计算或筛选任何性能 proxy，不访问 confirmation artifact。

## 支持标准

所有可审计 P/S pair 的数据图相关字段一致，且没有发现可改变图文训练边的结构性
缺失；结论为：

> `PURE_DATA_XMC_INVARIANT_WITHIN_PS`

这只否定 `XMC-01` 的纯数据版本对同数据 P/S 排序的解释，不否定其对跨数据/预算
泛化的价值，也不证明模型保持版本成立。

## 否定标准

至少一个 P/S pair 存在可复现的训练样本身份、配对关系、采样 seed/顺序、split 或
有效训练边差异；结论为：

> `PS_DATA_GRAPH_CONFOUNDED`

此时不得把 P/S 性能差归因于表示保持，必须先冻结数据混杂。

## 无法判断标准

manifest/receipt 没有保存足以重建或核对训练图的字段，或关键文件缺失；结论为：

> `DATA_GRAPH_IDENTITY_NOT_AUDITABLE`

此时只记录证据缺口，不从“配置看起来相同”推出实际训练图相同。

## 可能混杂

- 配置相同但 replacement sampling 的实际序列未保存；
- dataset 文件内容在运行后被替换；
- P/S 使用相同 seed 但不同代码路径消费 RNG；
- protocol hash 一致却未覆盖外部数据文件；
- 把预算差异误当作同预算结构差异。

## 所需资源

- GPU：0 小时；
- 运行：CPU read-only manifest audit；
- 输出：审计脚本、JSON 结果、简短结论；
- 禁止：性能相关性搜索、模型 forward、重新训练、final confirmation。

