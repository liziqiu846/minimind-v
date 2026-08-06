# Autonomous Loop State

```text
MODE: AUTONOMOUS_RESEARCH
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: VISSUP-01
CURRENT_ROUND: 2
CURRENT_STATE: VISSUP01_ROUND2_PLAN_FROZEN_READY
RUNNING_JOB: none
LAST_PLAN: experiments/plans/VISSUP-01_round2.md
LAST_RESULT: experiments/results/VISSUP-01_round1/RESULT.md
GPU_HOURS_USED_THIS_CYCLE: 0.75
ACTIVE_QUEUE: VISSUP-01
NEXT_QUEUE: TBD_AFTER_VISSUP-01
BACKLOG_QUEUE: OBJ-01,COVER-01
WINOGROUND_ACCESS: blocked_by_access
RESOURCE_NOTE: no_running_gpu_job;round2_is_only_schema_rescue;CVBench2D_variable_choices_A_to_F;single_GPU_sequential_only
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
