# Phase 3 private versus shared budget v1

Engineering-only framework for the frozen 18-candidate P/S comparison. P uses
three independent coordinate vectors allocated by the verified Stage 2 M2
factor-element proportions. S uses one registered vector `w`; each module has
its own frozen projection and computes `delta_theta_m = P_m w`.

All description lengths are bits. Fresh-confirmation selection pays exactly
`log2(18)` bits and does not re-encode checkpoints or frozen seed integers.
Formal confirmation requires an independent manifest; the existing 1343-image
set is development-only.

Formal training is a separate protocol-bound path. First create the immutable
run manifest with `run_manifest`, then dispatch it with `run_matrix`. The
single-candidate `train_one` entry accepts only a frozen config ID and runtime
paths/device; scientific fields and training hyperparameters have no CLI
overrides. Completed candidates are skipped, failed candidates retain their
status and are eligible only for an explicit `run_matrix --resume` using the
same immutable command.
