# Autonomous Loop State

```text
MODE: AUTONOMOUS_RESEARCH
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: LITMAP-04
CURRENT_ROUND: 1
CURRENT_STATE: LITMAP04_PLAN_FROZEN_SEARCH_PENDING
RUNNING_JOB: none
LAST_PLAN: experiments/plans/LITMAP-04_round1.md
LAST_RESULT: experiments/results/PROJALLOC-01_round1/RESULT.md
GPU_HOURS_USED_THIS_CYCLE: 1.39
ACTIVE_QUEUE: LITMAP-04
NEXT_QUEUE: EXECUTE_LITMAP04_EXISTING_SOURCE_DEDUP_AND_FIVE_QUERY_FAMILIES
BACKLOG_QUEUE: OBJ-01,COVER-01
WINOGROUND_ACCESS: blocked_by_access
RESOURCE_NOTE: PROJALLOC-01 root43201 valid but all scientific support gates failed;roots43202/43203 forbidden;no running job;no final confirmation
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
