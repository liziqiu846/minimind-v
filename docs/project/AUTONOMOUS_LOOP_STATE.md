# Autonomous Loop State

```text
MODE: AUTONOMOUS_RESEARCH
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: LITMAP-07
CURRENT_ROUND: 1
CURRENT_STATE: LITMAP07_PLAN_PENDING_COMMIT
RUNNING_JOB: none
LAST_PLAN: experiments/plans/LITMAP-07_round1.md
LAST_RESULT: experiments/results/XID-01_round4/RESULT.md
GPU_HOURS_USED_THIS_CYCLE: 1.81
ACTIVE_QUEUE: FACTORIZED_RULE_ABSORPTION_VS_TRAINABILITY
NEXT_QUEUE: COMMIT_LITMAP07_PLAN_THEN_SEARCH_F1_FOUR
BACKLOG_QUEUE: AR_VISUAL_CREDIT;CROSS_MODAL_COMPOSITION;JOINT_SUPPORT_COVERAGE;OBJ-01
WINOGROUND_ACCESS: blocked_by_access
SEARCH_PROGRESS: LITMAP06_COMPLETE;3479_raw_records;2395_unique_titles;369_prior_search_duplicates;98_score_ge_10;10_decisive_primary_sources;5_of_5_DOIs_verified;deterministic_index_verified;AI_figure_backend_failed_twice
REJECTION_SCOPE: XMC01_BRIDGE;COMP01_PROXY;VISCOND01_PROXY;VISSUP01_INSTANTIATION;PROJALLOC01_INSTANTIATION;LITMAP04_BRIDGE;LITMAP05_BRIDGE;COVER01_BRIDGE;NO_MECHANISM_REJECTED
CANONICAL_STATE: docs/project/CURRENT_STATE.md
RESOURCE_NOTE: XID01 root43301 valid pilot rejected;43302/43303 forbidden;one wrong-CUDA-ordinal interruption preserved as engineering failure;no running job;no final confirmation
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
