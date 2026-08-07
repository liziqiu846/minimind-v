# PROJALLOC-01 Round 1 Result

## 当前科学问题

在 frozen base、总计 4,096 个 trainable coordinates、visual-necessary data 与训练/
评分协议完全相同时，将低维更新容量集中到跨模态 projector，能否提高视觉结构吸收
与未见 vision-centric task 泛化？

## 假设

若 current allocation 的主要瓶颈是 projector bridge 容量不足，则
projector-dominant `1/4094/1` 应比 current `582/2327/1187` 同时明显提高 held-out
rotation 与 CV-Bench-2D。

## 本轮实验

fresh mapping root `43201` 上顺序训练 current 与 projector-dominant 两条件；二者
逐字节使用相同 11,008-row visual-necessary parquet、mapping root、train seed、
optimizer、2,064 steps、11 个 target tensors 与总 4,096 coordinates。两模型完成且
paired training audit 通过后，统一评分 1,008 个 held-out rotation images 和完整
1,438-image CV-Bench-2D，并只运行一次预注册 analyzer。

## 判定标准

- 支持：rotation accuracy 差至少 `+5 pp`、paired-bootstrap 95% CI 下界 `>0` 且
  projector absolute accuracy 至少 30%；同时 CV-Bench accuracy 差至少 `+1 pp`
  且 gold-margin 差为正。
- 否定：pilot 任一支持项失败即 `REJECT_IDEA`，不得补 seed、改 allocation、换
  metric 或运行旧 sweep。
- 无法判断：仅限 paired invariant、asset、实现、metric 或 job failure；有效的小
  效应或反方向不是无法判断。

## 执行结果

- 配对训练门：两条件均完成 `2,064/2,064` optimizer steps；相同 data SHA、三组
  epoch permutation SHA、train seed、target names 与 frozen hashes。两条件各有
  22 个 factor mappings、0 unused coordinates，所有 loss/gradient finite，frozen
  parameters 前后不变。
- held-out rotation：
  - current accuracy `0.250992`；
  - projector-dominant accuracy `0.263889`；
  - difference `+0.012897`（`+1.29 pp`）；
  - paired image bootstrap 95% CI `[-0.020833,0.045635]`；
  - margin difference `-0.001055 bits/token`。
- CV-Bench-2D：
  - current accuracy `0.352573`；
  - projector-dominant accuracy `0.338665`；
  - difference `-0.013908`（`-1.39 pp`）；
  - paired image bootstrap 95% CI `[-0.039638,0.011127]`；
  - margin difference `-0.058169 bits/token`。
- task/source 方向：Count `-0.025381`、Relation `0`、ADE20K `-0.017378`、COCO
  `-0.011180`，没有外部 task/source 支持。
- pilot 六项门中只有 paired training invariants 通过；rotation effect、CI、
  projector absolute accuracy、CV-Bench effect 与 CV-Bench margin 五门均失败。
- 两次正式训练合计 `966.44 s`（约 `0.268 GPU-hour`）；两次 full scoring 合计
  `177.56 s`（约 `0.049 GPU-hour`）。未访问 final confirmation。

## 结论

`PROJALLOC-01` 被否定：fixed-total projector-dominant allocation 在当前
frozen-base、hashed-coordinate、visual-necessary setting 下不能解释或修复视觉泛化
失败。rotation 的小幅正点估计未达到阈值且 CI 跨 0，外部 CV-Bench accuracy 与
margin 均反向。

本结果不能推出 frozen encoder 一般不可读，也不能推出 objective competition
成立，更不能翻转 `VISSUP-01=REJECTED`。不得运行 `43202/43203`、搜索 allocation
比例、换 metric/proxy 或启动旧 9-point sweep。

## 下一步

冻结 `LITMAP-04` failure-driven plan：围绕 objective competition / gradient
routing、task-specific signal absorption 与 frozen visual representation 对
autoregressive objective 的匹配问题，检索能产生真正不同最小干预的 primary
evidence；不得成为 `VISSUP-01` 或 `PROJALLOC-01` rescue。

## 状态

`REJECT_IDEA`
