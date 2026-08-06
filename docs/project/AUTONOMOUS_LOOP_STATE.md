# Autonomous Loop State

```text
MODE: AUTONOMOUS_RESEARCH
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: LITMAP-03
CURRENT_ROUND: 1
CURRENT_STATE: LITMAP03_PLAN_REQUIRED
RUNNING_JOB: none
LAST_PLAN: experiments/plans/VISSUP-01_round2.md
LAST_RESULT: experiments/results/VISSUP-01_round2/RESULT.md
GPU_HOURS_USED_THIS_CYCLE: 1.07
ACTIVE_QUEUE: LITMAP-03
NEXT_QUEUE: TBD_FROM_LITMAP-03
BACKLOG_QUEUE: OBJ-01,COVER-01
WINOGROUND_ACCESS: blocked_by_access
RESOURCE_NOTE: no_running_gpu_job;VISSUP01_rejected_after_one_paired_root;raw_retained=experiments/results/VISSUP-01_round2/raw;no_seed_escalation
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
