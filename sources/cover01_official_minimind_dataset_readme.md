---
license: apache-2.0
task_categories:
- visual-question-answering
language:
- zh
- en
tags:
- multimodal
---

<div align="center">

![logo](./images/logo.png)

</div>


<div align="center">

![visitors](https://visitor-badge.laobi.icu/badge?page_id=jingyaogong/minimind-v)
[![GitHub Repo stars](https://img.shields.io/github/stars/jingyaogong/minimind-v?style=social)](https://github.com/jingyaogong/minimind-v/stargazers)
[![GitHub Code License](https://img.shields.io/github/license/jingyaogong/minimind-v?v=1)](LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/jingyaogong/minimind-v)](https://github.com/jingyaogong/minimind-v/commits/master)
[![GitHub pull request](https://img.shields.io/badge/PRs-welcome-blue)](https://github.com/jingyaogong/minimind-v/pulls)
[![Collection](https://img.shields.io/badge/🤗-MiniMindV%20%20Collection-blue)](https://huggingface.co/collections/jingyaogong/minimind-v-67000833fb60b3a2e1f3597d)

</div>

<div align="center">

![GitHub Trend](https://trendshift.io/api/badge/repositories/13265)

</div>

## Ⅰ 数据集

本轮训练用到的图文数据全部来自 [ALLaVA-4V](https://huggingface.co/datasets/FreedomIntelligence/ALLaVA-4V) 系列。
相比以往从几份 LLaVA 衍生集拼接得到的数据，ALLaVA-4V 的质量更整齐、中英双语原生对照，细粒度描述也更充分。
它由两个子源构成：一份是 LAION 里挑出来的高质量图片（自然图像为主），一份是 VFLAN 指令流里挑出来的图片（文档、图表、合成场景居多）。

- **Pretrain（`pretrain_i2t.parquet`，约 127 万条 / ~64 万张唯一图像）**
  - `ALLaVA-Caption-LAION-4V` 英/中：~47万 + ~44万
  - `ALLaVA-Caption-VFLAN-4V` 英/中：~19万 + ~17万
  - 任务形式为"请描述这张图片"类的单轮长描述，用于让模型建立视觉 token 到语言 token 的基础对齐。

- **SFT（`sft_i2t.parquet`，约 290 万条 / ~65 万张唯一图像）**
  - `ALLaVA-Instruct-LAION-4V` 英/中：~47万 + ~47万
  - `ALLaVA-Instruct-VFLAN-4V` 英/中：~19万 + ~17万
  - `Instruct-LAION-4v-gemini-claude-ensembled`（Gemini/Claude 合成的增广指令）：~5万
  - `Instruct-LAION-4oiterative`（基于 GPT-4o 迭代润色的指令）：~5万
  - 纯文本对话（保留基础语言能力，图像列填 8×8 黑图占位）：~23万
  - **Pretrain caption 数据全量合并**（与 pretrain 同源、~99% 图像重叠）：~127万
  - 任务形式混合了"围绕图片的推理式问答"、"caption 长描述"和"纯文本对话"，既考验细节追问/长链条推理，也兼顾图像描述与通用语言能力。

合计约 290 万条样本，Pretrain 阶段可直接跳过（SFT 已把 Pretrain 作为子集吸收）。中英比例大致均衡。
考虑到 MiniMind-V 的语言主干仅 67M，把英文和中文一起喂进去是比较稳妥的做法——中文语料对母语输出更友好，而英文原生描述通常更精细，两者互为补充。

图像统一 `resize` 到 **256×256**（与 SigLIP2 NaFlex 编码器的 256 patch token 输入规格相对应），重新编码为 JPEG 打包进 parquet。

(`pretrain_i2t.parquet`) Pretrain 数据集格式：

```text
列名: conversations (json string), image_bytes (binary)

conversations 示例:
[
  {"role": "user", "content": "<image>\n请提供对图片的详细文字描述。"},
  {"role": "assistant", "content": "这张图片展示的是一个..."}
]
image_bytes: <图像二进制数据>
```

(`sft_i2t.parquet`) 单图 SFT 数据集格式：

```text
列名: conversations (json string), image_bytes (binary)

conversations 示例:
[
  {"role": "user", "content": "根据图片推断这个场景的大致时间？<image>"},
  {"role": "assistant", "content": "从光线和阴影来看..."}
]
image_bytes: <图像二进制数据>
```

> 注：sft_i2t.parquet 共约 290 万条数据，其中约 140 万条为图像 instruct 对话、约 127 万条为图像 caption 描述（Pretrain 数据合并而来）、约 23 万条为纯文本对话（t2t，图像列填 8×8 黑图占位，用于保持模型的基础语言能力）。由于 Pretrain 已作为子集并入，可选择跳过 Pretrain 阶段直接进行 SFT。

数据集下载地址：([ModelScope](https://www.modelscope.cn/datasets/gongjy/minimind-v_dataset) | [HuggingFace](https://huggingface.co/datasets/jingyaogong/minimind-v_dataset))