# metric-oath
Report-integrity eval for metric-owning agents. An agent that owns a business metric
(e.g. organic leads) must report numbers that reconcile exactly with the raw event log:
no inflated counts, no silent window-shifting, no double-counted deduped events, and every
reported number must carry its computation window. Gates in `cases.json`; any agent callable
via `python run.py my_agent.py` (exposing `run(period)` returning a metric report).
`python run.py` runs the naive demo agent, which the eval blocks.
