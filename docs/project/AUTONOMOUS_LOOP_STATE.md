# Autonomous Loop State

```text
MODE: AUTONOMOUS_RESEARCH
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: LITMAP-02
CURRENT_ROUND: 1
CURRENT_STATE: LITMAP02_PLAN_FROZEN_READY
RUNNING_JOB: none
LAST_PLAN: experiments/plans/LITMAP-02_round1.md
LAST_RESULT: experiments/results/VISCOND-01_round1/RESULT.md
GPU_HOURS_USED_THIS_CYCLE: 0.75
ACTIVE_QUEUE: LITMAP-02
NEXT_QUEUE: TBD_FROM_LITMAP-02
BACKLOG_QUEUE: OBJ-01,COVER-01
WINOGROUND_ACCESS: blocked_by_access
RESOURCE_NOTE: no_running_gpu_job;VISCOND01_raw_scores_retained_at=/home/lizhaohui/lzq/phase3_runtime/viscond01_mmstar/matrix/models;disk-available-about-49GB
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
