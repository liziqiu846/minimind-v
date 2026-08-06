# XMC-01 Round 2 Source Manifest

## 检索回执

- 截止日期：2026-08-07（不采用晚于该日期首次发布的工作）。
- Parallel CLI：已按 `research-lookup` 路径检查，但服务器没有 Parallel
  authentication；没有伪造或补写 Parallel 结果。
- 回退检索：按 `paper-lookup` 使用 arXiv API 与 OpenAlex API。
- 原始查询响应：仓库 `sources/research_xmc_*`。
- PDF：从 `https://arxiv.org/pdf/<id>` 获取，保存在仓库外
  `/home/lizhaohui/lzq/phase3_runtime/xmc_round2/papers/`。
- 正文解析：13/13 均为有效 PDF；因服务器没有 `pdftotext`，按 `pdf` skill
  使用 `pypdf` 逐页提取全文和 appendix 到仓库外 runtime。

## 完整正文核查版本

| arXiv | Version | SHA-256 |
|---|---:|---|
| [2303.09166](https://arxiv.org/abs/2303.09166) | v1 | `e23f818c7b69cd0a691a06803dd3250352d1f85888bfa5759de5b1c5289393b5` |
| [2306.04272](https://arxiv.org/abs/2306.04272) | v1 | `d3b99dedf191da4cc6a18d9eb7414cdd7d935b49ea5be0b011356929d85201c4` |
| [2409.07402](https://arxiv.org/abs/2409.07402) | v2 | `f57c0a6dfd27181e137fc2109b42ab75bfc02c135a0b2df3714fe2da035a37e2` |
| [2504.10143](https://arxiv.org/abs/2504.10143) | v7 | `457dd723323ba879ca1bac77bde10ab846663ae468cd30ff598b45a6585e7034` |
| [2505.24134](https://arxiv.org/abs/2505.24134) | v1 | `fca602bc430e069ffac456280d7265475a6b87aa43c90af49884842a8a4204b4` |
| [2507.09128](https://arxiv.org/abs/2507.09128) | v2 | `dce5224c01b30e6abb7a5315d86be3eba744e8db6da2b2dd12156e376e81b224` |
| [2510.03268](https://arxiv.org/abs/2510.03268) | v2 | `10938a36b6089344e624434ec426ef8656688ca42523435ff29a489c53ba633e` |
| [2602.07026](https://arxiv.org/abs/2602.07026) | v3 | `3c3d1f387f418b9cee055ebbdbaf96d670c3f0fab457984ee1bd6f0df1b590a1` |
| [2604.04496](https://arxiv.org/abs/2604.04496) | v1 | `031a2c0f299b2263c3aefdd37dce6713417b2866fb68f399d9edb6dafd9d9e96` |
| [2605.02116](https://arxiv.org/abs/2605.02116) | v3 | `a4ac8a51521174ef01a140c46d5a8d8e575a5fc2c06a1d135731513e82b21e98` |
| [2605.08764](https://arxiv.org/abs/2605.08764) | v1 | `dc75c026038fdb1d7a379c563a3efb7dc87c5888dc18d8dbfaa39210a7e65cb5` |
| [2607.08194](https://arxiv.org/abs/2607.08194) | v1 | `1ce7f44e8ee7a9b802c27741063d36e634aade492097516cbe57a6547af820f7` |
| [2607.17673](https://arxiv.org/abs/2607.17673) | v1 | `70af975e6aeec27a1db1af78549128d72fe2d0a5d18c415bc2ab0704d8055588` |

这些 hash 只标识本轮实际核查的 PDF 字节版本；不把 arXiv 预印本状态误写为
同行评审状态。已发表版本在 applicability matrix 中单独标明。
