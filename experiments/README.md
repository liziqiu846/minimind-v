# MiniMind-V Stage 1 最终归档

本目录保存大规模 Stage 2 开始前的最终实验状态。Stage 1 的核心问题是：在冻结
SigLIP 视觉编码器和 MiniMind 语言模型后，能否只编码一小段新学习到的图文适配信息，
并为同分布新图文样本上的条件文本预测给出非空洞泛化保证。

早期的全参数冻结策略比较、普通高维 4-bit 量化和重复结果摘要已经从主展示路径移除。
用于冻结协议溯源的 Phase 1 选择证据仍然保留，不能修改或删除，否则会破坏既有协议哈希。

## 最终方法

最终模型仅训练视觉投影器中的 4096 个哈希子空间坐标：

```text
图片
  -> 冻结的 SigLIP
  -> 4096 维可训练视觉投影适配器
  -> 冻结的 MiniMind
  -> 条件文本预测
```

坐标经过 3-bit 量化和 zlib 压缩，风险使用量化后重新解码的模型计算。泛化证书由
平滑训练风险和实际描述长度共同确定；正确图像、配对错图和无图像条件用于诊断模型
是否真正利用视觉信息。

## 冻结 Phase 2 证书

完整流水线入口：

```bash
python experiments/run_phase2_certificate.py --device cuda:0
```

它依次执行：

```text
冻结数据构造
  -> 子空间训练
  -> 3-bit 量化与压缩
  -> 解码模型风险评估
  -> 泛化界计算
  -> 公开证书包构建与验证
```

冻结配置及实现：

- `phase2_protocol.json`：正式协议及文件、资产哈希；
- `phase2_decoder_registry.json`：预声明解码器；
- `phase2_environment.json`：运行环境回执；
- `run_phase2_certificate.py`：端到端执行入口；
- `build_public_bundle.py` / `verify_public_bundle.py`：公开包构建与复核。

最终公开证书包位于 `results/phase2_bundle/`，核心结果为：

| 指标 | 结果 |
|---|---:|
| 描述长度 | 9144 bits（约 1.1 KB） |
| 平滑训练风险 | 4.87854 bits/token |
| 复杂度惩罚 | 7.12984 bits/token |
| 泛化上界 | 12.00838 bits/token |
| 随机猜测基线 | 12.64386 bits/token |
| 非空洞余量 | 0.63548 bits/token |

该结果只认证冻结基础视觉与语言模型后新增的图文适配信息，不表示整个视觉语言模型只需
1.1 KB，也不证明对分布外数据的泛化。

## 核心代码

- `build_bound_dataset.py`：构造并验证冻结数据划分；
- `quantize_subspace.py`：子空间坐标量化、压缩与解码；
- `evaluate_smoothed_risk.py`：训练/验证风险与视觉条件诊断；
- `compute_bound_report.py`：根据风险和实际描述长度计算证书；
- `generalization_bound.py`：泛化界公式；
- `phase2_protocol.py`：冻结协议加载及完整性检查；
- `model/subspace_projector.py`：4096 维视觉投影子空间；
- `trainer/train_pretrain_vlm.py`：正式训练入口。

`quantize_checkpoint.py` 虽源自早期高维量化实验，但仍提供最终子空间 codec 使用的公共函数，
并被冻结协议按 SHA256 登记，因此作为兼容性依赖保留。

## 验证

运行单元测试：

```bash
python -m unittest discover -s tests
```

验证已有 Phase 2 公开包：

```bash
python experiments/verify_public_bundle.py \
  --bundle-dir experiments/results/phase2_bundle
```

冻结 JSON、证书包和历史选择证据是复现链的一部分。后续整理不得直接修改这些文件；如需形成
新协议，应创建新版本并保留当前归档。
