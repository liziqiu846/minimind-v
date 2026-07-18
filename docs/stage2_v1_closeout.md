# Stage 2 v1 closeout and interpretation addendum

## Status

Stage 2 v1 remains an immutable, reproducible exploratory experiment. Its
model-loading and artifact-integrity audits passed, but its selected training
images were not independent draws under the premise used by Equation (1) of
Lotfi et al. (2024). Consequently, the reported numerical compression-bound
values must not be described as strict 95% population-generalization
certificates.

This addendum does not replace or modify the frozen report. The original files
remain at:

- `experiments/runs/stage2/final/stage2_final_report.md`
- `experiments/runs/stage2/final/stage2_final_report.json`
- `experiments/runs/stage2/final/stage2_artifact_manifest.json`

Their SHA-256 values at closeout were, respectively:

- `9db351916371b1a213e97b7ceec88b396ad7f3647ab73c0dac48b3bebe7e1210`
- `8ef8a277f074425b44f32a20464129752620d33d1a1509c4cf6a7d80ca6ca0a7`
- `716b893c2e1bc17719c574055f95a8ef78b67c1200dd7d842dca5ef525f7d7e5`

## Audit results

The authoritative closeout receipts are under
`experiments/audits/stage2_v1/`.

### Model loading: passed

The audit reconstructed every model before adapter injection and replayed the
initial LLM load with `strict=False` while retaining the complete incompatibility
record.

| Group | Missing keys | Missing language or `lm_head` keys | Unexpected keys | Result |
| --- | ---: | ---: | ---: | --- |
| M0 | 0 | 0 | 0 | passed |
| M1 | 210 | 0 | 0 | passed |
| M2 | 212 | 0 | 0 | passed |
| M3 | 212 | 0 | 0 | passed |

Every tensor in the immutable initial LLM checkpoint loaded exactly. All VLM
missing keys belonged to `vision_encoder.*` or `vision_proj.*`, which are
constructed from separately hashed immutable assets and fixed projector rules.
Thus the former implementation was missing a guard, but the recorded v1 models
did not silently omit language weights.

Receipt: `experiments/audits/stage2_v1/model_load_audit.json`.

### Git, implementation, and artifacts: passed

The audit established all of the following:

- annotated tag `stage2-protocol-v1` resolves to the commit recorded in the
  final report;
- the frozen implementation commit and protocol commit differ only by the
  addition of `experiments/stage2_protocol.json`;
- every implementation blob at the frozen implementation commit matches its
  protocol-declared SHA-256;
- all 252 entries in the final artifact manifest still exist and match both
  their byte counts and SHA-256 values;
- all ten formal runs and seven visual diagnostics are complete;
- no formal failure receipt exists;
- confirmation train and validation files replay through both post-tag
  receipts.

Receipt: `experiments/audits/stage2_v1/integrity_audit.json`.

### Sampling premise: strict certificate not established

The v1 data builder did more than apply a fixed history-exclusion filter. It:

1. collapsed source rows by exact image value;
2. ranked candidates using the image SHA-256;
3. rejected a candidate when its pHash was near any previously selected image;
4. immediately inserted each selected pHash into the forbidden set;
5. required all 12,000 selected images to be unique and mutually pHash-distant.

Later eligibility therefore depended on earlier selections. This is not the
independent sampling construction assumed by the finite-hypothesis bound. No
alternative without-replacement or dependent-sample theorem was frozen for v1.

Receipt: `experiments/audits/stage2_v1/sampling_assumption_audit.json`.

## Claims retained from v1

The following are direct observations on the frozen v1 data and artifacts and
remain valid:

- ten predeclared models trained, quantized, independently decoded, and
  evaluated successfully;
- all reported training and validation risks reproduce on the frozen datasets;
- MMS2 archive sizes and decoded model hashes reproduce;
- no mapping root was selected post hoc;
- for each of the three roots, the computed M3 value was lower than the
  corresponding computed M2 value;
- M3's advantage in the computed quantity came primarily from shorter encoded
  adapters rather than lower empirical risk;
- correct, paired-shuffled, and absent-image evaluations remain secondary
  descriptive diagnostics.

## Claims withdrawn or restricted

The following language is not supported by v1 without an additional theorem:

- “8.1907 bits is a strict 95% population-generalization upper bound”;
- “all ten v1 models have strict non-vacuous certificates”;
- “the 10,000 training images are independent samples for Equation (1)”;
- any unqualified claim that the v1 calculation proves semantic cross-modal
  redundancy or strong visual reasoning.

The safe wording is:

> Under the frozen v1 coding and risk calculation, M3 produced smaller
> exploratory compression-bound values than M2 for all three predeclared
> mappings. The strict independent-sample premise was not established, so these
> values are not presented as population-generalization certificates.

## Successor protocol

Stage 2 v2 will preserve the model families, mapping roots, selected learning
rates, optimizer, codec, smoothing, risk aggregation, familywise confidence
allocation, and diagnostic status. It will change the confirmation sampling
contract and runtime audit guards:

- define a fixed eligible-image-unit population;
- apply pHash only against the fixed historical-exposure set;
- sample train and validation units independently with replacement using
  domain-separated predeclared streams;
- allow and report repeated draws and cross-split coincidences rather than
  adaptively resampling them;
- fail before formal work if model-load, Git, implementation-hash, protocol, or
  data-replay guards do not pass.

Only v2 may be used for renewed strict certificate language, and only for the
explicit target distribution frozen in its protocol.
