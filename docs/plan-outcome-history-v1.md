# Plan outcome history v1

The owner can read one plan's committed and actual history at `GET /journal/plans/{id}/outcomes` and download the same JSON at `GET /journal/plans/{id}/outcomes/export`. Both paths use the current request environment and require the plan's owner. A plan in another environment is not found. Organization and solo plans use the same shape.

The export is a read projection of existing sprint, size, outcome, and delivery repositories. It creates no analytics rows. Its top-level fields are:

| Field | Contents |
| --- | --- |
| `schema_version` | `plan-outcome-history-v1`. |
| `scope` | Environment and plan IDs, title, current state, and organization or solo mode. |
| `estimates_mode` | The current `estimates.mode`, including `off`. Off does not hide already recorded history. |
| `availability` | Frozen capacity assumptions when present; otherwise `not_measured`, with no invented zero capacity or observation count. |
| `sprints` | This plan's sprint memberships, frozen commitment snapshots, and later scope changes, with actor and recorded time. Other plans' memberships and changes are omitted. |
| `tasks` | Each task's immutable size revisions, execution summary, event facts and cohort keys, current delivery projection, measurement availability, and quality flags. |
| `delivery` | This plan's current domain-delivery status and append-only evidence history, including prior generations. |
| `data_quality` | `complete` or `incomplete`, with each unavailable measurement named. |

Estimate facts use their recorded time and actor. Outcome facts retain both the row actor and source actor, occurrence and recorded timestamps, policy version, cohort version/key, and cohort dimensions. Sprint commitments and changes retain the creator and recorded time. Delivery evidence retains its evidence timestamp, recorded time, actor, assurance, policy version, and generation.

Missing facts are represented explicitly. Active time is `null` and `not_measured` without a reliable task-start fact. Block and wait intervals are `null` and `not_measured` without durable intervals. Cost is `null`, labelled `Not measured`, without worker-spend facts. Delivery time is `null` and `not_evidenced` without currently accepted domain evidence. Legacy or imported rows with no reliable timestamps are flagged incomplete; the reader never invents start, block, cost, capacity, or deployment values.

The route remains readable while estimates mode is off, so persisted migrations and older history stay inspectable. Reads use scoped repositories and cannot enumerate another environment's plan rows.
