# Autonomous Loop State

```text
MODE: AUTONOMOUS_RESEARCH
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: PROJALLOC-01
CURRENT_ROUND: 1
CURRENT_STATE: PROJALLOC01_SMOKE_PASSED_READY_FOR_PAIRED_PILOT
RUNNING_JOB: none
LAST_PLAN: experiments/plans/PROJALLOC-01_round1.md
LAST_RESULT: experiments/results/PROJALLOC-01_round1/SMOKE.json
GPU_HOURS_USED_THIS_CYCLE: 1.07
ACTIVE_QUEUE: PROJALLOC-01
NEXT_QUEUE: PROJALLOC-01_ROOT43201_CURRENT_THEN_PROJECTOR_FULL_TRAIN
BACKLOG_QUEUE: OBJ-01,COVER-01
WINOGROUND_ACCESS: blocked_by_access
RESOURCE_NOTE: no_running_gpu_job;CPU_preflight_and_paired_smoke_passed;run_current_full_then_projector_full_without_intermediate_scoring;no_final_confirmation
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
