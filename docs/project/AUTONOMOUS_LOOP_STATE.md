# Autonomous Loop State

```text
MODE: AUTONOMOUS_RESEARCH
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: PROJALLOC-01
CURRENT_ROUND: 1
CURRENT_STATE: PROJALLOC01_PAIRED_PILOT_CURRENT_TRAINING_RUNNING
RUNNING_JOB: session=92257;driver_pid=1005590;current_child_pid=1005594;physical_gpu=5;root=43201;order=current_then_projector;no_scoring_between_conditions
LAST_PLAN: experiments/plans/PROJALLOC-01_round1.md
LAST_RESULT: experiments/results/PROJALLOC-01_round1/SMOKE.json
GPU_HOURS_USED_THIS_CYCLE: 1.07
ACTIVE_QUEUE: PROJALLOC-01
NEXT_QUEUE: WAIT_CURRENT_THEN_AUTOMATIC_PROJECTOR_TRAIN_NO_INTERMEDIATE_SCORING
BACKLOG_QUEUE: OBJ-01,COVER-01
WINOGROUND_ACCESS: blocked_by_access
RESOURCE_NOTE: current_training_stable_at_start;GPU5_about_1p8GiB_and_active;low_frequency_10_to_20_min_check;projector_auto_starts_after_current;no_final_confirmation
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
