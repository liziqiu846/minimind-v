# Stage 2 joint-compression experiment report

Protocol: `minimind-v-stage2-joint-compression-v2` (`4a15ae6697081098973998f7340702368403fa81f39d6c8ed43172b74a55b5b3`)

All ten predeclared formal models completed. The table reports the raw, unclipped compression bound; no mapping root was selected post hoc.

| Model | Root | Train risk (bits) | Validation risk (bits) | Adapter bits | Penalty (bits) | Raw bound (bits) | Random margin (bits) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| M0 | 43101 | 5.067062 | 5.054879 | 6408 | 5.973921 | 11.040984 | 1.602873 |
| M0 | 43102 | 5.064794 | 5.054002 | 6720 | 6.116961 | 11.181755 | 1.462101 |
| M0 | 43103 | 5.014444 | 5.000706 | 8040 | 6.688340 | 11.702784 | 0.941072 |
| M1 | — | 4.874315 | 4.861855 | 10600 | 7.676111 | 12.550426 | 0.093430 |
| M2 | 43101 | 4.931502 | 4.919503 | 8792 | 6.992995 | 11.924497 | 0.719359 |
| M2 | 43102 | 4.916816 | 4.902748 | 9856 | 7.402647 | 12.319463 | 0.324393 |
| M2 | 43103 | 4.878552 | 4.864660 | 10568 | 7.664550 | 12.543102 | 0.100754 |
| M3 | 43101 | 4.974591 | 4.961433 | 6144 | 5.850154 | 10.824745 | 1.819111 |
| M3 | 43102 | 5.004928 | 4.990440 | 7528 | 6.472710 | 11.477638 | 1.166219 |
| M3 | 43103 | 4.998919 | 4.984781 | 6112 | 5.834973 | 10.833892 | 1.809964 |

## Predeclared paired differences

| Root | Vision cost T (bits) | Shared gain G (bits) |
| ---: | ---: | ---: |
| 43101 | -0.216239 | 1.099752 |
| 43102 | 0.295882 | 0.841826 |
| 43103 | -0.868892 | 1.709210 |
| mean | -0.263083 | 1.216929 |

## Integrity and scope

- Confirmation data verification: `passed` over 12000 independent draws.
- Visual diagnostics: seven models, secondary/descriptive only; see `/home/lizhaohui/lzq/minimind-v-stage2/experiments/runs/stage2_v2_fast/final/diagnostics.json`.
- Artifact manifest: `/home/lizhaohui/lzq/minimind-v-stage2/experiments/runs/stage2_v2_fast/final/stage2_artifact_manifest.json`.
- Certificate scope: the finite uniform empirical distribution over the frozen v2 eligible-image catalog; this is not a real-world-distribution certificate.
- Execution amendment: all ten models were rerun from scratch, with each model confined to one A40 and independent models dispatched concurrently across dynamically idle A40s.
- Physical A40s used: 2 (`GPU-8e1547c5-b212-b319-786a-c17a3d644e0b`, `GPU-dc9b3899-d5cf-ff29-8870-c369ef8196a6`).
- Conformance caveat: these results conform to the hardware-amended protocol recorded above; they are not claimed as a strict execution of the superseded single-GPU tag.
