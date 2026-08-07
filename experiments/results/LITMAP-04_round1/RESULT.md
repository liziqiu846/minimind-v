# LITMAP-04 Round 1 Result

## 当前科学问题

在 visual-necessary supervision 与 fixed-total projector allocation 都失败后，
是否存在 direct autoregressive-LVLM evidence 支持的 objective-routing /
task-specific-absorption 机制，能转成当前 MiniMind-V 上唯一、无需 sweep 的最小
二条件实验？

## 假设

若该方向值得当前优先检验，则至少两篇独立 primary sources 应提供直接机制证据，
其中至少一篇有 matched control；同时应能唯一预注册一个区分至少两个竞争解释、
具有新 mechanism 与 external prediction 且不复用已失败路线的本地干预。

## 本轮实验

按冻结的五族 query 使用 arXiv/OpenAlex fallback 搜索 555 records、523 unique
titles，并标记 81 个既有检索重复；完整核查 14 篇决定性 primary sources 的
problem setting、modules、objective、controls、theory、external evidence、
limitations 与本地可行性。本轮 GPU、checkpoint inference、training 均为 0，未访问
final confirmation。

## 判定标准

- **支持**：≥2 个独立 direct autoregressive-LVLM sources、≥1 matched mechanism
  control、≥1 mechanism/in-domain + external evidence，并能形成唯一 no-sweep
  本地干预。
- **否定**：只能依赖额外 architecture/data/compute、多 component、loss weight /
  layer / rank / task / mixture sweep、已失败 proxy/instantiation，或不能产生
  external prediction。
- **无法判断**：仅限决定性全文/appendix、source identity/control 或本地 feasibility
  无法核查。

## 执行结果

- direct-source 数量门通过：CoMMIT、ROSS/ASVR/DV-SFT、VIGIL、OPD-V 等直接干预
  autoregressive MLLM，并有多项 matched/component control 与 external benchmark
  结果。
- 唯一最小干预门失败：
  - CoMMIT 需要 component LR、额外 distribution estimate 与 auxiliary loss；
  - ROSS/ASVR/DV-SFT/JARVIS/LaVer 需要 tokenizer/head/teacher/masking、loss weight
    或 target-layer 选择；
  - DPA/VIGIL 依赖 seeing/blind 类 proxy、proxy/preference stages 与 gating；
  - OPD-V 需要 bbox zoom/mask、EMA 双 teacher、8 rollouts、top-K JSD 和 4×H200；
  - task-specific-overfitting remedy 需要 dataset/mixture-ratio search；
  - Pareto LoRA 依赖本地不存在的 image-generation objective；
  - 唯一原本无需额外 component 的 V-GIFT local route 已由 `VISSUP-01` 当前
    instantiation 有效否定。
- 这些路线都不能在不恢复 task/ratio/allocation/seed/proxy search 的前提下，唯一
  区分 frozen-feature mismatch、task-specific absorption 与 objective competition。
- 14/14 决定性来源均有正文/appendix 或 source archive 可核查，不满足“无法判断”。

## 结论

`LITMAP-04` 得到 `NO_CANDIDATE`：当前 objective-routing / task-specific-absorption
文献到本地最小实验的 bridge 被否定，failure level=`BRIDGE_REJECTED`。这不否定
objective competition、gradient routing、task-specific absorption 或
frozen-feature/objective mismatch 机制本身。

## 下一步

转向数据/表示侧的新对象：以两次训练 instantiation 都未学会 held-out rotation
为约束，先建立一个 `LITMAP-05` frozen-feature sufficiency / identifiability gate，
寻找不需要训练、layer/rank/proxy sweep 的直接 decoder-readout falsifier；若不存在
理论唯一 readout，则转向具有权威 domain/mixture labels 的 controlled coverage
candidate，不无机制地启动 `OBJ-01`。

## 状态

`REJECT_IDEA`
