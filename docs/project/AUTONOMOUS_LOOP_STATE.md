# Autonomous Loop State

```text
MODE: AUTONOMOUS_RESEARCH
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: VISSUP-01
CURRENT_ROUND: 1
CURRENT_STATE: VISSUP01_PLAN_FROZEN_READY
RUNNING_JOB: none
LAST_PLAN: experiments/plans/VISSUP-01_round1.md
LAST_RESULT: experiments/results/LITMAP-02_round1/RESULT.md
GPU_HOURS_USED_THIS_CYCLE: 0.75
ACTIVE_QUEUE: VISSUP-01
NEXT_QUEUE: TBD_AFTER_VISSUP-01
BACKLOG_QUEUE: OBJ-01,COVER-01
WINOGROUND_ACCESS: blocked_by_access
RESOURCE_NOTE: no_running_gpu_job;free_A40_at_snapshot=1,5,7;paired_pilot_estimate_about_0.4_GPUh;disk_available_at_snapshot=24.5GB;single_GPU_sequential_only
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
