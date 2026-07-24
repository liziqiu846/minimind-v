# SugarCrepe++ contrast hull 第二轮结构审计

本目录独立读取阶段三冻结 canonical 文本，审计“共同前缀 + 对比包围区域 + 共同后缀”的结构可行性。
Contrast hull 只是确定性文本对齐产物，不是人工语义标注。本目录不加载 MiniMind-V、不读取模型输出，也不
定义最终 v6 评分或正式样本过滤规则。第一轮 `experiments/phase3_v6/audit/` 保持不变。

## Alignment view

每条原始描述执行 Unicode NFKC、去除首尾空白、折叠内部连续空白、casefold。句末连续 `. ! ?` 被保存为
独立表面字段并从 alignment lexeme 序列中排除；其他单词、数字、多首字母缩写、连字符词和标点均保留。
每个 lexeme 保存原始字符 `[start, end)` 偏移。规范化只用于对齐，不覆盖 canonical 原文。

## 确定性编辑与比较正描述

Lexeme 编辑脚本使用精确 Wagner–Fischer 动态规划，单位代价为 1，平局优先级固定为
`replace > delete > insert`。输出完整 `equal / replace / insert / delete` 操作块。

两条正描述分别按以下精确元组比较：总编辑 lexeme 数、正负 hull lexeme 总数、非 equal 块数、归一化
lexeme 编辑距离、归一化字符编辑距离。字典序严格更小者成为 `selected_comparison_positive`。完全平局时，
规范化正描述相同则确定性选择 `caption` 并分类为 `equivalent_positive_sources`；否则分类为
`ambiguous_comparison_positive`。

Contrast hull 从第一个非 equal 块开始，到最后一个非 equal 块结束，包括中间所有 equal 桥接词。模型
token 映射在 alignment text 上使用阶段二冻结 fast tokenizer 的 offset mapping。两侧完整 token 序列采用
确定性的 token-ID 最长公共前缀与不重叠最长公共后缀作为边界；这种边界回退可以容纳 BPE token 跨越空格或
lexeme 边界的情况，同时要求两侧使用完全相同的前缀 token，并验证所得 token hull 完整覆盖已确定的 lexical
hull；公共 token 前后缀还会被约束为不得侵入 lexical hull。边界回退带入的额外文本逐条保存为
`*_token_boundary_expansion_text`。若任一 lexical hull 为空或不能
被 token 区间完整覆盖，则保留为 `token_mapping_problem`。是否改用原始文本进行后续正式评分留待理论协议决定。

## 第二轮分类

异常分类优先。正常结构按最大正负 hull token 覆盖率分箱：单块且不超过 50% 为 `one_block_local`；多块且
不超过 75% 为 `multi_block_local_hull`；单块 50%–75% 额外记为 `medium_contrast_hull`；超过 75% 但未覆盖
整句为 `large_contrast_hull`；任一侧覆盖全部模型 token 为 `whole_sentence_hull`。这些分箱不是正式纳入规则。

## 复现命令

```bash
/home/lizhaohui/lzq/minimind-v/.conda-env/bin/python \
  experiments/phase3_v6/audit_v2/contrast_hull_audit.py \
  --input-jsonl /home/lizhaohui/lzq/phase3_runtime/prepared_phase3_v4_official_coco_20260721/sugarcrepe_pp_canonical.jsonl \
  --image-manifest /home/lizhaohui/lzq/phase3_runtime/prepared_phase3_v4_official_coco_20260721/coco_referenced_images_manifest.jsonl \
  --pilot-filenames /home/lizhaohui/lzq/phase3_runtime/prepared_phase3_v4_official_coco_20260721/pilot_filenames.txt \
  --formal-filenames /home/lizhaohui/lzq/phase3_runtime/prepared_phase3_v4_official_coco_20260721/formal_filenames.txt \
  --certifying-formal-filenames /home/lizhaohui/lzq/phase3_runtime/results/phase3_formal_v2_phase3v4_20260722/certifying_formal_filenames.txt \
  --first-round-audit experiments/phase3_v6/audit/edit_span_audit.jsonl \
  --tokenizer /home/lizhaohui/lzq/stage2-assets-v1/tokenizer \
  --expected-input-sha256 35f9fbd7b01e885e95452cd39c9131c440c4d3f69b19a817800468d902e871df \
  --expected-first-round-sha256 042df4e235384571c017a91a6ac11c4f9b67fd948f1a1d58455ffacb55e69fa4 \
  --output-dir experiments/phase3_v6/audit_v2
```

人工抽查文件只提供待审核样本，不代表已完成人工语义验证。
