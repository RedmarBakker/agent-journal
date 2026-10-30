# Sprint metrics v1

`GET /journal/sprints/{id}/metrics` is an owner-scoped read of a sprint's recorded execution, delivery and scope. It does not approve, start or change plans.

The report uses the frozen task snapshots taken when a sprint starts. A recorded `plan_added` change contributes its saved task snapshot on the day the change was recorded. A task cancellation is a scope removal; a task that left a plan without a recorded sprint change is flagged instead of reconstructed. Accepted size revisions do not rewrite the committed size used for throughput or velocity.

Execution throughput counts a task once when it is completed or worker work is merged. Delivered throughput counts it once when delivery evidence is accepted or corrected. The frozen definition of done labels remaining deployment work as awaiting deployment; other required evidence remains awaiting evidence. Daily buckets use the outcome's `recorded_at`, not a potentially backdated evidence occurrence time, so an evidence record added later does not move delivery into an earlier day.

Each total carries its domain, size-scale version, definition-of-done version, and available model and tier. Compare matching cohorts only. Different domains and size-scale versions can use different units, so their points are not pooled. Closed-sprint velocity is reported only after the sprint closes.

The current backend records no daily availability or actual-place observations. Those values and `zero_output` remain null, including on days with no recorded output. Unknown-size tasks remain counted separately from zero-sized work. Cycle and delivery-wait ranges use recorded lifecycle times; unfinished delivery waits are listed as right-censored counts without inventing an elapsed duration.
