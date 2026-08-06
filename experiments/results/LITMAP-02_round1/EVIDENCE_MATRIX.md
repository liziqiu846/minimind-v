# LITMAP-02 Evidence / Applicability Matrix

| Source | 正式对象 / 实验对象 | 对本项目的有效证据 | 不能推出 | Gate |
|---|---|---|---|---|
| Deng et al., *Words or Vision*，CVPR 2025 | 十个 VLM 的冲突文本视觉任务；1,000-sample SFT；Theorem A.5 对 text / multimodal i.i.d. mixture、bounded Lipschitz loss、ERM 和 covering number 给出两域风险分解 | text 数据远多于 multimodal 数据时，cross-modal error 项可使两域风险不对称；固定总 SFT 样本的实证表明 mixture composition 会改变 text bias | 不证明 visually necessary SSL 优于普通 multimodal data；不证明 caption-only MiniMind-V 风险；其 corruption task 不是本项目总体风险 | `FORMAL_ADJACENT + EMPIRICAL_SUPPORT` |
| Wang et al., ROSS，ICLR 2025 | LLaVA-style generative LMM；额外 latent visual tokenizer/denoiser；同训练数据与主架构比较 text-only visual instruction baseline | 直接视觉输出监督能在多视觉 encoder / LLM 上改善 fine-grained comprehension；latent/denoising 优于 raw RGB regression，反对“任意 auxiliary loss 都一样” | 增加了 denoiser、参数和目标；不能隔离 data instruction necessity，也不适合当前最小代码改动 | `ALGORITHMIC_EVIDENCE`，支持共同机制，不选作本地 intervention |
| Wang et al., ASVR，arXiv `2506.09040v2` | 视觉 semantic/appearance tokenizer、visual head、autoregressive visual target；LLaVA 558K–2M、多个 backbone | semantic reconstruction 平均改善而 appearance-only 低于 baseline；这是 mechanism-specific competing target | 未报告跨 seed 方差；新增 tokenizer/head/compute；不能直接证明 semantic target 因果链 | `EMPIRICAL_MECHANISM`，支持但不直接运行 |
| Caffagni et al., JARVIS，arXiv `2512.15885v1` | LLaVA alignment stage 中 JEPA masked latent prediction；对照 unmasked whole-image alignment；多个 LLM | masked prediction 优于相同架构的 unmasked alignment，说明视觉目标的结构而非“有额外 loss”本身重要 | 最佳 LLM layer 由实证选择且作者承认缺 principled criterion；本地采用会违反 no layer sweep | `EMPIRICAL_MECHANISM`，本地 gate 否定 |
| Li et al., LaVer，arXiv `2512.06281v1` | EMA teacher、masked image modeling、global alignment；多 encoder/backbone | 直接视觉 latent supervision 与视觉任务改善跨模型出现 | intervention 含多个 loss/component 和选择；无法在二条件最小实验中唯一归因 | `EMPIRICAL_MECHANISM`，本地 gate 否定 |
| Sirko-Galouchenko et al., V-GIFT，arXiv `2604.12966v1` | rotation/color/correspondence 被改写为 standard autoregressive instructions；3–10% mix；full/LoRA、多 backbone、三 seed | matched extra-iteration control 无收益；同图复用与 single-image views 仍有收益；mix during instruction tuning 才有效；最直接支持“必须看图的 supervision”而非额外 compute/新图规模 | 最新预印本；ratio/task family 做过选择；attention/TVI 是解释性分析；未给 seed 方差，MMStar 单项效应小 | `DIRECT_ALGORITHMIC_EVIDENCE`；唯一通过本地最小干预门 |
| OGM-GE / modality competition family | 多模态分类器的 on-the-fly gradient modulation | 支持 modality competition 可以由优化产生 | 不是 autoregressive LVLM，且会恢复已禁止的 gradient proxy 路线 | `REJECT_FOR_GENERATIVE_BRIDGE` |

## 保留候选：VISSUP-01

### 机制

caption-only next-token 目标允许模型用语言统计完成大部分监督；在 instruction mix 中
加入少量“答案无法从文本获得”的视觉自监督任务，可能使相同低维训练坐标吸收可迁移
的视觉结构，而不是只拟合 caption language prior。

### 为什么不是失败 idea 的改名

- 不复用 `COMP-01` caption counterfactual NLL；
- 不计算 `VISCOND-01` correct-vs-no-pixel 差；
- 不选择 `XMC-01` 的 layer/kernel/representation proxy；
- intervention 发生在训练数据监督关系，主比较是未来模型在新外部 panel 上的
  性能，不是旧 checkpoint 的事后相关性；
- control 与 intervention 将固定相同 rotated pixels、rotation labels、target
  token distribution、样本数、optimizer steps 和模型结构；唯一主要差异是文本是否
  泄露答案、从而任务是否必须使用视觉。

### 未解决竞争解释

visually necessary condition 比 label-revealed control 更难，因此 positive 仍可能部分
来自 hard-example training，而不是一般“视觉信息”规律。本轮最多只能得到
`PROMISING`，不能宣称正式理论；若 paired pilot 不改变 held-out rotation 能力或外部
vision-centric performance，直接拒绝，不调 ratio/task/prompt。
