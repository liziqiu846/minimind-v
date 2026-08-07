# COVER-01 Local Data-Lineage Receipt

## Exact local artifact

| Field | Value |
|---|---|
| Local path | `dataset/pretrain_i2t.parquet` |
| Size | 4,326,415,097 bytes |
| Rows | 1,274,698 |
| SHA-256 | `65761f37d1947d54a1d85457ff70938275e4ef58ba5cedcd02463a3a247c93fd` |
| Columns | `conversations: String`, `image_bytes: Binary` |
| Official MiniMind revision | `1e279a8b665cb10383451a6af6fd62b9f35bdd79` |
| Official tree match | size and LFS content SHA-256 both match |

The local schema has no `id`, `source_id`, `dataset`, `image_path`, `original_caption`,
or task/domain field. Across all local conversation strings, exact occurrences of
`allava_laion`, `allava_vflan`, `source_id`, and `original_caption` are each zero.
Therefore source IDs are not embedded in the parquet schema or text.

## Official upstream schema

The MiniMind card says the pretraining parquet combines English/Chinese captions from
ALLaVA LAION and VFLAN. The saved upstream ALLaVA card/API/tree at revision
`0fd42fce5c047d387a4bb5318d588eae9a9797f0` exposes:

- `allava_laion/caption`: `id`, `image`, `conversations`, `url`, `caption`,
  `llava-1.5-7b-PPL`;
- `allava_vflan/caption`: `id`, `image`, `conversations`, `caption`,
  `llava-1.5-7b-PPL`.

The card describes LAION as web imagery and VFLAN as Vision-Flan imagery. Both use
GPT-4V-generated captions, but their acquisition/task origins differ. The source label is
therefore meaningful provenance, yet it simultaneously carries natural-image versus
document/chart/synthetic content, original task, acquisition, style, and difficulty
differences; it is not a factorial coverage variable.

## Reproducible sample reconstruction

The saved official dataset-server responses contain 169 usable caption rows:

| Source | Official rows | Unique IDs | Exact local assistant matches |
|---|---:|---:|---:|
| ALLaVA LAION caption | 76 | 76 | 76 |
| ALLaVA VFLAN caption | 93 | 90 | 93 |
| **Total** | **169** | **166** | **169** |

Every official English assistant answer has exactly one exact match in the local parquet.
This demonstrates a deterministic sampled mapping from local assistant text to an official
row occurrence, source ID, and image path.

The audit also found three duplicated official VFLAN ID values:

- `allava_vflan_cap_13941`
- `allava_vflan_cap_14554`
- `allava_vflan_cap_2293`

Each appears twice with the same image path; two have visibly different generated caption
texts and all saved assistant strings remain unique. Thus the official `id` field cannot be
treated as a globally unique example key without an occurrence/caption disambiguator.

The exact mappings and assistant-text hashes are in `LINEAGE_AUDIT.json`. Running
`experiments/phase3/audit_cover01_local_lineage.py` reproduces the receipt.

## What this proves

- The local parquet is exactly the official MiniMind pretraining artifact at the saved
  revision.
- Source IDs are absent from the local schema.
- Contrary to an “irrecoverable lineage” claim, sampled English rows can recover their
  upstream ALLaVA source occurrence deterministically from exact assistant text.
- Official source IDs themselves have a sampled uniqueness defect, so reconstruction must
  preserve row occurrence or caption identity.

## What this does not prove

- Full-dataset reconstruction coverage for all 1,274,698 local rows.
- Correct propagation of an English-row source ID to Chinese translations by identical
  image bytes.
- That LAION versus VFLAN isolates coverage rather than source, task, content, style,
  quality, and difficulty.
- An exact baseline/complementary/redundancy partition or unique held-out target.
- Any effect of coverage on autoregressive LVLM generalization.

The failure of COVER-01 therefore must not be attributed simply to “missing IDs.” The
independent decisive failure is that no audited source schema or primary study fixes a
unique single-factor complementary-versus-redundancy contrast and held-out target without
analyst choice or major confounding.

## Access and license boundary

- The MiniMind dataset card declares Apache-2.0.
- The upstream ALLaVA card declares CC-BY-NC-4.0.
- The upstream card explicitly states that the publisher does not own rights to the
  packaged images.

This is a lineage/licensing caveat that must be carried into any future reconstruction.
It is not a current `HARD_STOP`, because COVER-01 launches no training and selects no
candidate. Any later use would need to obey the upstream non-commercial and image-rights
conditions rather than relying only on the downstream card label.
