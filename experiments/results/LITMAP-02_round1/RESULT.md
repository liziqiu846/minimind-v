# LITMAP-02 Round 1 Result

## 当前科学问题

在三条冻结 checkpoint prediction route 均失败后，是否存在一个以训练时跨模态监督
信息为核心、能由最小受控干预区分竞争解释的 VLM 泛化机制？

## 假设

若 caption-only next-token training 系统性遗漏无法由文字表达的视觉结构，则直接或
隐式的视觉自监督应在生成式 LVLM 中跨方法改善 vision-centric 泛化；其中至少一条
路线应能排除额外 compute/数据规模，并适配 MiniMind-V 的最小二条件训练。

## 本轮实验

执行三组定向 arXiv/OpenAlex 检索，保存 568 records / 532 unique titles，并全文核查
6 篇决定性 primary sources。随后只读核查 10k train parquet、Stage 2 训练代码、历史
runtime 和官方 CV-Bench 可达性；没有训练、没有读取 final confirmation。

## 判定标准

- 支持：直接生成式 LVLM 受控证据或正式理论+生成验证；唯一 mechanism-specific
  intervention；可排除至少一个简单 baseline；本地可作最小 paired pilot。
- 否定：仅 CLIP/分类、复用失败 proxy、只增加 loss/data/compute、需要 sweep 或
  无未来方向性 prediction。
- 无法判断：决定性全文缺失、竞争解释不能区分或所需资源越界。

## 执行结果

- CVPR 2025 *Words or Vision* 的 Theorem A.5 为 text/multimodal mixture 的
  bounded-loss ERM risk decomposition，说明数据域不平衡可进入两域风险，但不直接
  证明任何具体视觉 instruction。
- ICLR 2025 ROSS 与三个独立新预印本 ASVR、JARVIS、LaVer 一致显示：视觉 latent /
  semantic target 可改善生成式 LVLM 的 vision-centric 任务；raw appearance、
  unmasked global alignment 或错误 loss 不能稳定替代，说明不是任意 auxiliary loss。
- V-GIFT 直接把 rotation/color/correspondence 写成标准 autoregressive instruction；
  跨三个 backbone、full/LoRA 和三 seed 的平均 vision-centric score 为正。matched
  extra-iteration control 无收益，single-image views 仍有收益，排除了“只因多 compute”
  和“只因增加图像规模”。
- JARVIS 需要事后选 LLM layer；LaVer/ROSS/ASVR 引入多个新 head/loss/component；
  按冻结门均不作为本地首测。
- 唯一通过本地门的是 `VISSUP-01`：固定约 10% rotation instruction，和
  label-revealed、等 pixels/labels/steps 的 control 配对。现有 checkpoint 没有该
  intervention，checkpoint-only test 不足；历史单训练约 715 秒，资源合法。
- 官方 CV-Bench 公开、非 gated，可为尚未训练模型提供未查看的外部 prediction；
  MMStar 只作次要 continuity check，不能用于 rescue `VISCOND-01`。

## 结论

`LITMAP-02` 支持登记一个新的 `VISSUP-01` candidate，但证据只足以进入
mechanism-intervention plan：训练时“任务是否必须看图”比再造冻结输出 proxy 更直接，
且有 matched-compute 文献控制与本地可执行设计；尚未证明它适用于低维 MiniMind-V，
也未形成科学规律。

## 下一步

创建并 commit `VISSUP-01_round1` immutable plan：先构造相同 rotated pixels 与
label distribution 的 visual-necessary / label-revealed 两条件，固定一个 paired
mapping-root pilot；只有机制量和预注册外部方向同时为正，才补至 total 3 pairs。

## 状态

`CONTINUE`
