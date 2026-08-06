# LITMAP-03 Round 1 Result

## 当前科学问题

VISSUP 的视觉监督没有进入 4,096-coordinate M2-current，主要应优先检验 frozen
encoder 不可读、module allocation 不足，还是 objective competition/routing？

## 假设

若权威 autoregressive-LVLM 文献能给出至少两条独立的 module-specific 干预证据，
且本地可用一个固定总容量、无比例搜索的实验区分 competing explanations，则只登记
一个新 candidate；否则记录 `NO_CANDIDATE`。

## 本轮实验

五族 arXiv/OpenAlex 检索得到 541 raw records、480 unique titles，并与既有
LITMAP/XMC sources 去重；随后核查 11 篇决定性 primary sources 的正文与附录。
本地只读检查了 M2 target registry、arbitrary private-coordinate constructor、
VISSUP data/scorer artifacts、历史未执行 curve infrastructure、GPU/disk 与运行成本。
本轮没有运行模型或训练。

## 判定标准

- 支持：至少两篇独立 direct autoregressive-LVLM sources、至少一个 matched
  mechanism/competing-module control、唯一最小本地干预、尚未验证的 mechanism
  与 external direction prediction，且不需 sweep。
- 否定：证据只到非生成式 proxy、更多参数/架构替换混杂，或本地只能换
  task/ratio/seed/metric 才能测试。
- 无法判断：只限决定性全文、source identity、control 实现或本地 artifact
  可行性无法核查。

## 执行结果

- ACL 2024 的 MLLM PEFT 实证在同任务/训练设置下直接比较 connector
  tune-vs-freeze，并在附录比较 visual encoder tune-vs-freeze：connector 对 unseen
  tasks 更常有益，visual unfreeze 多数无益。
- CROME 在 autoregressive MLLM 中冻结 encoder 与 LLM，仅训练 pre-LLM adapter，
  仍在 unseen task-specific SQA/AI2D 上获得强 adaptation。
- Cambrian-1 在 23 个 vision encoders、相同 LLM/data/hyperparameters 下发现
  unfreeze vision encoder 对多数 visual-centric tasks 有益；但增加参数和约
  50–55% training time。
- 三者证明 module trainability 是 VLM-specific 可干预对象，同时留下
  encoder-vs-projector 的真实冲突；CoVFT、HyperLLaVA 等支持 routing/动态模块可能
  有效，但均需 architecture replacement、layer/route choice 或大规模训练。
- Pareto LoRA 的独立 text/image losses 不存在于本地 text-only output MLLM；
  TinyAlign 的 “effective MI” 依赖未证明的正信息与误差降低假设；二者均未通过
  bridge gate。
- 本地可把总数严格固定为 4,096，仅把 dimensions 从 current
  `582/2327/1187` 改为唯一极端 `1/4094/1`；mapping-only gate 已通过。旧 72-run
  module curve 未执行且违反当前 no-sweep rule，不使用。

## 结论

文献门通过并只选择 `PROJALLOC-01`：用 current allocation 对
projector-dominant fixed-total allocation，直接区分“frozen features 可读但
projector subspace 容量不足”与“增加 projector 容量仍无法读取/吸收视觉信号”。
文献只支持提出该可证伪假说，不支持预先宣称 projector 更优。

## 下一步

登记 `PROJALLOC-01`，另建并提交 immutable paired-pilot plan；使用 fresh mapping
roots，保持 VISSUP visual-necessary data、task、ratio、prompt、metrics 与阈值不变，
先运行 current-vs-projector-dominant 一个 paired root，任一门失败即拒绝且不换分配。

## 状态

`CONTINUE`
