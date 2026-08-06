# Autonomous Loop State

```text
MODE: AUTONOMOUS_RESEARCH
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: PROJALLOC-01
CURRENT_ROUND: 1
CURRENT_STATE: PROJALLOC01_REGISTRY_READY_PLAN_REQUIRED
RUNNING_JOB: none
LAST_PLAN: experiments/plans/LITMAP-03_round1.md
LAST_RESULT: experiments/results/LITMAP-03_round1/RESULT.md
GPU_HOURS_USED_THIS_CYCLE: 1.07
ACTIVE_QUEUE: PROJALLOC-01
NEXT_QUEUE: PROJALLOC-01_PAIRED_PILOT
BACKLOG_QUEUE: OBJ-01,COVER-01
WINOGROUND_ACCESS: blocked_by_access
RESOURCE_NOTE: no_running_gpu_job;LITMAP03_complete_0_GPU;PROJALLOC01_plan_required_before_code_or_training;fresh_roots_43201_43203;no_final_confirmation
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
