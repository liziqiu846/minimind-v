# LITMAP-03 Evidence / Applicability Matrix

| Source | 模型、trainable / frozen modules | 干预与控制 | 有效证据 | 不能推出 / 本地限制 | Gate |
|---|---|---|---|---|---|
| Zhou et al., *An Empirical Study on PEFT for MLLMs*，Findings ACL 2024，`2406.05130v1` | LLaVA-1.5 7B/13B、ShareGPT4V、Qwen-VL-Chat；vision encoder 通常 frozen；四种 PEFT 作用于 LLM，connector 分别 full-tune/freeze | 同 base/task/data/epochs 下 connector tune-vs-freeze；附录另做 visual encoder tune-vs-freeze；main seed 42，稳定性子实验三 seed | connector tuning 对 unseen datasets 多数改善；visual encoder unfreeze 的四方法平均几乎不变或略差；直接证明 module choice 的效果不等同于总 PEFT 名称 | connector/encoder unfreeze 增加 trainable parameters，未做 fixed-count allocation；主 module 结果不是跨 seed；论文还做了 rank/location/LR 搜索 | `DIRECT_MECHANISM`，支持 projector-allocation candidate，但不证明方向 |
| Tong et al., Cambrian-1，NeurIPS 2024 Oral，`2406.16860v2` | Vicuna-1.5-7B + 23 vision encoders + connector；1.2M adapter data、737K instruction data | 各 encoder 的 frozen-vs-unfrozen；LLM、data 和训练 hyperparameters matched | unfreezing 对多数 general、OCR/chart、vision-centric benchmarks 有益；多种 encoder 重现；正式报告约 50–55% slowdown | full encoder unfreeze 同时增加大量 trainable parameters/compute；未报告 seed variance；与 ACL 2024 task-specific 结果冲突 | `DIRECT_MECHANISM`；给出 matched intervention control，支持 frozen-vs-trainable 竞争解释 |
| Ebrahimi et al., CROME，`2408.06610v1` | frozen EVA-CLIP 与 frozen Vicuna/Flan；train Q-Former/projections/CROME adapter；task-specific 阶段只训练 5.24M pre-LLM adapter | 相近 backbone/data 下 CROME adapter ablation 到 BLIVA；task-specific adapter-only 与重训 Q-Former baselines 比较 | autoregressive text-output MLLM 能在 frozen encoder+LLM 下仅靠 pre-LLM adapter 获得大幅 SQA/AI2D adaptation，直接支持“fixed encoder 可读、bridge capacity 可能足够” | adapter 新增参数；baseline 架构和参数量不完全 matched；规模 5.24M 远大于本地 4,096 coordinates | `DIRECT_MECHANISM`，projector-only 可行性的第二条独立 primary evidence |
| Zhou et al., CoVFT，CVPR 2026，`2603.21077v2` | LLaVA-1.5 7B/13B；LLM/projector train；vision 用 BitFit/VPT/SVPT/LoRA/full 或 CVE+CoMoE | Freeze、常见 VFT、image/text/context routing；Random@2/Uniform 控制额外 expert width | CoVFT 相对 Freeze 在 12 benchmarks 全部改善、平均 `+2.15%`；random/uniform 同宽控制失败，支持 context routing 而非仅更多 width | 引入 frozen BERT、cross-attention、多个 experts；选择 latter-half layers、routing 与默认超参；665K training，无法成为本地唯一最小干预 | `DIRECT_MECHANISM`，支持 routing competing explanation；`REJECT_FOR_LOCAL_BRIDGE` |
| Laurençon et al., *What matters when building VLMs?*，NeurIPS 2024，`2405.02246v1` | fully autoregressive 与 cross-attention VLM；frozen 或 LoRA-adapted pretrained backbones | 固定训练 data 的 architecture/freeze-LoRA ablation | fully autoregressive 模型由 frozen 到 LoRA 平均 `+12.9` points，而 cross-attention 仅 `+0.6`，说明 trainability 与架构交互 | LoRA 同时进入 unimodal backbones，不能隔离 vision/projector/language；两架构 token/parameter/compute 不匹配 | `DIRECT_ADJACENT` |
| Zhang et al., HyperLLaVA，`2403.13447v1` | LLaVA-style；动态 visual expert 作用于 projector，language expert 作用于 LLM | 去掉 visual/language expert 的 ablation；另选 expert insertion blocks | visual expert 与 language expert 分别贡献约 `2.61%`、`0.94%` mean improvement，表明两个模块的动态容量并非同义 | hypernetwork architecture replacement、额外参数、layer selection；不是 fixed-count allocation | `HEURISTIC_MECHANISM` |
| Xiao et al., PaLM2-VAdapter，`2402.10896v2` | frozen vision encoder 与大 LLM，108M tiny LM + perceiver adapter 逐阶段训练 | 相同 encoder/decoder 下 perceiver baseline、adapter architecture 与 progressive pretraining | connector 的结构与训练历史会显著改变收敛和 VQA/captioning performance | architecture、pretraining、steps 与参数均改变；包含大量 adapter design ablation，不能转成单一 4,096-coordinate test | `HEURISTIC_ONLY` |
| Cha et al., Honeybee，CVPR 2024，`2312.06742v2` | frozen vision encoder；pretrain projector，instruction-tune projector+LLM | linear/resampler/locality-aware projectors、visual-token count 与 data recipe ablations | projector 是否保留 local context 会影响 spatial benchmarks；参数更多的 resampler 仍可能更差 | projector architecture、token count、data mixture 与 schedule 多重选择；不是 module trainability control | `HEURISTIC_ONLY` |
| Huang et al., SPIDER / *Learn from Downstream*，`2411.10928v1` | LLaVA/VILA；主要在最后两个 LLM layers 按 pretrained magnitude 与 accumulated gradient 选择 elements | 50% random、magnitude、gradient、importance discrepancy masks 与 full FT | 说明相同模型内 parameter selection 会改变 source/target trade-off | 没有区分 vision/projector/language allocation；gradient 是 intervention rule 但仍属事后 task-dependent mask；本地复用会恢复被禁止的 proxy/layer route | `REJECT_FOR_VLM_BRIDGE` |
| Hu et al., TinyAlign，Findings ACL 2026，`2505.12884v2` | frozen vision tower；pretrain connector，instruction-tune LLM+connector；另加 RAG memory/connector | baseline vs RAG-enhanced connector；多个 KB/top-k ablations | 更丰富 pre-LLM context 可改善小 LLM 下游表现 | “effective mutual information” 不是标准理论对象；推导直接假定 retrieved captions 带来正 conditional MI 且降低 irreducible error，未证明；输入信息、架构和 compute 同时变化 | `REJECT_FOR_FORMAL_BRIDGE` |
| Wei et al., Pareto LoRA，`2606.17296v1` | Emu2 unified text/image generator；LoRA 作用于 60-layer LLM | text-loss/image-loss gradients 的 MGDA/rescaling；GradNorm、Step Balance、layer group 与 threshold ablation | 对真正双输出目标给出 objective gradient competition 的直接干预 | 本地 MiniMind-V 只有 image-input→text next-token loss，没有独立 image generation loss；还需选 layer group 和 `τ`，违反 no-sweep gate | `REJECT_FOR_OBJECTIVE_BRIDGE` |

## 跨文献判定

三篇相互独立的 autoregressive-LVLM primary sources 形成可用但不闭合的证据链：

1. ACL 2024：connector 是否训练会改变 unseen-task performance，而 full vision
   unfreeze 通常无益；
2. CROME：在 encoder 和 LLM 都 frozen 时，pre-LLM adapter-only 仍能完成强
   task-specific adaptation；
3. Cambrian-1：在相同 data/hyperparameters 下，full vision unfreeze 对多数
   vision-centric benchmarks 有益。

它们共同否定“module placement 可以忽略”，但对“应放在 encoder 还是 connector”
给出冲突方向，而且都没有固定 trainable parameter count。本地固定总 4,096
coordinates 的二条件实验因此增加新科学内容，而不是复述文献。

## 保留候选：PROJALLOC-01

### 机制

在 frozen vision encoder 已包含可读 rotation / spatial cues 的前提下，当前
`582/2327/1187` 分配仍把 1,769 coordinates 放在 vision 与 language targets；对于
visually necessary task，真正瓶颈可能是把 fixed visual features 转成 LLM 可用
tokens 的 projector subspace 容量。

### 唯一最小干预

- control：current allocation
  `vision=582/projector=2327/language=1187`；
- intervention：projector-dominant
  `vision=1/projector=4094/language=1`；
- 两者总计均为 4,096 coordinates；
- 相同 frozen base、11 targets、mapping root、data、pixels、labels、prompt、
  optimizer、steps、train seed 与 scorers；
- 使用 fresh roots，不补 VISSUP 禁止的 `43102/43103`，也不把结果用于翻转
  `VISSUP-01=REJECTED`。

若 projector-dominant 明显提高 held-out rotation 与 CV-Bench，则支持
trainable-subspace module allocation，并反对“frozen encoder 完全不可读取”是唯一
解释。若没有提高，则 `projector capacity` 在该严格 setting 下被否定；不得改为
vision-heavy、换比例或运行旧 9-point sweep。

### 尚未验证的 prediction

在尚未训练 projector-dominant 模型前预声明：

1. projector-dominant 相对 current allocation 的 held-out rotation accuracy
   至少提高 5 percentage points，95% paired-bootstrap CI lower `>0`，且绝对
   accuracy 至少 0.30；
2. 同一新模型在 CV-Bench-2D 的 image-group accuracy 至少提高 1 point，且
   gold-vs-distractor margin difference `>0`。

这同时给出 mechanism prediction 和新模型的 external performance prediction。
它不复用生成 NLL、no-pixel 或无桥 representation/gradient proxy。
