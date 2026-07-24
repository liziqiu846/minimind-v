# SugarCrepe++ 关键语义编辑片段审计

本目录是阶段三 v6 的独立、只读数据审计，不属于 v4/v5 冻结评估流程，也不实现 v6 评分。

## 实际数据绑定

v4 与 v5 的协议和运行 receipt 都绑定到同一个 `data_manifest.json` SHA-256：
`2effb7fbdc763ed1870ba943d30a9cd68be7c6be15ead9892b8c69da62918405`。对应 canonical JSONL 的
SHA-256 是 `35f9fbd7b01e885e95452cd39c9131c440c4d3f69b19a817800468d902e871df`，共 4,757 行。

冻结上游五个 JSON 文件的真实行字段只有 `id`、`filename`、`caption`、`caption2`、
`negative_caption`。canonical 化后逐字保留三个描述字段，把源文件 config 加为 `category`，把
`id` 改名为 `numeric_id`，并增加 `row_key`。数据未提供来源正描述、被修改文本或字符区间。

## 固定规则

脚本分别计算负描述与两条正描述的字符和 token Levenshtein 距离，并以各自最大序列长度归一化。
只有当同一条正描述在两组 `(归一化距离, 原始距离)` 上均不劣，且至少一组严格更优时，才选择该
正描述。完全相同的得分或字符/token 排名冲突均记为 `ambiguous_source`，不使用模型输出或人工判断
破除冲突。

选定来源后，字符片段由不重叠的最长公共前缀和最长公共后缀唯一确定；token 片段对
`add_special_tokens=False` 的完整 token ID 序列使用同一规则。若 lexeme 级出现多个不相等块、检测到
词序变化，或触发固定的大范围重写规则，则分类为 `complex_edit`。只有来源唯一、字符编辑连续、
不是纯大小写/标点/空白差异且 token 对齐可验证时，才分类为 `unique_alignment`。

Byte-level tokenizer 把词前空格并入 token 时，token 区间可能相对精确字符区间移动一个空白字符；
这类可逆且仍能形成明确 token 片段的情况不算 tokenizer 失败。脚本另以 `token_boundary_mismatch`
保留真正的字符/token 边界不覆盖证据，不会静默丢弃。

`direct_metadata` 仅接受可重建完整负描述的显式 `edit_metadata` 区间；本次真实数据中不存在该字段。
额外的 `non_semantic_edit` 类用于单独暴露纯大小写、标点或空白差异。

## 复现命令

从仓库根目录使用阶段三环境运行：

```bash
/home/lizhaohui/lzq/minimind-v/.conda-env/bin/python \
  experiments/phase3_v6/audit/edit_span_audit.py \
  --input-jsonl /home/lizhaohui/lzq/phase3_runtime/prepared_phase3_v4_official_coco_20260721/sugarcrepe_pp_canonical.jsonl \
  --image-manifest /home/lizhaohui/lzq/phase3_runtime/prepared_phase3_v4_official_coco_20260721/coco_referenced_images_manifest.jsonl \
  --pilot-filenames /home/lizhaohui/lzq/phase3_runtime/prepared_phase3_v4_official_coco_20260721/pilot_filenames.txt \
  --formal-filenames /home/lizhaohui/lzq/phase3_runtime/prepared_phase3_v4_official_coco_20260721/formal_filenames.txt \
  --certifying-formal-filenames /home/lizhaohui/lzq/phase3_runtime/results/phase3_formal_v2_phase3v4_20260722/certifying_formal_filenames.txt \
  --tokenizer /home/lizhaohui/lzq/stage2-assets-v1/tokenizer \
  --expected-input-sha256 35f9fbd7b01e885e95452cd39c9131c440c4d3f69b19a817800468d902e871df \
  --output-dir experiments/phase3_v6/audit \
  --seed 3407 \
  --review-limit 30
```

输出的 Markdown 只是待人工检查材料，不表示已经完成人工验证。
