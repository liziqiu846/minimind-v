# XMC-01 Round 2 Theorem Applicability Matrix

## Gate

要通过本轮 gate，文献必须把以下三段以明确假设连接起来：

1. 图文联合分布中的任务相关方向；
2. 冻结 autoregressive LVLM 中唯一、无需事后选择的表示保持量；
3. 未见数据上的生成式语义风险方向。

只证明 contrastive retrieval、linear-probe classification、表示可识别性、优化偏置或
给定 metric 下的几何保持，均不能替代第 2→3 段。

## Primary-source audit

| Source | 正式对象与成立范围 | 下游对象 | 到 MiniMind-V 仍缺什么 | 唯一 statistic gate | 判定 |
|---|---|---|---|---|---|
| Zhang et al., ICML 2023, arXiv:2306.04272 | spectral MMCL 与归一化图文共现矩阵的 asymmetric factorization 等价；最优 dual-encoder 表示由 leading SVD directions 决定 | 冻结 encoder 的最优 linear-probe error bound；依赖 pair label error、谱和模型类复杂度 | MiniMind-V 没有用该 spectral contrastive loss 学习可分离的 image/text encoders；需新证明 adapter/AR decoder hidden states 保留同一算子并控制生成风险 | 定理固定的是最优 encoder output，且仅在线性 probe 下吸收非唯一旋转/缩放；没有固定 AR layer/pooling | **FAIL** |
| Daunhawer et al., ICLR 2023, arXiv:2303.09166 | 连续可逆生成机制、content invariance、style perturbation 与已知 content dimension 下，渐近 contrastive objective block-identify shared content | 表示 identifiability；无 downstream risk bound | 真实 captions/离散 tokens 不满足连续 diffeomorphic setup；MiniMind-V 不是该双编码器优化器；block-identifiability 不给模型间风险方向 | content dimension 本身需已知或估计，且 block 只确定到可逆变换 | **FAIL** |
| Dufumier et al., ICLR 2025, arXiv:2409.07402 | 在 oracle-like minimal label-preserving multimodal augmentation 与 expressive optimum 下，CoMM 的 fused contrastive representation 保持 redundant/unique/synergistic task information | 主要用 linear probes 验证信息项 | 需要任务变量和满足 \(I(X,X')=I(X,Y)\) 的 augmentation；不是现有 AR LVLM 训练目标，也没有生成风险桥 | augmentation、fusion representation 和下游 probe 都不是冻结 MiniMind-V 的唯一量 | **FAIL** |
| Cai et al., NeurIPS 2025, arXiv:2504.10143 | 连续 latent、diffeomorphic image/text generators 和 selection/perturbation bias 下，MMCL block-identify 未受偏语义 | identifiability 与经验 zero-shot F1；无 AR risk theorem | 需从 latent invariants 到离散生成风险、从 MMCL encoder 到 AR decoder 的两段新证明 | invariant subset/dimension 和 encoder output 属于理论生成模型，不给 MiniMind-V layer/pooling | **FAIL** |
| Baptista et al., arXiv:2505.24134 | 一般部分把 dual-encoder exponential tilting 解释为条件/联合分布；可解生成结果限于 centered multivariate Gaussian、linear encoders、特定 tilting/loss | retrieval、classification；“generative”指从诱导条件分布取样或 Gaussian conditional matching | 没有 next-token factorization、autoregressive decoder 或 held-out semantic risk；Gaussian optimal matrix不能由任意冻结 LVLM hidden states等同推出 | 一般理论不选 checkpoint statistic；Gaussian \(A=G^\top H\) 只在指定线性模型/loss 中唯一 | **FAIL** |
| Mehta & Harchaoui, arXiv:2507.09128 | 用 conditional-mean operator / information density 表达 CLIP 式 zero-shot indirect predictor；误差分为 prompt bias、residual dependence、estimation error | zero-shot regression/classification，另由 surrogate 转成 classification risk | 对象依赖 pretrain image-caption distribution、prompt distribution 与 CLIP-style score；没有 AR sequence loss或冻结 decoder 表示保持 theorem | kernel、conditional-mean/RN estimator、encoder realization均不唯一固定 MiniMind-V hidden statistic | **FAIL** |
| Yi et al., arXiv:2510.03268 | 在 MCL optimum、vMF/cone/hyperplane collapse 与 intra-modal isometry 下推导 modality gap、pair alignment 和 shared-subspace projection | CLIP retrieval / zero-shot classification；perfect alignment 是 pairwise ranking | 强几何假设不对应 AR LVLM；论文实验也显示 post-hoc SSP 未改善分类表现 | shared subspace 需估计，实践中又选择低维子空间以降噪；违反无 rank/subspace 选择 gate | **FAIL** |
| Yu et al., arXiv:2602.07026 | 对 dual-encoder embedding gap 给 fixed-frame mean/covariance 分解与几何恒等式；ReAlign/ReVision 是经验训练框架 | 经验 MLLM benchmark，无从几何量到风险的 theorem | frame 来自外部 dual encoders，非 AR decoder 的模型保持；训练效果不能证明冻结 checkpoint 排序 | PCA energy threshold、reference step、source encoder 与统计层均需选择 | **FAIL** |
| Lu et al., arXiv:2604.04496 | 给定满足三角不等式的 cost，Yoneda/Indra relational profile 在该 sample category 中 faithful/structure-preserving | 经验 cross-model/cross-modal matching；无 semantic risk guarantee | 定理保证的是“给定 cost 的关系完整性”，不是该 cost 与任务风险一致；不能把 angular profile 直接命名为泛化对象 | 内部 representation、angular cost、全部样本/landmarks 均需选择 | **FAIL** |
| Yang et al., ICML 2026, arXiv:2605.02116 | contrastive population risk 对 AUC-type positive-vs-negative retrieval ranking Fisher-consistent，并给 excess-risk calibration；有限负样本 generalization bound | contrastive retrieval AUC；附录仅在额外 idealized setup 讨论 zero-shot classification | 这是最强的 risk calibration，但 risk 明确是 contrastive ranking，不是 AR generated semantic risk；MiniMind-V checkpoint 未最小化该 objective | 定理固定 score 而非 AR hidden representation；不能从多个 layer/proxy 中唯一导出 score | **FAIL** |
| Dhinagar et al., arXiv:2605.08764 | 将 Davis–Kahan/Weyl/covariance concentration 组合为 recoverable eigendimension 与 truncated Mahalanobis heuristic | 低数据 supervised classification/AUC；class difference direction进入量中 | 多模态“stabilization”主要是经验解释；未证明该量控制 AR LVLM risk，且需标签方向 | empirical threshold \(\tau=0.1\)、class direction、SVD/rank 选择，不满足冻结唯一量 | **FAIL** |
| Shi et al., arXiv:2607.08194 | UFM + additive feature noise 下的 Taylor smoothing，以及 small-step noisy-flow stationary approximation，解释 low-rank alignment 的 flat/noise-robust偏置 | 论文明确称 theorem 是 mechanistic explanation、不是 quantitative bound；feature signatures 与 downstream gain 仅关联 | 没有从 flatness/linear separability/manifold geometry 到生成风险的保证；实验包含 operator/rank/layer/schedule 搜索 | linear probe token、angular coverage、manifold、rank/layer均非唯一；不能选一个事后评分 | **FAIL** |
| Rheude et al., arXiv:2607.17673 | Jacobian singular-value不等式与 gradient transport；主要因果证据来自 regularization/GPE intervention，不含 downstream-risk theorem | trimodal contrastive retrieval 与 linear probes | 对象是 modality encoder Jacobian，MiniMind-V transformer 已有 residual paths；未连接 AR generation | 输入层、encoder block、JVP directions、gain band均需指定；无唯一 frozen statistic | **FAIL** |

## 最强桥的逐段结论

### 最强“生成式”候选：arXiv:2505.24134

- 成立：对指定 dual-encoder tilting，contrastive population loss可解释为拟合两个
  conditional distributions；在线性高斯模型中可解析 conditional mean/covariance。
- 不成立：它没有证明 autoregressive \(p_\theta(y_{1:T}\mid x)\) 的 hidden
  representation retention，也没有把任意表示距离连接到 held-out semantic risk。
- 所需新证明不是技术性补丁，而是本 gate 的核心缺口。

### 最强“风险 calibration”候选：arXiv:2605.02116

- 成立：contrastive excess risk控制同一 positive/negative distribution 定义的
  AUC-type retrieval excess risk。
- 不成立：MiniMind-V 的 next-token objective、sequence semantic risk 和任意中间
  layer statistic都不属于该定理对象。
- 把 retrieval score 换成 hidden-state相似度会重新引入未预注册 proxy。

### 最强“生成式 LVLM 机制”候选：arXiv:2607.08194

- 成立：在理想化 UFM 与噪声动力学下给出 low-rank update 的方向偏置解释。
- 作者边界：不是 quantitative bound；表示 signature 与 downstream gain 是
  associational evidence。
- 因而可启发将来训练 intervention，但不能授权本轮 frozen-checkpoint scoring。

## Decision

13 篇完整 primary-source/appendix 核查中，没有一篇同时固定：

1. autoregressive LVLM 的表示对象；
2. 唯一 layer/pooling/kernel/rank-free statistic；
3. statistic 到未见语义生成风险的方向保证。

继续评分只能在 CKA/CCA/HSIC、token probe、Jacobian、spectral energy、Indra profile
等多个经验 proxy 中事后选择，直接触发 immutable plan 的否定标准 1–3。因此
`XMC-01` model-retention bridge 判定为 `REJECT_IDEA`。这不否定上述论文在其各自
contrastive / classification / optimization 对象上的定理，只否定把它们无新证明地
迁移成当前 MiniMind-V prediction test。
