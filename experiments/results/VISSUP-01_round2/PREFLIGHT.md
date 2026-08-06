# VISSUP-01 Round 2 Preflight

- deterministic data/panel implementation commit：`e2412fe`；
- 6/6 unit tests passed；
- 10,000 base draws 对应 8,848 个独立 normalized pixel groups；
- rotation training / held-out 各 1,008 个独立图像，集合不重叠，A/B/C/D 各 252；
- 两条件均为 11,008 rows，rotated bytes、labels 与 target IDs paired；
- CV-Bench-2D 1,438/1,438 rows、1,438 独立图像组全部通过 variable-choice token
  gate，最长 185 tokens；
- 与完整 base train 的 exact normalized-pixel overlap 为 0；
- 没有训练、没有模型 inference、没有访问 final confirmation。

结论：round2 data / panel gate 通过，可以进入每条件 2-sample 非科学 smoke；只有
smoke 全部通过后才能启动 root `43101` paired pilot。
