# Fitness

The fitness is how close the main agent comes to its work mode, worked out minute by minute from measures of its work
and its load, never from tool counts. Each measure has one line naming one action; the lines speak only in the pressure
bands where they may, so two lines that push opposite ways never share a band. The design is doc 1065; the code is
`src/journal/features/workers/support/mode_measures.py` (the one table of measures), `measure_source.py` (what each
reads), `line_bands.py` (where each line speaks) and `measure_lines.py` (the lines).

## The two queues and the band

Everything that waits on the agent is an item: a worker's clock-out (cleared by its merge or a checked proof, ended by a
send-back, a release or a stop) and a user's message (cleared by the first reply naming it). The worker items and the
messages are measured apart, each as one queue: arrivals over clearings smoothed by a half-life, ρ. Only the worker
queue opens places and moves the band.

The band is low, normal or high, per mode, on the smoothed worker queue:

| Mode | High from | Leaves high under | Low under | Leaves low at |
|---|---|---|---|---|
| Orchestrator | 0.8 | 0.65 | 0.5 | 0.65 |
| Builder | 0.5 | 0.4 | 0.3 | 0.4 |

A band stays at least 10 minutes; high is left once no worker item has waited 5 minutes and is never entered on a queue
empty that long. Solo has no band. The numbers were chosen by `scripts/band_replay.py` over a week of history (NOTES,
Fitness measures).

## The measures

| Mode | Measure | Fails | Passes | Weight | Line |
|---|---|---|---|---|---|
| Builder | Own share of the code, last hour, from 40 lines | under 0.5 | at 0.6 | 4 | write task n yourself (low, normal) |
| Builder | Minutes the worker queue stood high with an item waiting | over 10 | at 10 | 4 | take in worker n first (high) |
| Builder | Workers active at once, last hour | over 2 | at 2 | 2 | merge worker n next, on a dispatch or queue |
| Orchestrator | Minutes the worker queue stood high | over the place dwell plus 5 | the same | 6 | clear worker n first (high) |
| Orchestrator | Minutes the oldest worker waited | over 6 | at 6 | 3 | check worker n (normal, high) |
| Orchestrator | Own share of the landed code, from two merges | over 0.3 | at 0.2 | 3 | hand out task n (low, normal) |
| Orchestrator | Minutes a place stood free, smoothed | over 5 | at 4 | 3 | hand out task n (low, normal) |
| Orchestrator | First reports per merged task, two hours | over 0.5 | at 0.34 | 2 | queue worker n more with --report queue |
| Every mode | Minutes the oldest message waited | over 5 | at 5 | 3 | none: the messages feature's lines decide |

Shown, not scored: tasks completed an hour, and for the orchestrator the share cleared oldest first and the share sent
back. A measure with nothing to measure is left out, never counted perfect. On a dispatch in high the orchestrator is
told to merge the waiting worker next.

## The score

The score is the weighted closeness of every measured measure, from 100 inside its range to 0 far off it, once the mode
has been measured for 30 minutes. A change of mode starts the mode's measures, their windows and its band fresh. The
score is kept as a point each minute it moves; the chart marks where a new version of the scoring begins.

## Blocking and the switch

A worker queue that has failed for `workers.write_block_minutes` (15) makes the agent's writes wait, with the clear line
as the remedy; the merge, check or reply it names and every read go through, and the block lifts once the queue clears.
With `workers.fitness_warnings` off, the measures are still worked out and shown, and no line or block reaches the agent.
