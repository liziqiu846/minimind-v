# Autonomous Loop State

```text
MODE: AUTONOMOUS_RESEARCH
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: CROSSFACT-01
CURRENT_ROUND: 1
CURRENT_STATE: CROSSFACT01_PLAN_REQUIRED
RUNNING_JOB: none
LAST_PLAN: experiments/plans/COVER-01_round1.md
LAST_RESULT: experiments/results/COVER-01_round1/RESULT.md
GPU_HOURS_USED_THIS_CYCLE: 1.39
ACTIVE_QUEUE: CROSSFACT-01
NEXT_QUEUE: COMMIT_CROSSFACT01_IMMUTABLE_PLAN
BACKLOG_QUEUE: OBJ-01
WINOGROUND_ACCESS: blocked_by_access
SEARCH_PROGRESS: COVER01_COMPLETE;442_raw_records;380_unique_titles;69_prior_search_duplicates;75_score_ge_10;14_decisive_primary_sources;169_of_169_official_sample_matches;3_duplicated_vflan_ids;source_hashes_verified;deterministic_index_verified
REJECTION_SCOPE: XMC01_BRIDGE;COMP01_PROXY;VISCOND01_PROXY;VISSUP01_INSTANTIATION;PROJALLOC01_INSTANTIATION;LITMAP04_BRIDGE;LITMAP05_BRIDGE;COVER01_BRIDGE;NO_MECHANISM_REJECTED
CANONICAL_STATE: docs/project/CURRENT_STATE.md
RESOURCE_NOTE: COVER01 complete with zero GPU/checkpoint/training;CROSSFACT01 plan must be committed before analysis;PROJALLOC roots43202/43203 forbidden;no running job;no final confirmation
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
