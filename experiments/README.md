# MiniMind-V 泛化验证实验

本目录把当前理论场景固定为：给定单张图片，自回归预测文字描述。首轮只使用
`pretrain_i2t.parquet` 的 caption 数据，不混入 SFT 问答和纯文本样本。

## 环境

```bash
source /home/fuyongjian/anaconda3/etc/profile.d/conda.sh
conda activate /home/lizhaohui/lzq/minimind-v/.conda-env
cd /home/lizhaohui/lzq/minimind-v
```

## 1. 固定数据划分

先做约 10,000/2,000 的快速闭环；确认训练、评估和统计代码后再扩大样本量。划分以图片内容
SHA-256 为分组单位，同一图片的中英文 caption 会进入同一个 split，避免图片泄漏。由于完整保留图片组，
实际行数可能略高于请求值，以 `split_manifest.json` 为准。

```bash
python experiments/prepare_caption_splits.py \
  --input dataset/pretrain_i2t.parquet \
  --output-dir dataset/caption_10k_seed42 \
  --train-size 10000 \
  --val-size 2000 \
  --seed 42
```

## 2. 第一轮三组冻结策略

三组实验必须使用同一初始化权重、数据划分、随机种子、batch size、训练轮数和学习率调度。

| 组别 | `freeze_llm` | 可训练部分 | 当前实测可训练参数 |
|---|---:|---|---:|
| A | 2 | 仅 `vision_proj` | 1,182,720 |
| B | 1 | `vision_proj` + LLM 首末层 | 15,931,776 |
| C | 0 | 除视觉编码器外全部 | 65,094,912 |

先以 A 组验证训练闭环：

```bash
cd trainer
python train_pretrain_vlm.py \
  --data_path ../dataset/caption_10k_seed42/train.parquet \
  --from_weight llm \
  --save_weight caption10k_freeze2_seed42 \
  --save_dir ../out \
  --freeze_llm 2 \
  --augment 0 \
  --seed 42 \
  --epochs 1 \
  --batch_size 4 \
  --accumulation_steps 4 \
  --device cuda:0
```

随后仅改变 `--freeze_llm` 和 `--save_weight` 运行 B、C 两组。正式比较前应为三组分别调节学习率，
再报告“统一学习率”和“各组最佳学习率”两套结果，避免优化难度被误解释为泛化效应。

## 3. 计算训练集与验证集 NLL

```bash
cd ..
python experiments/evaluate_nll.py \
  --data-path dataset/caption_10k_seed42/validation.parquet \
  --weight caption10k_freeze2_seed42 \
  --output experiments/results/caption10k_freeze2_seed42_validation.json
```

评估脚本关闭训练时的随机 system prompt 增广，并同时报告：

- 目标 token 平均 NLL 与 perplexity；
- 每个图文样本的平均序列 NLL；
- 样本数、目标 token 数和每样本平均目标长度。

## 4. 与理论量的对应

首轮结果表至少包含：训练 NLL、验证 NLL、泛化差、可训练参数量和随机种子。下一步再加入相对
`llm_768.pth` 的参数增量量化/编码长度，并代入已经推导的视觉—语言泛化界。模型复杂度应以实际编码
比特数为主，可训练参数量只作为尚未实现压缩编码时的诊断代理，不能直接替代理论中的编码长度。

## 5. 实际编码、解码评估和泛化界

正式界必须使用量化后重新解码的模型。下面的归档包含可训练张量的固定宽度量化索引、每张量
scale、名称、形状和解码协议；其完整文件大小（而不是解码后的 `.pth` 大小）作为描述长度。

```bash
python experiments/quantize_checkpoint.py \
  --run-dir experiments/runs/freeze_comparison/a_freeze2_seed42 \
  --bits 4 \
  --archive experiments/runs/freeze_comparison/a_freeze2_seed42/compression/q4.mmq \
  --decoded-checkpoint experiments/runs/freeze_comparison/a_freeze2_seed42/compression/q4_decoded.pth

python experiments/evaluate_smoothed_risk.py \
  --run-dir experiments/runs/freeze_comparison/a_freeze2_seed42 \
  --checkpoint experiments/runs/freeze_comparison/a_freeze2_seed42/compression/q4_decoded.pth \
  --model-kind decoded_quantized \
  --data-path dataset/bound_caption_10k_seed42/train.parquet \
  --output experiments/runs/freeze_comparison/a_freeze2_seed42/risk_train_q4.json

python experiments/compute_bound_report.py \
  --encoding experiments/runs/freeze_comparison/a_freeze2_seed42/compression/q4.json \
  --training-risk experiments/runs/freeze_comparison/a_freeze2_seed42/risk_train_q4.json \
  --validation-risk experiments/runs/freeze_comparison/a_freeze2_seed42/risk_validation_q4.json \
  --output experiments/runs/freeze_comparison/a_freeze2_seed42/bound_q4.json
```

当前 codec 对初始权重中已有的可训练张量编码增量；由于旧实验没有保存 projector 的训练前状态，
`vision_proj` 采用全零基线，即编码绝对权重。C 组的 tied embedding/lm-head 只编码一次。

## 6. 当前结果

seed42 的完整表见 `results/freeze_comparison_seed42_q4.json` 和同名 CSV。下表风险均使用
`alpha=0.0001`，单位是 bit/目标 token；“上界”列则是在八个预声明 alpha 中计入 3-bit 选择代价后
取得的最小原始压缩上界。

| 设置 | 可训练参数 | q4 实际码长 | 未量化训练/验证风险 | 未量化差距 | q4 训练/验证风险 | 最小原始上界 |
|---|---:|---:|---:|---:|---:|---:|
| A：仅 projector | 1,182,720 | 4,748,176 | 3.8059 / 3.8155 | 0.0096 | 3.8088 / 3.8180 | 166.91 |
| B：projector + 首末层 | 15,931,776 | 63,798,840 | 3.0001 / 3.2930 | 0.2929 | 3.0132 / 3.3028 | 598.51 |
| C：除视觉编码器外全训 | 65,094,912 | 260,619,776 | 3.0458 / 3.4383 | 0.3924 | 3.2305 / 3.6120 | 1205.85 |

验证图片与训练图片的 SHA-256 交集为 0。B 在统一学习率下得到最低验证风险，A 的差距和描述长度
最小，C 没有超过 B 且对 4-bit 量化更敏感。三组上界都高于随机猜测的 12.64 bit，仍为空洞界；
下一步应先做不同 seed 和各冻结策略的学习率调节，再讨论稳定趋势。
