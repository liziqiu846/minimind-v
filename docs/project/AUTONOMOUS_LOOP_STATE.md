# Autonomous Loop State

```text
MODE: AUTONOMOUS_RESEARCH
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: VISCOND-01
CURRENT_ROUND: 1
CURRENT_STATE: VISCOND_ROUND1_SCORING_RUNNING
RUNNING_JOB: VISCOND01_MMSTAR_18_MODEL_MATRIX_GPU7
LAST_PLAN: experiments/plans/VISCOND-01_round1.md
LAST_RESULT: experiments/results/XMC-01_round2/RESULT.md
GPU_HOURS_USED_THIS_CYCLE: 0.21
ACTIVE_QUEUE: VISCOND-01
NEXT_QUEUE: OBJ-01
BACKLOG_QUEUE: COVER-01
WINOGROUND_ACCESS: blocked_by_access
RESOURCE_NOTE: GPU-7_assigned_VISCOND01;matrix_log=/home/lizhaohui/lzq/phase3_runtime/viscond01_mmstar/matrix.log;disk-available-about-49GB
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
