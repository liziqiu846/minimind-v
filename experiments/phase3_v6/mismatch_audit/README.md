# 阶段三 v6 K=5 图片错配清单审计

本目录独立生成 certifying formal 内部的五轮均衡错排。每轮是 1,345 个目标图片到同一批 1,345 个 donor
图片的双射错排；同一目标跨五轮不得重复 donor。脚本不加载 MiniMind-V，不读取模型得分，不使用文本相似度
改变匹配，也不定义最终 v6 评分或正式纳入规则。

## 冻结输入与真实图片路径

图片 manifest 的实际字段是 `coco_image_id / error_code / exists / filename / perceptual_hash / sha256 /
size_bytes / status`，不直接保存路径。脚本将 certifying filename 唯一解析到：

`/home/lizhaohui/lzq/phase3_runtime/coco2017_official/val2017/<filename>`

运行时重新读取每张图片并核对 manifest 的文件 SHA-256 和字节数，同时保存原始宽高、模式、规范化像素
SHA-256、64 位 dHash 和 64 位 aHash。

## 硬性排除与匹配

同 filename、同 COCO ID、同文件 SHA-256、同规范化像素 SHA-256，或同时满足 dHash 汉明距离不超过 1
且 aHash 汉明距离不超过 1 的边被硬性排除。dHash 不超过 4 或 aHash 不超过 4 的其他允许边只标为疑似
视觉近邻，不自动排除。

五轮均使用确定性 Hopcroft–Karp 完美匹配。每个目标的邻接顺序按以下材料的 SHA-256 排序，并以 filename
作为最终平局键：

`phase3-v6-mismatch-v1|seed=3407|round=<r>|target=<target>|donor=<donor>`

后一轮从该目标邻接表中排除前轮已经分配的 donor。任一轮无完美匹配时直接失败，不放松约束。

## 冻结后诊断

错配 manifest 写入并计算 SHA-256 后，脚本才读取每张图片的正描述集合做诊断。TF-IDF 固定为
`lowercase=True`、`stop_words="english"`、`ngram_range=(1, 2)`，vocabulary 按 UTF-8 字节序固定。
同时报告 unigram Jaccard、unigram/bigram Jaccard、规范化正描述完全相同、内容词重叠和 100,000 个固定种子
允许边基线。所有指标只用于描述已冻结清单。

Hull 提及诊断使用大小写不敏感的完整 lexeme 精确集合交集；排除纯标点，不做 stemming、同义词扩展或外部
语义推断。`mentions_*` 只表示 donor 正描述字面出现对应 lexeme，不证明 donor 图片包含该语义。

K 的嵌套定义固定为：K=1 使用 round 1；K=3 使用 round 1–3；K=5 使用 round 1–5。本目录不比较或选择
哪个 K 更好。

## 复现命令

```bash
/home/lizhaohui/lzq/minimind-v/.conda-env/bin/python \
  experiments/phase3_v6/mismatch_audit/build_mismatch_manifest.py \
  --certifying-formal-filenames /home/lizhaohui/lzq/phase3_runtime/results/phase3_formal_v2_phase3v4_20260722/certifying_formal_filenames.txt \
  --image-manifest /home/lizhaohui/lzq/phase3_runtime/prepared_phase3_v4_official_coco_20260721/coco_referenced_images_manifest.jsonl \
  --canonical-jsonl /home/lizhaohui/lzq/phase3_runtime/prepared_phase3_v4_official_coco_20260721/sugarcrepe_pp_canonical.jsonl \
  --contrast-hull-audit experiments/phase3_v6/audit_v2/contrast_hull_audit.jsonl \
  --contrast-hull-summary experiments/phase3_v6/audit_v2/contrast_hull_summary.json \
  --coco-root /home/lizhaohui/lzq/phase3_runtime/coco2017_official/val2017 \
  --expected-certifying-sha256 afb73f300dfbff0c60fd207a3f65c8950448cd2266cc2c8eb0f04b4a41643329 \
  --expected-image-manifest-sha256 317e2273edac3b2abf4d1980d53277f51de987eeb52f26abc39d0bb2636e497a \
  --expected-canonical-sha256 35f9fbd7b01e885e95452cd39c9131c440c4d3f69b19a817800468d902e871df \
  --expected-contrast-audit-sha256 34f592eec832fba78999a2084dcb871a3d6a2e5b015817cc8d598082797d9a4d \
  --expected-contrast-summary-sha256 3eaddd46c68947ed9cca6e125e4b5ca112ec4a48d88a1fa789dbb3e72612d479 \
  --output-dir experiments/phase3_v6/mismatch_audit
```

`manual_review_pairs.md` 及 `review_assets/` 只提供待人工检查材料，不代表图片语义已经人工验证。
