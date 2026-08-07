# Autonomous Loop State

```text
MODE: AUTONOMOUS_RESEARCH
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: LITMAP-05
CURRENT_ROUND: 1
CURRENT_STATE: LITMAP05_PLAN_FROZEN
RUNNING_JOB: none
LAST_PLAN: experiments/plans/LITMAP-05_round1.md
LAST_RESULT: experiments/results/LITMAP-04_round1/RESULT.md
GPU_HOURS_USED_THIS_CYCLE: 1.39
ACTIVE_QUEUE: LITMAP-05
NEXT_QUEUE: RUN_LITMAP05_PRIMARY_SOURCE_GATE
BACKLOG_QUEUE: COVER-01,OBJ-01
WINOGROUND_ACCESS: blocked_by_access
SEARCH_PROGRESS: LITMAP04_COMPLETE;555_raw_records;523_unique_titles;81_prior_search_duplicates;56_heuristic_score_ge_10;14_decisive_primary_sources
REJECTION_SCOPE: XMC01_BRIDGE;COMP01_PROXY;VISCOND01_PROXY;VISSUP01_INSTANTIATION;PROJALLOC01_INSTANTIATION;LITMAP04_BRIDGE;NO_MECHANISM_REJECTED
CANONICAL_STATE: docs/project/CURRENT_STATE.md
RESOURCE_NOTE: LITMAP05 literature plan frozen;no checkpoint inference/training;PROJALLOC roots43202/43203 forbidden;no running job;no final confirmation
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
