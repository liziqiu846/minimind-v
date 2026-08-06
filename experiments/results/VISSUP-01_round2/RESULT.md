# VISSUP-01 Round 2 Result

## 当前科学问题

等模型、base captions、rotated pixels、labels、steps 与 target format 下，使 9.16%
instruction 必须看图，能否比文本泄露 label 的 control 形成可迁移视觉能力？

## 假设

若 caption-only 监督未充分迫使 4,096-coordinate MiniMind-V 吸收视觉结构，则
visual-necessary rotation mix 应先提高 held-out rotation，再方向性提高全新
CV-Bench-2D accuracy 与 gold margin。

## 本轮实验

round1 因官方 CV-Bench 为 2–6 choices 而在模型运行前触发 schema gate；round2
作为唯一 rescue 保留全部 1,438 题并采用 per-row A–F scorer。随后在 root `43101`
顺序训练 `label-revealed` 与 `visual-necessary` 两条件，各 11,008 rows、3 epochs、
2,064 steps；两模型完成后统一评分 1,008 个 held-out rotation images 与 1,438 个
CV-Bench-2D images。

## 判定标准

- 支持：rotation accuracy 差至少 `+5 pp`、bootstrap 95% CI 下界 `>0` 且 visual
  accuracy 至少 30%；同时 CV-Bench accuracy 差至少 `+1 pp` 且 margin 差为正。
- 否定：pilot 任一支持项失败即 `REJECT_IDEA`，不得补 seed 或换 task/ratio/proxy。
- 无法判断：仅数据/panel/asset/实现或 job failure；有效小效应不是无法判断。

## 执行结果

- 数据门：base 8,848 独立 pixel groups；rotation train/held-out 各 1,008 且不重叠；
  CV-Bench 1,438/1,438 rows，与 base exact pixel overlap 为 0。
- 训练门：两条件均完成 `2,064/2,064` steps；相同三组 permutation SHA、相同初始
  frozen hash，所有 frozen parameters 前后不变，loss/gradient 全 finite。
- held-out rotation：
  - control accuracy `0.251984`；
  - visual accuracy `0.245040`；
  - difference `-0.006944`（`-0.69 pp`）；
  - paired image bootstrap 95% CI `[-0.037698, 0.022817]`；
  - margin difference `-0.025345 bits/token`。
- CV-Bench-2D：
  - control accuracy `0.354659`；
  - visual accuracy `0.353268`；
  - difference `-0.001391`（`-0.14 pp`）；
  - paired image bootstrap 95% CI `[-0.042420, 0.040334]`；
  - margin difference `+0.002841 bits/token`。
- Count accuracy difference `-0.003807`，Relation `+0.001538`；ADE20K
  `-0.011058`，COCO `+0.006211`，没有跨 task/source 稳定方向。
- pilot 六项门中只有 paired training invariants 与 CV margin positive 通过；rotation
  mechanism、rotation CI、visual absolute accuracy 与 CV accuracy effect 均失败。
- 两次正式训练共 956.8 秒；两次 full scoring 共 168.0 秒。未访问 final
  confirmation。

## 结论

`VISSUP-01` 被直接机制门否定：在当前低维 M2-current 下，visual-necessary rotation
supervision 不仅没有迁移到 CV-Bench，连预声明 held-out rotation task 也没有优于
文本泄露 control。positive margin 的单一辅助方向不能覆盖两项主 accuracy 的负方向。

不能由此推出所有视觉自监督无效；可推出的是固定 9.16% rotation instruction、
4,096-coordinate MiniMind-V 与当前 frozen encoder/adapter 组合不支持该机制。不得
换 task、ratio、prompt、metric 或补 `43102/43103` rescue。

## 下一步

冻结 `LITMAP-03` failure-driven plan：针对“显式视觉任务为何没有进入低维可训练
subspace”检索 parameter-efficient LVLM、module allocation、visual gradient routing
与直接视觉 target 的权威理论/受控证据，只登记一个能区分 frozen-encoder
identifiability、trainable-subspace capacity 和 objective competition 的新 candidate。

## 状态

`REJECT_IDEA`
