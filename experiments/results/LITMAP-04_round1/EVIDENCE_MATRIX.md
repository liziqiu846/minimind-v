# LITMAP-04 Evidence / Applicability Matrix

本表按 frozen plan 核查 14 篇决定性 primary sources。`DIRECT_MECHANISM` 表示论文
直接干预 autoregressive LVLM/MLLM 的训练机制，不表示该干预自动满足本项目的
no-sweep、单因素和资源门。预印本状态按 2026-08-07 检索时可核查版本记录。

## 1. CoMMIT

- **Source**: Wu et al., *CoMMIT: Coordinated Instruction Tuning for Multimodal
  Large Language Models*, arXiv `2407.20454v2` (2024 preprint).
- **Model / modules**: autoregressive vision/audio MLLMs；feature encoder 与 LLM
  都参与协调更新；4×A100，论文报告约 8 小时。
- **Objective / intervention**: 根据相邻更新的 generation distributions 估计
  learning-balance coefficient，为不同 component 动态设 learning rate，并加入
  auxiliary distribution-change regularizer。
- **Control / replication**: 多 backbone、vision/audio downstream tasks；与固定
  learning rate、coordinate descent 等比较。没有固定总 update coordinates，也没有
  current-task mechanism 与独立 external-transfer 的配对控制；未报告本项目所需的
  seed-level held-out effect。
- **Mechanism + performance evidence**: component gradient / distribution dynamics
  与 downstream performance 同时变化，支持“训练不平衡可由 objective-level update
  改变”，但不能排除 scheduler 与 auxiliary loss 的组合贡献。
- **Theory**: 非凸 Adam-style convergence 分析依赖 Lipschitz/smoothness、bounded
  gradients 与 descent-direction assumptions；认证对象是 optimization convergence，
  不是 unseen semantic risk，也不证明 balance coefficient 是泛化量。
- **Cannot imply**: 当前 MiniMind-V 的 projector/frozen-feature mismatch、held-out
  rotation failure 或 CV-Bench transfer 由 gradient competition 导致。
- **Local test / cost**: 需要 component-specific LR、额外 forward estimates、
  auxiliary loss 及其权重；不是唯一单因素 intervention，且明显超过现有 paired SFT
  pilot 的实现与资源等级。
- **Gate**: `DIRECT_MECHANISM; REJECT_FOR_LOCAL_BRIDGE`.

## 2. MoReS / LLaVA Steering

- **Source**: Bi et al., *Visual Instruction Tuning with 500x Fewer Parameters
  through Modality Linear Representation-Steering*, arXiv `2412.12359v2`
  (2024 preprint).
- **Model / modules**: LLaVA-style autoregressive MLLMs，3B/7B/13B；LLM frozen，
  在多个 transformer layers 对 visual-token subspace 加 linear steering。
- **Objective / intervention**: 用 Layer-wise Modality Attention Ratio (LMAR) 描述
  text-dominant attention，并训练低秩 visual representation steering。
- **Control / replication**: 与 full FT、LoRA、Adapter、IA3 比较，多 task/scale；
  论文实验选择 visual-token ratio、subspace rank、steering layers 与插入位置。
- **Mechanism + performance evidence**: LMAR 与 benchmark performance 同时改善，
  但 LMAR 是解释性 attention proxy；architecture/parameterization 与训练方法同时
  改变，不能把 performance gain 唯一归因于 modality balance。
- **Theory**: 无连接 LMAR 到 held-out semantic risk 的正式 theorem。
- **Cannot imply**: attention mass 等价于任务相关视觉信息，或当前低维
  MiniMind-V 应选择某个 layer/rank。
- **Local test / cost**: 必须新增 layerwise modules，并选择 layer/rank/token ratio；
  违反 `XMC-01` proxy/layer/rank 禁令与 LITMAP-04 no-sweep 门。
- **Gate**: `DIRECT_MECHANISM; REJECT_FOR_BRIDGE`.

## 3. Decoupled Proxy Alignment (DPA)

- **Source**: *Decoupled Proxy Alignment: Mitigating Language Prior Conflict for
  Multimodal Alignment in MLLM*, arXiv `2509.14735v1` (2025 preprint).
- **Model / modules**: Qwen2.5/Llama/Gemma-based autoregressive MLLMs，
  1.5B–32B；proxy LLM、connector 与原 LLM 分三阶段训练。
- **Objective / intervention**: 先 text-only 适配 proxy LLM，再冻结 proxy 做
  multimodal pretraining；以 image-present vs text-only token probability difference
  动态加权 caption tokens。
- **Control / replication**: component ablation、不同 backbone/scale/data fraction；
  需要 LoRA rank、clamp lower/upper bounds、pretrain+instruction stages；小数据下
  DPA 反而更差。
- **Mechanism + performance evidence**: word-level visual/linguistic loss 与
  vision-centric benchmark 同时改善；但 proxy preparation、token reweighting 和
  三阶段 schedule 共同变化。
- **Theory**: 无 held-out-risk theorem。
- **Cannot imply**: image-present vs text-only score 是正式视觉信息量，或当前
  `VISCOND-01` 构念失败可以通过训练时复用同类 proxy 得到规避。
- **Local test / cost**: 需要 proxy model、额外 training stage、token weighting
  bounds/rank 与足够数据；复用已失败 no-image-style operational proxy。
- **Gate**: `DIRECT_MECHANISM; REJECT_FOR_BRIDGE`.

## 4. Fine-tuning MLLMs Without Forgetting

- **Source**: *Fine-tuning MLLMs Without Forgetting Is Easier Than You Think*,
  arXiv `2603.14493v1` (2026 preprint).
- **Model / modules**: Qwen2.5-VL-3B/7B、LLaVA-1.5-7B；主要冻结 vision/projector，
  full 或 LoRA 更新 language backbone。
- **Objective / intervention**: 2×2 text-distribution × image-distribution
  evaluation；对 ImageNet-VQA task-template overfitting 加入 OCR-VQA、
  LLaVA-665K 等 task-diverse hybrid data。
- **Control / replication**: 相同 base 与主任务；dataset type 在 50% mix 比较，
  LLaVA mixture ratio 从 0% 到 70% 扫描；跨模型、领域与数据 regime。
- **Mechanism + performance evidence**: class-label distractor 直接暴露
  instruction ignoring；diverse-text mixture 改善 OOD-text/ID-image transfer 且
  主任务损失小，支持 task-specific absorption/overfitting。
- **Theory**: 经验机制研究，无泛化 theorem。
- **Cannot imply**: VISSUP rotation signal 已被吸收但未 transfer；论文 failure 是
  已学会主任务模板，而本地 rotation accuracy 仍近 chance。
- **Local test / cost**: 必须选择 auxiliary dataset 与 mixture ratio；会更改
  VISSUP data ratio，并需要数据-mixture sweep，违反冻结约束。
- **Gate**: `DIRECT_MECHANISM; REJECT_FOR_LOCAL_BRIDGE`.

## 5. DV-SFT

- **Source**: Zhao et al., *DV-SFT: Direct Vision Supervision for Fine-Grained
  Visual Understanding*, arXiv `2605.26656v1` (2026 preprint).
- **Model / modules**: Qwen3-VL-2B/8B 与 Qwen3-1.7B autoregressive models；
  vision encoder frozen；2B full tune、8B LoRA。
- **Objective / intervention**: OCR-derived word labels directly supervise visual
  tokens with the same vocabulary objective；vision smoothing spreads patch labels。
- **Control / replication**: standard SFT、BASIC、vision-loss and smoothing
  ablations；2×A100；one epoch/final checkpoint。未报告 seed-level replication。
- **Mechanism + performance evidence**: OCR in-domain、4 个 OCR OOD benchmarks、
  non-contextual OCR 与 MME 同时评估；direct labels improve OCR，MME 仅很小变化。
  Loss-weight ablation 明确显示过大 vision weight 有害。
- **Theory**: 无正式 theorem；visual logits/labels 是任务构造，不是风险证书。
- **Cannot imply**: OCR patch-word correspondence 可用于自然图像 rotation 或
  CV-Bench；也不能把微小 general-task gain 外推为通用视觉泛化规律。
- **Local test / cost**: 需要构造 token labels、vision smoothing，并选择 vision
  loss weight；当前 rotation data 没有合法 patch labels，违反 no-weight/task sweep。
- **Gate**: `DIRECT_MECHANISM; REJECT_FOR_LOCAL_BRIDGE`.

## 6. Visual-shortcut RLVR dynamics

- **Source**: Xu, *When Does a Video–Language Model Stop Watching? Reward Strength
  Controls the Formation and Reversal of Visual Shortcuts in Multimodal RLVR*,
  arXiv `2606.22043v1` (2026 preprint).
- **Model / modules**: 单一 Qwen3-VL-8B video-language policy；RLVR。
- **Objective / intervention**: grounding-penalty strength 与 intervention timing；
  OOD frame-shuffle invariance proxy 追踪 shortcut onset。
- **Control / replication**: onset 用两个 seeds；reward dose 与 before/at/after timing
  控制；固定 intervention steps。dose–response 依赖多个 penalty strengths。
- **Mechanism + performance evidence**: OOD proxy、accuracy、dose 与 timing 形成
  清晰 dynamics；representation probe 落在 bootstrap variability 内，仅探索性。
- **Theory**: 无正式 theorem；“hysteresis-like”明确只是类比，未执行双向 dose sweep。
- **Cannot imply**: 单一 video RLVR onset 可迁移到 caption/SFT MiniMind-V，
  frame-shuffle invariance 也不是本项目正式视觉风险。
- **Local test / cost**: 需要 RLVR、reward strength sweep、checkpoint trajectory 与
  proxy；不适用于已冻结 SFT pilot。
- **Gate**: `DIRECT_MECHANISM; REJECT_FOR_BRIDGE`.

## 7. VIGIL

- **Source**: Xiao et al., *Staying VIGILant: Mitigating Visual Laziness via
  Counterfactual Visual Alignment in MLLMs*, arXiv `2606.26387v1`
  (2026 preprint).
- **Model / modules**: Qwen2.5-VL-7B/72B、LLaVA-OneVision-7B、
  InternVL2.5-26B；offline DPO/full fine-tuning。
- **Objective / intervention**: policy/reference 都在 matched seeing 与
  attention-masked blind states 下评分；hard negatives、counterfactual visual
  decoupling 和 dynamic gating 联合训练。
- **Control / replication**: 同 preference pool 对 DPO/SimPO/HA-DPO/DA-DPO；
  component ablation、blind-state variants、data fraction、KL/weight curves；
  附录只对 text-only retention 明确提到三 seeds。
- **Mechanism + performance evidence**: visual-anchor ablation、high visual-dependency
  bucket、POPE/AMBER/MathVista/MMBench/RefCOCOg 与 text-only maintenance；但 hard
  negatives、blind contrast、gating 与 preference data composition 同时参与。
- **Theory**: 文中把 objective 描述为 maximizing MI / causal grounding，但没有
  证明 attention-masked likelihood contrast 等于 mutual information，也没有
  held-out-risk theorem；必须按经验 counterfactual objective 解读。
- **Cannot imply**: `VISCOND-01` 的 no-pixel proxy 是正式信息量，或 blind attention
  masking 在 MiniMind-V SFT 中能单因素改善。
- **Local test / cost**: 7B DPO 需 preference/reference model、大 batch 与 A100；
  另需 hard negatives、gating、KL/weight choices，并复用 seeing/blind proxy family。
- **Gate**: `DIRECT_MECHANISM; REJECT_FOR_BRIDGE`.

## 8. OPD-V

- **Source**: Bi et al., *OPD-V: Visual On-Policy Self-Distillation with Modality
  Balance*, arXiv `2608.05131v2` (2026 preprint).
- **Model / modules**: Qwen3.5-4B/9B、Qwen3-VL-4B/8B；student、EMA positive teacher
  与 negative teacher；4×H200。
- **Objective / intervention**: student original image rollout；positive teacher 用
  evidence-centered zoom crop，negative teacher 用 mask crop；positive logit margin
  选 trust-region tokens，再做 margin-weighted top-100 JSD distillation。
- **Control / replication**: 同 6.2K data 的 SFT/GRPO/OPSD/Vision-OPD/VA-OPD；
  positive/negative teacher 与 image-operation ablations，4 backbones、6 benchmarks。
  正文未给跨 seed variance；zoom/mask 是多种操作中最优组合。
- **Mechanism + performance evidence**: attention ratio、trust-region fraction、
  entropy/response length 与 6-benchmark performance 同时报告；component ablation
  支持两个 teacher 互补，但不能隔离 crop、mask、token selection、margin weighting
  与 JSD 的单独作用。
- **Theory**: 无泛化 theorem；attention ratio/logit margin 是经验操作性量。
- **Cannot imply**: attention/logit balance 是正式视觉信息或因果中介；也不能推断
  low-dimensional SFT 会复现 on-policy distillation gain。
- **Local test / cost**: 8 rollouts/prompt、EMA 双 teacher、bbox crops、mask、
  top-K JSD 和 4×H200，远超本地单因素/资源门，并需要 operation selection。
- **Gate**: `DIRECT_MECHANISM; REJECT_FOR_LOCAL_BRIDGE`.

## 9. ROSS

- **Source**: Wang et al., *ROSS: Reconstructive Visual Instruction Tuning*,
  ICLR 2025, arXiv `2410.09575v2`.
- **Model / modules**: LLaVA-style autoregressive LMM；额外 visual tokenizer、
  post-projector 与 denoising network。
- **Objective / intervention**: text next-token loss 加 latent visual-token denoising；
  比较 pixels、VAE/VQGAN/DINO-style targets、regression/denoising/generation。
- **Control / replication**: 同类 training baseline 与 rich target/objective
  ablations，多 encoder/LLM/benchmarks；architecture、parameters 与 compute 增加。
- **Mechanism + performance evidence**: latent denoising 优于 raw regression，
  attention 与外部 comprehension/hallucination benchmarks 改善，另有 depth-map
  transfer；不支持“任意 auxiliary visual loss 都有效”。
- **Theory**: 无 held-out-risk theorem。
- **Cannot imply**: 当前 MiniMind rotation signal 可由一个简单 auxiliary term
  吸收，或 attention improvement 是机制证书。
- **Local test / cost**: 必须选择 tokenizer/target/objective 并新增 denoiser；
  不是单一最小干预。
- **Gate**: `DIRECT_MECHANISM; REJECT_FOR_LOCAL_BRIDGE`.

## 10. ASVR

- **Source**: Wang et al., *Autoregressive Semantic Visual Reconstruction*,
  arXiv `2506.09040v2` (2025 preprint).
- **Model / modules**: LLaVA-like autoregressive LVLM；pretrained semantic visual
  tokenizer，visual-token output head/sequence。
- **Objective / intervention**: 与 text next-token 同构地预测 discrete semantic
  visual tokens；semantic-vs-appearance reconstruction 形成 competing target。
- **Control / replication**: 多 backbone/benchmark；semantic target 改善而
  appearance-only 可低于 baseline。未报告 seed-level effect，新增 tokenizer/head/
  output tokens 与 compute。
- **Mechanism + performance evidence**: 直接 target 和外部 VQA/vision-centric/
  hallucination/OCR 同向，支持 target semantics 重要而非“有额外 loss”本身。
- **Theory**: 无正式 generalization theorem。
- **Cannot imply**: 当前 frozen visual feature 含有 rotation 可识别结构，或
  MiniMind 可在 4,096 coordinates 内实现相同 visual-token generator。
- **Local test / cost**: 需要 semantic tokenizer、output head 与 loss balance；
  无唯一低成本 instantiation。
- **Gate**: `DIRECT_MECHANISM; REJECT_FOR_LOCAL_BRIDGE`.

## 11. JARVIS

- **Source**: Caffagni et al., *JARVIS*, arXiv `2512.15885v1`
  (2025 preprint).
- **Model / modules**: LLaVA alignment stage；JEPA-style target encoder/predictor，
  masked latent visual prediction。
- **Objective / intervention**: masked prediction 与 unmasked whole-image alignment
  直接对照，训练 projector/adapter 使 visual tokens 预测 latent target。
- **Control / replication**: 多 LLM/backbone；masked target 优于 unmasked；
  target LLM layer/representation 由实验选择，作者承认无 principled criterion。
- **Mechanism + performance evidence**: in-training latent objective 与外部 tasks
  同向，但 target layer 与 extra components 是必要设计选择。
- **Theory**: 无冻结-feature到风险的正式 bridge。
- **Cannot imply**: 事后最佳 layer 可合法迁移到 MiniMind-V。
- **Local test / cost**: 需要 target encoder/predictor、mask schedule、target layer；
  违反 layer/no-sweep gate。
- **Gate**: `DIRECT_MECHANISM; REJECT_FOR_BRIDGE`.

## 12. LaVer

- **Source**: Li et al., *Unleashing the Intrinsic Visual Representation Capability
  of Multimodal Large Language Models* (LaVer), arXiv `2512.06281v1`
  (2025 preprint).
- **Model / modules**: autoregressive LMM；EMA teacher、masked image modeling 与
  global alignment components。
- **Objective / intervention**: latent visual reconstruction/alignment 作为
  text supervision 的辅助目标。
- **Control / replication**: 多 encoder/backbone 与 component ablations；最终方法
  同时包含多个 loss/component 与选择，未形成单因素配对。
- **Mechanism + performance evidence**: visual representation supervision 与
  downstream visual tasks 同向；不能唯一定位到 masking、teacher 或 alignment。
- **Theory**: 无 held-out-risk theorem。
- **Cannot imply**: frozen feature/objective mismatch 是 VISSUP failure 的唯一解释。
- **Local test / cost**: EMA teacher、masking、alignment loss 和 loss weights 超出
  唯一最小干预。
- **Gate**: `DIRECT_MECHANISM; REJECT_FOR_LOCAL_BRIDGE`.

## 13. V-GIFT

- **Source**: Sirko-Galouchenko et al., *V-GIFT*, arXiv `2604.12966v1`
  (2026 preprint).
- **Model / modules**: LLaVA-style autoregressive MLLMs，full/LoRA、多 backbone；
  无额外 decoder/head。
- **Objective / intervention**: 把 rotation/color/correspondence SSL 改写成 standard
  autoregressive visual-necessary instructions，3–10% mix。
- **Control / replication**: matched extra iterations、same-image reuse、
  single-image views、三 seeds、多 backbone；作者仍探索 task family 与 injection
  ratio。
- **Mechanism + performance evidence**: vision-centric external benchmarks 和
  attention/TVI 同向；TVI/attention 仅解释性。该论文曾是无需额外 component 的最强
  local candidate。
- **Theory**: 无证明 visual-necessary mix 到 unseen risk 的 theorem。
- **Cannot imply**: 7B/LoRA positive 可迁移到 4,096-coordinate MiniMind-V。
- **Local evidence**: 已由 `VISSUP-01` root `43101` 直接运行最小 paired
  instantiation；held-out rotation 与 CV-Bench accuracy 均未改善，状态为
  `INSTANTIATION_REJECTED`。不得换 task/ratio/prompt 或补 roots。
- **Gate**: `DIRECT_MECHANISM; REJECT_BY_LOCAL_INSTANTIATION`.

## 14. Pareto LoRA

- **Source**: Wei et al., *Pareto LoRA: Mitigating Modality Imbalance in Unified
  Multimodal Models via Pareto-Optimal Gradient Integration*, arXiv
  `2606.17296v1` (2026 preprint).
- **Model / modules**: Emu2 37B unified autoregressive text-image generator；
  vision encoder/decoder frozen，LoRA updates LLM/projections。
- **Objective / intervention**: 分离 text-generation 与 image-generation losses，
  按 cosine conflict 用 MGDA convex combination，按 magnitude ratio 和 threshold
  rescale gradients；选择 layer groups。
- **Control / replication**: vanilla LoRA、GradNorm/Step Balance、task/layer/
  threshold ablations；主要对象是 interleaved generation，不是 image-input→text-only
  MLLM。
- **Mechanism + performance evidence**: modality-specific gradient ratio 与 image
  quality/text performance 同时变化。
- **Theory**: MGDA 在两个明确定义 objectives 下给 common descent direction；认证
  optimization direction，不是 held-out semantic risk。
- **Cannot imply**: 本地单一 text-output next-token loss 可合法分成独立
  text/image objectives；visual input tokens 没有独立 generation loss。
- **Local test / cost**: 需要不存在于 MiniMind-V 的 image-generation objective，
  且要选 layer group 与 imbalance threshold。
- **Gate**: `FORMAL_ADJACENT; REJECT_FOR_OBJECTIVE_BRIDGE`.

## 跨文献判定

1. 至少两篇独立 direct autoregressive-LVLM sources 的门本身满足：CoMMIT、
   ROSS/ASVR/DV-SFT、VIGIL、OPD-V 等都直接干预训练。
2. 至少一个 matched mechanism control 和 mechanism/external joint evidence 也在
   公开研究中出现。
3. 但没有任何路线同时满足本项目其余接受门：
   - gradient routing 路线需要 component LR、extra forward/auxiliary objective，
     或依赖不存在的 image-generation loss；
   - visual-credit 路线需要 tokenizer/head/EMA teacher/DPO/OPSD/bbox/preference
     data 与 loss-weight/component choices；
   - seeing/blind 路线复用已失败的视觉 ablation proxy family，且没有 MI/causal-risk
     theorem；
   - task-specific absorption 路线需改变 data mixture 并搜索 ratio，而本地
     VISSUP 连 held-out mechanism 都未学会；
   - 唯一原本无需额外 component 的 V-GIFT local instantiation 已由
     `VISSUP-01` 有效否定。
4. 因此不能唯一预注册一个只改变主要因素、区分至少两个 competing explanations、
   同时提供新 mechanism + external prediction 且无需 sweep 的本地二条件实验。

最终 gate：

\[
\boxed{\text{NO\_CANDIDATE}}
\]

这只否定当前 `LITMAP-04` 文献到本地最小干预的 bridge；不否定 objective
competition、gradient routing、task-specific absorption 或 frozen-feature/objective
mismatch 这些上位机制。
