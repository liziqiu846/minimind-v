# Autonomous Loop State

```text
MODE: AUTONOMOUS_RESEARCH
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: VISSUP-01
CURRENT_ROUND: 2
CURRENT_STATE: VISSUP01_PILOT_CONTROL_TRAINING
RUNNING_JOB: root43101_label_revealed;gpu7;pid951237;session95362
LAST_PLAN: experiments/plans/VISSUP-01_round2.md
LAST_RESULT: experiments/results/VISSUP-01_round2/PREFLIGHT.md
GPU_HOURS_USED_THIS_CYCLE: 0.75
ACTIVE_QUEUE: VISSUP-01
NEXT_QUEUE: TBD_AFTER_VISSUP-01
BACKLOG_QUEUE: OBJ-01,COVER-01
WINOGROUND_ACCESS: blocked_by_access
RESOURCE_NOTE: smoke_passed_both_conditions;control_training_started_GPU7;launcher_cleanup_attempt_had_zero_steps_and_no_artifacts;single_GPU_sequential_only
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
