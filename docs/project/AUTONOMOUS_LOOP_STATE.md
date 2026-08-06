# Autonomous Loop State

```text
MODE: AUTONOMOUS_RESEARCH
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: PROJALLOC-01
CURRENT_ROUND: 1
CURRENT_STATE: PROJALLOC01_RAW_SCORING_RUNNING
RUNNING_JOB: session=62105;physical_gpu=5;root=43201;order=current_then_projector;raw_scores_only;no_aggregate_until_both_complete
LAST_PLAN: experiments/plans/PROJALLOC-01_round1.md
LAST_RESULT: experiments/results/PROJALLOC-01_round1/TRAINING_AUDIT.json
GPU_HOURS_USED_THIS_CYCLE: 1.34
ACTIVE_QUEUE: PROJALLOC-01
NEXT_QUEUE: WAIT_BOTH_RAW_SCORES_THEN_RUN_SINGLE_PREREGISTERED_ANALYSIS
BACKLOG_QUEUE: OBJ-01,COVER-01
WINOGROUND_ACCESS: blocked_by_access
RESOURCE_NOTE: paired_training_valid;current_raw_scoring_stable;projector_auto_follows;do_not_inspect_condition_performance_before_pair_complete;no_final_confirmation
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
