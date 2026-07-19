# Stage 2 v1/v2 comparison

v1 is retained as exploratory computed compression-bound values. v2 uses independent with-replacement draws from a fixed finite eligible-image catalog and supports strict certificate language only for that catalog distribution.

| Model | Root | v2-v1 train risk | v2-v1 validation risk | v2-v1 raw bound | Adapter bits unchanged |
| --- | ---: | ---: | ---: | ---: | --- |
| M0 | 43101 | 0.034413 | 0.014672 | 0.311809 | False |
| M0 | 43102 | 0.013844 | -0.002858 | -0.705076 | False |
| M0 | 43103 | -0.002260 | -0.024230 | 1.418319 | False |
| M1 | — | 0.004776 | -0.014950 | -0.024051 | False |
| M2 | 43101 | 0.048307 | 0.030004 | -0.185557 | False |
| M2 | 43102 | -0.005366 | -0.027567 | 0.281717 | False |
| M2 | 43103 | -0.010467 | -0.031734 | -0.001785 | False |
| M3 | 43101 | -0.110140 | -0.131305 | 2.634023 | False |
| M3 | 43102 | 0.047104 | 0.023770 | -0.014262 | False |
| M3 | 43103 | -0.029541 | -0.051478 | 0.823265 | False |

These differences are descriptive because v1 and v2 use different confirmation samples; they are not paired-sample estimates.
