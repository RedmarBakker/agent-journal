# Version 4 notes

Working notes for the rewrite. Decisions taken, and what is still open. Update as we go.

## What version 4 is

The same product, rebuilt simple: one SQLite database, one `journal` package, one small
supervisor. `v3.bak/` is the old tree and is the guide, never imported.

## Decided

- **Layout**: Laravel-style inside one package, `src/journal/`: `models/`, `repositories/`,
  `db/`, `hooks/`, `features/`, `http/`, `console/`. One concept lives in one file.
- **Models are data only.** Frozen dataclasses. `Model` has id and timestamps; `Scoped(Model)`
  adds `environment_id`. Two levels of inheritance, no more.
- **Every write names its actor.** `Actor` is system, agent (by session) or user (by id),
  stored as one `kind:id` stamp. `Model` carries `created_by` and `updated_by`; `Entry`
  carries `actor`; every `ModelEvent` carries `by`. `Repository.save(row, by)` and
  `delete(row, by)` take it explicitly, so nothing is written anonymously. A `Request` knows
  its actor (`http/identity.py` reads it: the hook's agent, the viewer's user token, or the one
  local user), and a `Command.run(args, by)` gets it from the console (`JOURNAL_SESSION` means
  the agent, else the local user). `User` is a model from the start, so a shared journal with
  many users needs no change to the base.
- **Relations are rows, never columns.** `Link` joins any two rows by `Ref` (type and id)
  with a `kind` that says what it means. Models declare no relations. `Links` checks both
  ends exist on save; `UnlinkDeleted` removes a deleted row's links.
- **Repositories own the queries.** `Repository[M]` for CRUD, `ScopedRepository[S]` adds `in_()`.
  A model's own repository adds only its own queries. No ActiveRecord, no global connection.
- **One SQL funnel**: `db/connection.py`. Nothing else executes SQL.
- **A query is composed, never written (2026-10-21, task 1136).** A repository builds each read and
  write with `db/query.py`, `self.query().filter(state=...).order_descending("id").limit(n)`, and hands
  it to `selected`, `counted`, `maximum`, `repeated` or `purged`; the builder renders the text and the
  connection runs it. A column the table lacks raises `UnknownColumn` as it is named; `data->key` is a
  JSON path. The methods are `filter_*`, not Laravel's `where_*`, because the naming rules ban `where`,
  `in` and `by`. `SqlOutsideDatabaseLayerDetector` flags SQL text outside `src/journal/db/`.
- **Dependency injection** through `container.py`: constructors name what they need by type.
  No globals, no service locators in bodies.
- **Task, not to-do.** A task carries its own state, start, finish and log lines (`TaskLog`
  rows). The old split between to-do and work is gone.
- **Model events, Laravel style.** `journal/events/`: `Saving`, `Creating`/`Updating`, `Created`/
  `Updated`, `Saved`, `Deleting`, `Deleted`, each carrying the model. The repository fires them
  on the `Bus` at each step of a write; a `-ing` listener may refuse. Hooks arrive as
  `HookReceived`; listeners answer with a `Decision` and the receiver folds them into one.
- **Entries** are the append-only table of what happened (`Entry`, `Entries`); hooks and
  commands both write to it. The in-process word is event, the stored word is entry.
- **Supervisor** is its own package, `src/supervisor/`, stdlib only, never imports `journal`: since plan 8 a thin process host started from a launch file the journal writes (see The thin supervisor).
  It owns the agent's pty, keeps the journal server alive, and carries out instructions from
  a unix datagram socket: `Type`, `RestartAgent`, `RestartJournal`, `Stop`. Nothing else.
- **One class per file**, named after the class in snake_case. Enums included.
- Style: no clutter, small methods, no big if-chains (dispatch on type), docstrings one line
  and only for a non-obvious why.

- **Server**: one process, `journal serve`, started and kept alive by the supervisor. A
  `ThreadingHTTPServer`: each request on a thread. The hook is `hooks/hook.sh`, a curl to
  `/hooks/<agent>` with the body on stdin; it decides nothing and exits 0 when the server
  is away. The port is read from `.journal/port`. The server takes the port this project had
  last, else the first free one from 8420 to 8439, so journals of many projects run side by
  side; `JOURNAL_PORT` names one exact port and `0` any free one. The `journal` shim runs the
  package itself when the port file names a server that no longer answers.
- **The schema follows the models.** `Schema.create` makes each table from the model's fields
  and adds a column a model gained since the table was made (`ALTER TABLE ADD COLUMN`);
  nothing is dropped or renamed by itself. Numbered migrations are for the rest.
- **Events are two families.** `events/models/` are the Laravel model events. `events/agent/`
  are what the agent did, one per hook kind: `SessionStarted`, `PromptSubmitted`,
  `ToolStarting`, `ToolFinished`, `Compacting`, `Idle`, `SessionEnded`, `SubagentStarted`,
  `SubagentEnded`. `hooks/translation.py` is the one table from hook kind to event. Features
  listen to agent events, never to raw hooks.
- **The agent is a state machine, and the state is the truth.** `models/agent.py` has a `state`
  column and a `data` dict the state fills (task id, plan id, sequence and step). One flat
  state at a time, no substates; what two states share is inherited, one level
  (`FollowingPlan(Working)`, `RunningSequence(Working)`). A state is a frozen dataclass in
  `engine/states/`, with a method per agent event named after it in snake_case; an event with
  no method changes nothing. Each state declares `allows`, the `Permission`s the agent has
  there. A method returns a `Transition`: the next state, nudges, an optional refusal.
  `engine/machine.py` is the one blocking listener on every agent event; commands move the
  agent too (`task start` -> Working). Starting states: Idle, Working, FollowingPlan,
  RunningSequence, Awaiting, Waiting, Stuck, CatchingUp, AtMark, Subagent, Ended. The last
  five extend `Paused`, which holds `resume` (the state it left, serialised) and goes back
  with `back()`; a pause inside a pause nests in the data, so no stack is kept anywhere.
- **A span a state waits out is a `Timeout`** (`support/timeout.py`): `Timeout.minutes(15)`,
  `.seconds(30)`, `.tool_uses(25)`, `.edits(50)`, `.marks(1)`, started or reset at a moment the
  event carries (its time, its tool-use count, a count of edits or context marks) and asked
  `is_elapsed` at a later one. A state keeps one as a field (Awaiting's next-task delay and
  check reminder), stored as a dict in its row's data and restored by its field's type.
- **Settings, not states**: auto mode and the work mode (hands-on, orchestrator, solo). They
  change what a state allows or says. Liveness (alive, compacting now) is not a state either;
  the viewer derives it from the last event's time.
- **How workers test** (`workers.testing`, settings Workers tab and the workers list): Hand the tests over, the default, or Run the tests it wrote. With hand-over the profile text and the dispatch template say a worker runs no test, its proofs name the tests and their commands, and a worker's test command is refused.
- **The runtime is the server process.** `runtime.py` keeps three threads: HTTP, the
  `Deferred` worker and the `JobRunner`. Every background poller is a `Job` with a
  `tick(time)` and its own `interval_seconds`, registered with the runner, never a thread or
  wait loop of its own: the `Clock`, which tells `Ticked` for every live agent every five
  seconds so a state can act on time, the `MenuWatcher`, and each feature's `jobs`. A tick
  that raises is logged and the job ticked at its next turn; one over a second is logged and
  told on the bus as `SlowTick`, which the faults feature says to the agent when the
  Developer setting asks. The machine holds nothing between events; the agent row is the
  state.
- **Hooks are deferred by default.** A feature's `AgentListener` has `blocking = False`: the
  server records the entry, replies to the agent, then runs it on the one `Deferred` worker
  thread. A listener that must answer before the agent goes on (the write gate, a hold)
  declares `blocking = True`, and only a blocking listener's `Decision` reaches the agent.
  Never the other way round: a deferred listener cannot refuse.
- **Threads and SQLite**: WAL mode; one sqlite connection per thread for reads, one process
  lock for writes inside `Connection.transaction()`.

- **Features register states; features depend on the engine, never the reverse.** The engine
  holds `AgentState`, `Paused`, `Transition`, `Machine`, `Nudger`, the catalogue and the
  generic `Ended` and `Subagent`. Every other state lives in its feature's `states/` folder:
  tasks (Idle, Working, Stuck), plans (FollowingPlan), helpers
  (Awaiting), questions (Waiting), memory (AtMark), briefing (CatchingUp). A feature off
  takes its states out of the catalogue; an agent found in one goes back to Idle.
- **A feature lives beside the states.** It owns its states, its nudges (declared `Nudge`
  constants with templates), its state-free listeners, its commands and its settings.
  `features/standard.py` lists what ships.
- **Who decides a nudge**: the state decides when (naming a nudge in its `Transition`), the
  feature decides what and whether (words and switch). A state-independent line is decided
  by a listener. One line, one decider. A state talks to a feature only by naming its nudge;
  a feature talks to the state only through `machine.move`. A state never owns a line: it names a feature's
  nudge in its `Transition` (`Tasks.CARRY_ON.about(task_id)`). A switched-off feature's nudges
  are silent wherever a state names them, so no state checks a switch.
- **A nudge is not a model.** It is a declaration on a feature (name, template) and, once
  said, an `Entry` of kind `nudge` in the same timeline as the hook that caused it. The
  `Nudger` in `engine/` renders it, queries the entries to drop a repeat, writes the entry
  and delivers. Readings nudges are not stored: the state says them again and dedupe
  decides. No nudge page, no nudge commands; wording is a feature setting if ever needed.
- **Delivery**: a nudge born in a transition rides back in the hook's answer (context, or the
  Stop hook's carry-on); one born later (clock, deferred) is typed in through the supervisor.
- **Not ported: boards, kanban, tickets, hosting.** The board is re-envisioned later.

- **Providers.** `providers/`: `Provider` answers four questions about Claude or Codex and no
  more: the transcript path, the resume arguments, which tools write, and how to wire the
  hook into its settings file. `TranscriptReader` yields `Turn`s from the conversation file.
- **The agent's chat** arrives as `TurnWritten` (from the MessageDisplay hook, or the
  transcript); message tags are a listener on it.
- **Settings** are rows: `Setting(key, value)` per environment, with environment 0 the
  project's, laid over. The `Registry` reads switches from `Settings`.
- **Context** comes from Claude's statusline (`hooks/status.sh` writes one file per session);
  `ContextFile` reads it and `Translation` puts it on every `AgentEvent.context`.

- **Instructions files.** The journal injects its law and its briefing only into AGENTS.md,
  between its own markers; CLAUDE.md imports it with `@AGENTS.md` and carries the project's
  own design philosophy, which the journal never writes and never injects anywhere: it is
  for developing the journal itself, not for any project the journal is installed in.

## Done so far, beyond the core

- tasks: Idle, Working, Stuck; task and halt commands; still-open after a quiet quarter hour;
  the same check three times; done names the next open task.
- plans: Plan with tasks linked `in_plan`; plan create/add/start/park/show/list;
  FollowingPlan starts the next task when one is done and ends the plan after the last.
  Deferred: phases, checkpoints, review reports, approval.
- messages: message send/list/read; unread user messages put before the agent at start,
  prompt and stop; every agent turn recorded as a message; `[!reply:N]` answers and reads N.
- questions: question ask/answer/list; Waiting leaves and returns; a prompt answers in place;
  the answer is typed in through the supervisor.
- memory: fact, rule, reminder, nothing; AtMark at 25/50/80 percent.
- briefing: ready, rules, facts, reminders at every session start.
- A compaction hook carries nothing to the agent (Claude reads no context on PreCompact), so
  no state says anything on Compacting; the context marks ask before it. LOG_FIRST is gone.
- Deferred from tasks: work put off in words (needs a text heuristic), closed by commit
  trailer, auto mode's carry-on timing.

## Decisions taken while building the features

- A feature's listeners go on the bus wrapped in `Switched`, which runs the inner listener only
  where its feature is on; so a switched-off feature has no listener running, by construction.
- **The environment is a scope (2026-10-16, task 191).** `repositories/scope.py` holds the
  environment of the thread of work in a contextvar; a scoped repository reads it, so its reads
  take no environment (`messages.unread()`, `tasks.in_state(TaskState.PARKED)`) and refuse with
  `Unscoped` when none is set, and a new row that names no environment is placed in it (entries
  and settings name their own: 0 is the project's). It is set where work enters: the router
  (the header's environment, looked up at the first read that needs it), the hook receiver, the
  console's run, the worker thread and the deferred worker (each piece in the scope it was added
  in). What crosses environments sets it per environment through the same object: the clock per
  agent, `Switched` per event (a feature's listener runs in its event's environment, 0 for an
  event in none), the nudger and `Turn` per agent, the viewer's summary per environment, a chart
  trial in the environment it names. `find` and `all` stay unscoped. The engine's own calls that
  take an environment id (`machine.move`, `SupervisorLink`, `Cards`) keep it: they are not reads.
- The machine fires `StateEntered(session, environment_id, left, entered)` on the bus whenever
  an agent's state name changes, by event or by command. It is a plain Event, not an AgentEvent,
  since no hook reported it. Skills are required on it; nothing listens to Agent `Updated` for
  state changes, since a row can change for other reasons.
- A `Skill` names the states it is `required_in`; Idle requires nothing, so a fresh session
  reads the journal skill only. A keyword in a prompt requires that skill too.
- The console appends `created: task 3 "title", link 7` to every command's output, listing every
  row created while it ran that the system did not make itself, by the command or by what its
  events caused; `Creations` is a bus listener with a per-run list.
- A command's dispatcher is `perform`, so a verb may be any word, `run` included. A state's
  fields never shadow its methods (`on` is the method; Awaiting holds `workers`).
- Skills, triggers, checks, the shell runner and etiquette are built; the feature table is complete.
  A check runs `subprocess` in the project root with a ten-minute cap, on demand or on the
  clock; the clock also dispatches a journal-wide `ClockTicked`.
- Every card in the chat is one of two kinds (task 1424, 2026-10-23). A moment card (`MomentCards`)
  shows a moment as it was and is never updated. A process card is a class of its own per process,
  extending `ProcessCard`, listed in its feature's `process_cards` and written through
  `ProcessCards`. It is updated in place by its key, and while it is active the viewer asks its
  `refresh` once a second through `GET /cards/active`. A card's data says which kind it is
  (`card_type`). Docking stays a placement of a message, not a change to its card. "Mark" and "live"
  are on the project's banned-word list, so the code says card, moment and process.
- A row recorded from a source that can repeat is keyed where it is built and stored through its
  repository's keyed funnel (tasks 3422 and 3453, 2026-10-26): `Messages.recorded`, `Entries.recorded`,
  `ScheduledJobs.recorded`, `Links.linked`, the commit card by its key in the environment. The hook script
  names each firing (`X-Journal-Hook-Id`, its pid and first start), the same when it sends it again, so a
  hook is one entry under `Hook.key()`. A hook sent again is answered from that entry, its refusal or a
  go-on, and reaches no listener. The event carries the key as `hook_key` for the rows it brings
  (`VoiceKey.hooked`). A hook without the header is unkeyed, as before. `StoredCheckOutsideFunnelDetector`
  flags a recorder that decides by its own check, or a listener on the agent's events that saves a
  message with no key.

## Skills (built as proposed)

A skill is a feature's teaching: each feature declares one `Skill` (name, body, keywords, the
states it is needed in). The skills feature writes them from the registry into
`.claude/skills/journal-<name>/SKILL.md` and `.agents/skills/` at install and upgrade, so the
project never hand-holds them. Loading is forced by the engine, not left to the agent's loader:
- `SessionStarted`: the `journal` skill is required, plus the skill of the state the agent is
  in (resumed Working needs tasks).
- Entering a state (Agent `Updated` with a new state): that state's feature's skill is
  required if not loaded this window.
- `PromptSubmitted` naming a skill's keyword: that skill is required.
- Required means a `LoadingSkill` paused state: writes are held and the agent is told
  "load X before anything else"; a `ToolFinished` that read that SKILL.md lifts it. Loaded
  skills live on the agent row (`skills_loaded`, with the file hash) so a changed skill is
  stale and required again, and a new window (compaction) clears the list.

## v3 features, sorted

Became states: work_tracking (Idle, Working), awaited (Awaiting), catching_up (CatchingUp),
memory_checkpoints (AtMark), plans' flow (FollowingPlan),
ask_questions' hold (Waiting), halt (Stuck), subagent tracking (Subagent).

Features to port first, with what they fold in and what they say:
- briefing: session_briefing, recital, skill_loading required. Ready on env, rules in force, facts, reminders, load these skills.
- memory: facts, rules, reminders, memory_checkpoints, rules review. Keyword whispers, rule review, moves the agent to AtMark.
- tasks: work_tracking's rest, put_off_work, close_from_commits. Carry on, still open, unlogged, next, deferred in words, commit closed rows, same check N times.
- messages: messages, acknowledgements, message_buttons, message_todos. Inbox, answer before anything, reaction only, paragraphs, bare numbers.
- questions: ask_questions. Answered so act, waited a day, choices in prose.
- plans: plans. Started, phases, to-dos, ready, reviewed, approved, parked.
- sequences: sequences. Next step, step stalled.
- workers (was helpers): helpers, helper_worktrees, awaited's lines. A subagent only reads; a worker writes, in a worktree of its own. Reported, stopped, refused, idle, quiet, worktree behind.
- laws: journal_laws. Refuse a dispatch without model or job, long read refused, large result.
- skills: skill_loading. None loaded, stale, required.
- triggers: triggers. Nudge, instruct, held, denied.
- checks: checks. Failed, failing again.
- commands: long_commands, heavy_runs. Held, moved to background, forgotten after.
- etiquette: chat_etiquette, form_of_address, command_tags. Voice, shop talk, tag hint, tag refused.

Settings, not features: work_modes, auto mode, permission_prompts routing.
Server-side, no nudges: updates, archive (auto_archive, runtime_cleanup, revisions, kept_rows), sessions liveness (agent_sessions, starting_agents).
Later: suggestions, templates, dumps, collections, attachment_descriptions, record_audit, source_links, git (git_actions, pull_requests, worktrees, file_feed), sharing, phone, connection, plugins, secrets, linear, gmail.
Viewer only: status_bar, open_viewer, family_tree, terminal, thinking, history_searches, report_dock, avatar, figure_floors, agent_profiles, organization, critique, session_recording, browser_control, dev_faults.
Dropped: boards, kanban, tickets, hosting.

## To a version you can test in a browser (decided 2026-10-15, in this order)

A. **Providers answer hooks in their own shape.** Claude ignores `additionalContext` on Stop
   and reads exit 2 with stderr as "do not stop, here is why"; so on Stop a nudge is a refusal
   of the stop, and on SessionStart, UserPromptSubmit, PreToolUse and PostToolUse it is
   `hookSpecificOutput.additionalContext`. `Provider.answer(kind, decision)` shapes the
   Response; Codex uses the same JSON shape. Claude's hook block goes into
   `.claude/settings.json` with the statusline; Codex's into `.codex/hooks.json`.
   Resume: `claude --resume <session>`, `codex resume <session>`. Transcripts:
   `~/.claude/projects/<cwd with non-alphanumerics as ->/<session>.jsonl`,
   `~/.codex/sessions/**/rollout-*-<session>.jsonl`.
B. **`journal setup`**: makes `.journal/`, wires both providers' hooks where their folder
   exists (Claude always), writes the skills, writes the law block into AGENTS.md and the
   `@AGENTS.md` line into CLAUDE.md, and puts a `journal` shim in `~/.local/bin`. The shim
   finds the root by walking up to a `.journal`.
C. **Who ran a command.** An agent's shell has no session id. The shim sends `agent: true`
   when `CLAUDECODE` or `CODEX_SANDBOX` is in its environment, and the server attributes the
   command to the environment's live agent (the latest session not ended). A terminal is the
   local user.
D. **Supervisor bodies** and `journal claude|codex [args]` in the entry point. The supervisor
   sets `AGENT_JOURNAL_ACTIVE=1`, `JOURNAL_ENV`, `JOURNAL_ROOT` and `JOURNAL_INBOX` for both
   the agent and the server it starts with `journal.py serve`.
E. **One API, `/journal`** (task 719, 2026-10-19): the viewer, the share page, a plugin's
   program and the shim all speak it; `/api` and `src/journal/http/v3` are gone. Each resource
   has one controller and is answered as its model's own fields with `table` first and a few
   named additions (a task's `plan_id` and `worker_id`, a message's `filed`, `comments_on` and
   `mentions`, a plan's outline, an agent's activity). One list protocol for every table:
   `GET /journal/<table>?limit&before&after&since&ids&closed` answers `{rows, more, counts}`.
   Acts are `POST /journal/<table>/<id>/<act>`, named as the controller's method. Rows are
   named by their table everywhere (`tasks:12`). The viewer marks itself with
   `X-Journal-Viewer: 1`. `tests/test_server.py::test_every_route_the_viewer_names_is_served_and_version_threes_api_is_gone`
   reads every path the viewer names and fails on one no route serves.
F. **The viewer reads version 4's rows**: its catalogue of tables (titles, icons, where each is
   listed) is its own (`src/web/src/domain/tables.js`), the manifest holds only the journal's
   facts and the features with their options; `domain/row.js` reads what every row answers alike
   (title, body, closed, times as ISO strings); `domain/acts.js` names what each table offers.
   Deleted with version 3's API, having no version 4 server (the phone came back in 4.2.0): the board and tickets,
   the organisation, the hub of journals, hosting and members, the browser extension,
   suggestions, collections, update reports, layout links, agent pause and
   appoint, agent hooks, work modes, priorities, the plugin services panel, replies on shares.
   Document revisions came back in task 1227, as version 3 kept them (report 35): a DocRevision row per
   revision, linked to its document by a `revision_of` Link, written by the docs feature's DocRevisionRecord on
   every save that changes the text; a save within `docs.revision_window` minutes (30) of the last folds into the
   open revision with its change noted section by section, a later one opens the next; `journal doc revisions`,
   `revision` and `keep`, `GET /journal/docs/{id}/revisions` and `POST .../keep`, and the strip and section diff above
   a document. No restore, as in version 3; the phone and the share page do not show revisions yet.
D2. **The boot menu** is version 3's, rebuilt in the supervisor and moved to the journal's launcher (`src/journal/launcher`) in plan 8: a banner, then one question
   at a time under it, moved through with ↑ ↓ (or j k), a number to jump, Enter to pick and
   Esc to leave; the space under the banner is cleared before each question. It asks which
   environment (badges: agent working, last used; or a new name), whether to carry on the last
   conversation (then the other questions take last time's answers, as version 3 did), whether
   to run without permission prompts (`--dangerously-skip-permissions` for Claude, the bypass
   flag for Codex) and whether to set aside the hooks that are not the journal's for the run,
   asked every time as an opt-in, listing the files found to hold any (version 3's clean slate: `OtherHooks` copies each
   file to `.journal/runtime/set-aside`, leaves only the journal's blocks, and puts the hooks
   key back when the agent exits, keeping edits made to the rest of the file meanwhile; a run
   that died is put back at the next launch; the journal's own hook is known by the one path
   `journal/hooks/hook.sh`, so version 3's hook.sh counts as somebody else's). The journal's
   own hooks always run. The answers
   to the last two are remembered in `.journal/launch.json` as the next defaults. The
   environment screen deletes with x: on the environment under the cursor, after a confirmation,
   it goes with everything recorded in it (`journal environment delete <name>`, which is
   `Environments.wipe`: every scoped table's rows in one transaction, then the row); one an
   agent is working stays. `--env`, `--new`, `--skip`, `--aside`, `--yes` and `--no-open`
   answer it without asking; without a terminal the same questions are numbered lines. The
   supervisor stays stdlib-only: it asks `journal.py environment json` for the list. Not carried
   over from version 3: taking over an environment another agent holds (version 4 has no
   eviction) and filling the chat from an unseen conversation's transcript.
   Once the agent starts the screen is cleared and the agent has it whole but for one line at
   the top (`Header`): the package on the left, project and environment centred, the viewer's
   URL on the right once the journal answers. The agent runs in a scroll region under it with
   one row less, and its clear-screen and home moves are rewritten to the row under the line.
E2. **Pagination.** Every index endpoint answers a page, newest first: `?limit=` (default
   50, at most 500) and `?before=<id>` for older rows. `Repository.page(limit, before,
   **fields)` is the one query. The viewer asks for a page and offers "Older".
F2. **The built viewer is committed** in `src/web/dist`, so `journal setup` and `journal serve`
   work from a clone without node; `npm run build` in `src/web` refreshes it.
G. **Run it for real**: `journal setup` in a scratch project, `journal claude`, the viewer in
   a browser, fix what breaks.

## Where it stands (2026-10-15, later)

The journal's lines about messages are short and name numbers, never words: `new message 4`
(typed at once through the supervisor, `InboxOnArrival`), `new messages 4, 5, 6`, or past three
`7 messages unread: journal message unread`; the same forms at start, at a prompt and at a stop
(`Messages.inbox`). The words and the reply hint (`reply with [!reply:N] in your turn`) reach
the agent from `journal message read <n>` or `journal message unread`, which mark them read.
Every line the journal types starts with `[journal] `, put on in `SupervisorLink.type`, the one
funnel, and law L6 says what the mark means. The supervisor types the line and presses Enter
half a second after the line has reached the terminal (`Terminal.ENTER_AFTER`), and every piece,
a key, a line, an Enter, goes in a write of its own: read together, Claude takes them for a paste
and keeps the line in its input, as version 3 found and as the box showed on 2026-10-16 when the
Enter was counted from the queueing and went in behind a line still waiting for a slow reader.
Seen on the first dogfood run: two messages from the chat reached the journal and nobody told
the terminal.

Version 3's viewer runs whole on version 4's server, checked page by page in a browser with
no console errors: Home (chat with replies as comments, commit badges, the status line, the
avatar), Tasks, Plans, Documents, Sequences, Triggers, Checks, Code, Collections, Resources,
Settings (version 3's full tree, feature switches live), Journals, Agents. A real Claude
session through the hooks replied in the chosen voice, wrote, committed, and the chat showed
it all. The boot menu is version 3's arrow-key picker and opens the viewer once the port
answers. A session driven through a pseudo-terminal passed the menu, started Claude with the
hooks, and the journal recorded the session start, the briefing nudges and the session end.

Found on the first real run here (2026-10-15 morning): the viewer's message post crashed with
"table messages has no column named idempotency", because the database here was made by an
earlier build and the schema never added columns; fixed by the schema adding them. The port
was fixed at 8420 for every project; fixed by the range.

## Where it stood before the viewer decision

Done and run for real: setup, the server, the hooks with a real Claude session (briefing, inbox,
skill hold, gate, chat recorded with reply tags, task started from inside the agent), the
viewer in a browser with the avatar on the chat's bubbles, voices, profiles, pagination.
The supervisor is proven with a shell agent in a pty; `journal claude` interactively is the
first thing to try by hand.

Still to do, in rough order:
- Workers spawn from the journal itself (`worker_runner.py`), outside the supervisor and its protocol.
- Resume after a restart of the agent is tried live (plan 8, task 453): it comes back on the same conversation. Codex runs on
  the thin supervisor, but its hooks did not reach the journal in a fresh project, so its resume is untried (task 461).
- The context figure needs Claude's statusline, which runs only interactively; untested.
- Reports and docs have models and routes but no page; no page for workers, checks, sequences,
  triggers; no hub of journals; no sharing; no plugins.
- Memory keyword whispers and the rule review; put-off-work; closed-by-commit; auto mode and
  work mode settings; permission prompts routed to the viewer.
- Panes read from the entries: file edits and the terminal.
- Chat marks drawn today: commit badges (from the git feature's entries), skills loaded; not yet: subagent marks, thoughts, whispers, test-run cards, reactions.
- Install from a clone or a release (`install.sh`), upgrade and migrations; the `.pyz` build.
- `v3.bak/` can go once nothing is left to read from it.
- A message is one shape whoever wrote it: GET /journal/messages serves the user's and the agent's
  alike, and the chat draws a reply with a one-line quote of what it answers. A comment is a message
  linked to its row as comments_on, listed under it by GET /journal/comments.
- The work mode (Builder, Orchestrator, Solo) is the workers feature's `workers.mode` option,
  set by `POST /journal/mode` from the plan bar; nothing in the journal reads it yet, as under
  version 3's last route. The pause button moves the agent into the pausing feature's
  `paused` state (`POST /journal/agents/<id>/pause` and `/resume`): every tool call is
  refused until the user resumes it or writes to it.
- Open: a worker's transcript has a route but no pane in the viewer; an automatic update's
  "Not now" has no route to cancel it; the context control no longer says when the
  conversation was last compacted.

## The plan

Each phase ends with something that runs. Phases 1 to 5 are done and proven by `tests/`
(`pytest`, about a second). The CLI goes through the server since phase 2.

1. **Data.** `Connection`, `Schema`, `Migrator`, `Model`, `Repository`, `ScopedRepository`,
   `Actor`, `Link`, `Links`. The model events fire. Proof: a test creates, links, updates and
   deletes a task in a temp database and sees every event with its actor.
2. **CLI.** `Container`, `Console`, `Command`, `TaskCommand`; `Environment`, `Message`,
   `Question`, `Fact`, `Rule`, `Reminder`, `Report`, `Doc`, `Entry` and their repositories.
   Proof: `journal task create/start/log/done/list` against `.journal/journal.db`.
3. **Server.** `Server`, `Handler`, `Router`, `Request`, `Response`, `Identity`, the task
   routes, `journal serve`. Proof: curl creates and lists tasks.
4. **Hooks.** `hook.sh`, `Hook.parse`, `Translation`, `Receiver`, `Deferred`, `Decision`,
   `Entries`. Proof: a posted PreToolUse lands as an entry and answers 200.
5. **Engine.** `Machine`, `StatesCatalogue`, `Transition`, `Nudger`, `SupervisorLink`,
   `Clock`, `Runtime`; the tasks feature's Idle and Working with their nudges. Proof: a
   write in Idle answers 409 with DECLARE; after `task start`, Idle on Stop says CARRY_ON.
6. **Supervisor.** `Terminal`, `Inbox`, `JournalProcess`, `Supervisor`, `Launch`; the four
   instructions. Proof: `journal claude` runs Claude under it, a typed line arrives, a
   restart resumes.
7. **Features, one at a time**, each with its states, listeners and nudges, and the
   settings page entry: briefing, memory, messages, questions, plans, sequences, helpers,
   laws, skills, triggers, checks, commands, etiquette.
8. **Viewer.** Read `v3.bak/src/web/src/api/client.js` for the endpoint list; serve the
   viewer; add routes until it is whole; then the phone.
9. **Install and upgrade**, docs, the generated skills, migrations from v3 if any.

## To settle later

- **Resume arguments per agent.** `RestartAgent` carries them; the journal builds them from the
  hook's session id. Claude: `claude --resume <session>`. Codex: `codex resume <id>`, to confirm.
  Where the journal stores the current session id per environment, and what happens when the
  agent is restarted before any hook has reported a session.
- **Who writes the hooks into `.claude/settings.json` and `.codex/hooks.json`**, and when they
  need an agent restart (an installed MCP server does; does a hook change?).
- **Which old features survive**, and in what order. First guess at the core: environments,
  tasks, messages, questions, memory, reports and docs, plans, the write gate, viewer, CLI.
  Candidates to drop or defer: helpers, tickets, boards, plugins, phone, sharing, hosting,
  Linear, Gmail, the avatar, the Chrome extension.
- **CLI and the database.** The server is the one writer. Decide whether `journal task ...` run
  by the agent posts to the server (consistent, one process) or opens the database itself
  (works with no server up). Leaning: post to the server, fall back to direct when it is away.
- **Live updates to the viewer**: long-poll or server-sent events off the same threaded server.
- **Users on a shared journal**: how a user token is issued and checked, and whether
  environments are shared per user. `Identity` is the one place to grow.
- **Subagent sessions**: a Claude subagent's hooks carry the parent's session id with an
  agent id; today a new session id lands in Idle and would be refused writes. Decide how a
  subagent is told apart (SubagentStarted carries its id) and put it in the Subagent state.
- **Hook output per provider**: today a nudge rides back as `additionalContext` for every
  hook; Claude's Stop hook needs `{"decision": "block", "reason": ...}` to make the agent
  carry on, and PreToolUse context is shown to the user, not the agent. The provider should
  shape `Decision.as_hook_output` per hook kind.
- **Permissions**: `allows` is declared on every state; since the work command went (2026-10-16) nothing refuses a write for lack of a task, and `allows` has no user.
  The gate should read `allows` generically (a tool that writes needs WRITE_FILES) so a new
  state cannot forget to refuse.
- **Hook timeout**: 5s in `hook.sh`; what a refusal looks like when the server is slow.
- **Where the database lives**: `.journal/journal.db`, and what else stays in `.journal/`
  (settings, runtime socket path, logs).
- **Links left by a wiped environment**: `Environments.wipe` deletes the scoped rows but a link
  whose refs pointed at them is only removed if the link row itself was in the environment.
- **Migrations from v3** records: decided 2026-10-19 (task 605): start empty, and bring in version 3's documents with `journal doc import <its project/doc folder>`, once; a doc already titled here is left. Other records stay in version 3.
- **Plans**: model shape (phases, checkpoints) once tasks stand.
- **State method injection**: a state method asks for rows by type (`task: Task`); decide
  whether the machine resolves them from the state's data before the call, or the state is
  handed repositories. Leaning: the machine resolves, so states stay pure.
- **Permissions vs the gate**: `allows` says what a state permits; the Idle refusal of a write
  is the first use. Decide which tools count as a write per provider (one table).
- **Viewer**: keep `v3.bak/src/web` as is and repoint its API client, or rebuild it smaller.
- **Install and upgrade**: `install.sh`, `install.py`, the `.pyz` build and the self-update
  loop are all old; decide the new install path before touching them.
- **Tests**: pytest, `tests/`, one file per phase proof, a temp database fixture, no mocks,
  core only; no tests on single models or features until the core stands.
- Old root files still to deal with: `docker/`, `install.py`, `install.sh`, `pytest.ini`,
  `conftest.py`, `.coveragerc`, `plugins.json`, `.githooks/`, `.codex/agents/`.

- **docs/messaging-and-chat-marks.md** holds the requirements for the chat, read from version 3 on 2026-10-15: your messages, the agent's words, tags, replies, reactions, marks, etiquette, and what version 4 still lacks.
- **Messaging, second batch (2026-10-15).** The whole turn is gathered in the hook layer
  (`TurnGatherer` under `Translation`): every `TurnWritten` carries the text so far and its delta, so
  the recorder and the etiquette listener read the same whole on the final one. Reactions are a model
  (`Reaction`: face, author) linked to the message by a `reacts` link, toggled by `journal message react`
  and the viewer; the user's face is typed to the live agent on the link's creation; a turn that is only
  a face is not posted. A turn answering a `[journal]` prompt with no file written since is kept as an
  acknowledgement (a column on the message) and hidden by the viewer's default. Em dashes and
  run-together paragraphs are nudged. Subagent marks come from the Agent tool's start and finish in the
  agent shaper. Found on the way: `UnlinkDeleted` existed and was never registered; it is now.
- **The agent introduces itself (2026-10-15).** On a fresh conversation (`SessionStarted.source ==
  "startup"`, never on resume, clear or compact) the voices feature types `introduce yourself to the
  user in the chat` four seconds after the start hook, when Claude's prompt is up. Typed lines now carry
  `after` seconds and go in one at a time in the order sent (`Terminal.type(line, after)`, `pump`).
- **Messaging, third batch (2026-10-15).** `Tags` (messages feature) reads every command tag at a
  line's start; `RunTags` runs the command each stands for through the console with the turn's words
  as its text (`todo`, `log`, `end`, `fact`, `rule`, `reminder`), and a refusal is typed back. The
  recorder strips every tag and keeps a `log` turn out of the chat. `Cards` (engine) is the one funnel
  for marks in the chat: a check run, a trigger met, a question answered, a skill loaded, a halt.
  Each is a message of author `system`, its label the text and its kind, icon, tone, detail, row and
  session on `Message.data`, so `/api/<env>/message` serves the whole chat in one stream by number. The console
  now answers a missing row or a refusal with code 1 and the reason instead of raising.
- **A deferred failure never stops the worker.** `Deferred._work` logs a failing piece of work to the
  server log and runs the next; before, one exception ended the thread and every later deferred listener
  waited in the queue for good, silently. Found 2026-10-15 behind a reply that never reached the chat.
- **Install is one command, as version 3's (2026-10-15, later).** `install.sh` copies `src` into
  `<project>/.journal/src` (from the checkout it is run from, or a clone of `AGENT_JOURNAL_REPO` at
  `AGENT_JOURNAL_REF`) and runs `journal setup` from the copy. Setup also writes the dispatcher at
  `~/.local/bin/journal` (`journal/launcher/dispatcher.py`): it finds the project's `.journal` walking up and
  hands over to `.journal/src/journal.sh` (version 4) or `.journal/journal` (version 3's launcher), so one
  command serves both versions and nothing of the journal lives outside a project. Setup adds `/.journal`
  to the project's `.gitignore`. A wired hook first tests that its script exists. A dogfood checkout
  therefore runs from its own `.journal/src` copy: re-run `sh install.sh` after a change to try it live.
- **The drain of the discrepancy list (2026-10-15, night).** `docs/v3-v4-discrepancies.md` ends with
  what landed and what is left by choice. Workers run through `WorkerRunner`: the provider's
  `worker_command` headless on the brief, a worktree under `.journal/worktrees` when asked, the journal's
  hooks off for it, its output filed by `WorkerReports` as its report. A question through the provider's
  own tool is refused. Version 4's own API moved under `/journal`, since `/api/agents` shadowed the
  viewer's online list.
- **One inbox per environment (2026-10-15, evening).** A supervisor's inbox socket is named for the
  project and the environment, and while it runs it announces its path at
  `.journal/runtime/inboxes/<environment>`. `SupervisorLink` takes the environment id on every call
  and reads that file, so a line reaches the agent of that environment and none other; an environment
  with no supervisor hears nothing. The viewer's Start runs `journal.py <agent> --env <name> --yes
  --no-open --no-journal` detached (`AgentLauncher`): no keyboard (`stdin=None`), no journal of its
  own (a launch file with no services), its screen in `.journal/runtime/agent-<env>.log`; Stop sends the supervisor the
  stop verb. Since plan 8 the inbox is a stream socket speaking the protocol and the announce file is JSON naming it, the protocol and the screen. Deleted on the way: `JOURNAL_INBOX`.
- **The command is the project's.** `journal setup` writes `.journal/bin/journal` and nothing outside the
  project; the launch puts that folder first on the agent's PATH, so `journal …` resolves inside a
  session and nowhere else. Ruled 2026-10-15 after a dogfood setup overwrote the global `journal` of
  version 3 on this machine (restored from version 3's own shim template). Nothing of version 4 is
  published: origin holds `main` only, the last tag is v3.3.2.

- **Services the journal starts through the supervisor (tasks 2967 and 3026, 2026-10-24).** The features' declared services, the sync service among them, are started at the server's boot by ServiceStart, since a launch file outlives an upgrade; the plugin services (features/plugins/support/plugin_services.py) and the tunnel (features/sharing/support/tunnel.py) also start and stop theirs. SupervisorServiceVerbDetector names these three files as its only exceptions. A supervisor that takes the installed version's services itself, so the journal names none, is still open.
- **The team image's hosted journal starts the sync service by hand (task 2967, unproved).** docker/team-server/hosted.sh runs python -m sync_service beside journal.py serve, since the hosted journal has no supervisor; the image has not been built or run with it.
- **Health checks (task 2973, 2026-10-24).** Every service declares its health check as plain data, so the supervisor knows nothing of what a service is (supervisor/health_check.py): a URL that must answer 200 within a timeout, its port read from a file when it names one, or a file written within a number of seconds, checked every few seconds after a grace from its start; a service that fails it three times in a row is started again and the supervisor's log says why. The launch file gives the journal service http://127.0.0.1:{port}/journal/health with the project's port file, which answers 503 naming the environment while the hook script has fired for over a minute past the last hook the server took since it started (HookArrivals): hook.sh writes the time of every hook it sends to .journal/runtime/hooks/<environment>.fired before posting it. A feature's service that names a health path (the sync service's /health) is given a free loopback port by ServiceStart as its second argument and its URL check in the start request. The agent in front gets a check of the same kind (supervisor/front_health.py): while its terminal output moved in the last 30 seconds and its hooks file has stood still for 600, longer than a long tool use, the warning the launch file gives is typed to it once, until the file moves again.

## The shell runner (2026-10-15)

- The foreground shows a part's output cut to its first and last `shell.shown_lines` lines (200); a line says how many were cut and that the whole lies in the part's file. A Read of a file longer than twice that, without offset or limit, is refused with the same guidance (`ReadNarrowly`).

- Every shell command of the agent runs through `hooks/run.sh`, set as Claude Code's shell prefix at launch. The
  line is taken apart at `&&` and `;` (`Chain`); a pipe is one pipeline. Claude's own wrapping (`source`, `setopt`,
  `eval '…' < /dev/null`, `pwd -P >| file`) is run in silence; the parts inside the eval are the agent's and are
  recorded, each with what it is doing (`Doing`), its output and its duration (`running` and `ran` entries).
- A worker in the agent's own shell runs the parts in order and stops where the shell would; the foreground
  process shows each part's output as it lands. Past the limit it returns at once with the output file and the
  chain goes on in the background; the journal types one line when it ends. The limit is `shell.foreground`
  (30 s) or `shell.foreground_while_waiting` (10 s) while a message of the user's is unread.
- The bar and the terminal pane read the parts, not the tool call; a Bash call as a whole adds nothing to either.
- What stays one part: a pipe, quotes of every kind including backticks, subshells, groups, double brackets,
  parameter braces, a comment to the end of its line, a loop, an if or a case to its closing word, and a line with a
  heredoc. A bare `exit` or `exec` in a part ends the chain with that part's code, as the shell would. Output folders
  older than a day are swept at each run.
- Open: each part costs two shim calls (about 0.1 s each); run.sh could post straight to the server. A worker or
  subagent started from the agent's shell inherits the prefix, so its commands are recorded under the live agent.
- The runner's process tests are in `tests/runner_process.py`, not in the default run: the chain and the move to
  the background as a real process, and a corpus of sixty lines each run whole by zsh and in parts by the runner,
  compared on output and exit code. Add a line there for every new corner.
- Zsh's own answers, tested on 2026-10-15: only `for`, `select` and `repeat` have the short form whose body is the
  next command with its `&&` chain; `if`, `while` and `until` read on to `then` or `do`. A part before `&&` runs
  guarded so `set -e` does not end the shell on its failure, as in the shell. Known differences left: an alias
  defined in one part applies to the next (the shell parses the line first); a failed glob in zsh aborts only its
  own part, not the rest of the line.

## Thinking (2026-10-15)

- Claude writes its thinking to the transcript; the display hook never carries it. `Claude.thoughts_this_turn`
  reads the transcript's tail for the thinking blocks since the last prompt. Before each tool use the latest is
  kept in memory (`Thoughts`) for the working bubble, and a visible message clears it.
- Found by dogfooding: a reply written mid-turn can land in thinking instead of in words, and the chat never sees
  it. A thought opening with `[!reply:N]` for a message still unanswered is dispatched as that turn, so the reply
  is posted and the message answered.

## Conduct toward the agent, settled on 2026-10-15 (evening)

- Delivery (2026-10-15): every line the journal types is noted in `TypedLines` until the prompt hook brings its words back. One not seen back while the agent has sat between turns for ten seconds is typed again, three times at most, each try a card in the chat; the fourth miss is a card saying the line never arrived. The agent's turn being over is `Turn.over`, shared with the MCP restart.

- Every session start, fresh, resumed, after a compaction or a takeover, holds writes until `journal environment
  here` is run: the task in hand, open and parked tasks, messages, questions, workers, background runs, rules,
  facts and reminders in one read.
- A stop is answered, the state untouched: task in hand, "carry on", every time; parked tasks named in any mode;
  in auto mode the next open task and "sure you want to stop?"; a wait the journal owes the agent, said once. A
  wait on the user, a worker, an awaited run or a halt lets the stop pass. Work since a held stop makes the next
  stop a fresh one; a stop with no work between cannot be held again, so its line is typed instead. A halt with a
  reason is the way out.
- Messages: nudged after ten tool uses unanswered, held after fifteen (settings); a reply, a face or any word in
  the chat after the read answers. Every read ends with the choice: steering, or a task filed from it with `--from`.
- Logging: ten tool uses with nothing logged ask for a log, twenty hold the next write (settings).
- A journal command runs alone or chained only with journal commands; mixed with anything else it is refused.
- The machine answers a hook before any other listener, so listeners see the state the event led to.
- The viewer's source lives in `src/web` and builds with `npm --prefix src/web run build`; `scripts/checks/
  viewer_built.py --digest` writes `dist/built-from`. The bar shows `agent.doing` when busy without a task and the
  task's whole title when one is in hand.
- Open from today: integrations as MCP servers (task 11); the behaviour tree, the journal's conduct as an editable
  flowchart in the viewer, after ../workflows (not started, by the user's word).

## Ported whole on 2026-10-15 (night)

- Plans are version 3's shape again: a goal, phases in order with a complete-when and a checkpoint flag, tasks under
  phases (links `phase_of` and `in_phase`), a ready stage the agent sets once every phase has tasks, and the user's
  approval before `plan start`, from the plan page's Approve button or `journal plan approve`. The agent is told
  of the approval by a typed line. The shaper derives the building stage from the rows.
- Sequences may start on a row event (`starts_on`, as `plan.created`); the shipped "Building a plan" sequence is
  seeded at boot (feature `seeds`, run by the runtime) and tells the plan's steps. A run is engine flow, not a state
  and not a workflow: the runs are a stack on the agent's row (`sequence_runs`), the one in hand last, each with the
  step titles it began with and the row it is about; every start goes through `Running`; the next session takes over
  the runs of the last one that ended with some (plan 10). A step is taken up with `journal sequence follow`, or by
  running a command the step names in backticks; until then a write waits, and a taken-up step that stands for
  `sequences.stale_after` writes (25) holds the next write again. Reads, journal-only lines and subagents are never
  held. A stop is told the step once until the agent uses a tool again, and is quiet in a wait, while a question
  is open, while the run is parked and while the agent owes the look, the mark or a skill (`Requiring.owes_anything`),
  so those debts are paid first. A run's start owes the sequences skill. An unedited shipped sequence follows the
  shipped text at boot. A sequence names the states its row must reach (`finishes_in`; Building a plan: ready or
  later) and its last step is refused until then; `abandon --why --sure` gives a run up with a card to the user; a
  cancelled or deleted row, or a deleted sequence, ends the runs about it. Only the user's own words start a sequence
  by trigger (`PromptSubmitted.by_user`). The step is said again at a start, when a wait ends and every
  `sequences.say_every` minutes to a quiet agent. The agent inspector's sequence band shows the run and its last
  changes (entries of kind `sequence_run`) with Skip step and End sequence; that history is not in the chart's
  Recent runs, which is the canvas's.
- Delivery: every line the journal types is held in `TypedLines` until its prompt hook brings it back; one not back
  after ten quiet seconds between turns is typed again, three tries, each a card.
- The supervisor pins nothing to the screen any more: its line is Claude Code's own status line, read from
  `.journal/runtime/status-line`; the terminal scrolls back as it always does.
- The server runs commands one at a time: the output capture is process-wide, and two at once stole each other's lines.
- The runner shows a part's output cut to its first and last two hundred lines; a Read of a longer file without a
  range is refused.
- Still open: the avatar that keeps jumping at a perch (task 38, parked with a finding), the behaviour tree (plan 1,
  ready for approval).

## The chart (2026-10-16, plan 1)

- One `Chart` per journal; `Node` rows of three kinds (trigger, check, action) naming a catalogue entry, with a
  text and a place; lines are links of kind then, yes or no; nodes are linked to the chart by `node_of`.
- The catalogue: a trigger per agent event and per row event of every model; the checks the journal answers
  from the rows, plain and counter ones (a number or a setting's name in the text); the actions say, hold,
  block the stop, type, start a sequence; each entry marks the providers it works for.
- The walk (`features/chart/walk.py`): read fresh per event; agent events blocking after the machine, row events
  deferred; one path per trigger node, fifty steps at most; a trace entry per walk; `Actions` go through the
  nudger, the decision, the supervisor and `Running`; `Fillers` fill placeholders from the rows.
- Saved whole over `POST /journal/chart` with a revision, refused with every fault named (`Validation`); reset to
  the shipped chart; a dry run (`Trial`) for an agent event. `journal chart show|catalogue|node|line|remove|reset|try`.
- The shipped workflows carry the stop rules that were `AnswerStop` and `StopWords.for_`, and since plan 3's
  phase 2 the counter rules too (unread, unanswered, log cadence), in the base workflow and Working's; their
  listeners stay in code until phase 3 deletes them; docs/the-rules.md says what stays in code for good.
- The Workflow page: canvas with pan and zoom, palette, lines dragged from ports, text in place, draft with undo,
  list form for a phone or a keyboard, Try it dry. No release yet: version 4 is still a branch.

## The night of 2026-10-16: settled and shipped

- **Pinned links**: a `Notice` row pins a link above the chat with its label; `journal notice create "<what>" --link <url> --label "<Open ...>"`
  and `journal notice close <n>`; the user closes it from the strip; a link in the chat that no pin carries earns one reminder,
  the journal's own and pull requests excepted.
- **No work command** (the user's ruling): a quick edit needs no task and is never refused; `task park <n>`, `task resume <n>`
  are the task's verbs and `journal await "<what>"` the one wait; the log is asked after 25 edits, named every 25, held at 50 (`Tasks.*` options).
- **Options**: a feature declares the settings it reads as `Option`s (`Feature.options`), key `feature.name`, with the words
  the settings page shows; `Settings.option(PROJECT, option)` reads one. The settings page is built from them: the manifest's
  features and groups come from the registry, the tree nests the stored keys on the first dot, a save writes the keys and
  drops the ones left out. Version 3's settings fixture, its eighty features, the services and developer tabs and the
  status bar's work modes are gone. The avatar is a feature with its `shown` option. The System tab has the Project group
  (`V3Manifest.SYSTEM_GROUPS`); the Share links tab is the `sharing` feature's, with the tunler account pane under it.
- **Share links** (the `sharing` feature): a `Share` row per link, linked to the doc, report or plan it opens as `shares`;
  the share server is a second loopback listener (`ShareServer`) that answers `/s/<token>/`, its `data.json`, its assets and
  `/health`, nothing else; the tunnel is `tunler <port> --domain=<name>` run by the supervisor that hosts the journal while a
  link is open, its name and ports kept in `.journal/sharing.json`. `journal share create|opens|stop|list` is the feature's
  command and goes through `ShareActions`, the viewer's own path: a link the agent makes waits, and a message of the agent's
  with Accept and Deny buttons asks the user (a press is recorded on the message as `pressed`). A visitor's comment, on a link
  made with comments, is posted to `/s/<token>/comment` and becomes a card of the system's in the chat, linked to the row as
  `comments_on`; it is never a message of the user's, so it never reaches the agent as the user's words. Version 3's hold
  until the agent agrees, the user's button letting the agent act on it, and trusted comments through a password are not
  ported. Not ported yet either: shared views and layouts, the watchdog that restarts the tunnel. The phone is back in 4.2.0.
- **A read never makes an environment**: `Environments.existing(name)` is the one lookup for every route and answers not
  found; the runtime makes `main` at boot. The browser's stray `#/settings` had made four environments named settings.
- **The supervisor's Enter**: typed half a second after the line has reached the terminal, each piece in a write of its own;
  before, the Enter was counted from the queueing and went in behind a line still waiting for a slow reader, so Claude took
  the two for a paste and kept them in the box.
- **The Workflows page** is built from Herr Gropius's design after one critique round (first-time, words, parity): PageBar
  with the picker (Default tag), New workflow (event and name in one row, the workflow born with its trigger), Reset to
  default and Delete workflow asking by name, Undo, Discard changes, Save with the unsaved count; the Integrations header;
  nodes as cards with the kind over the title, hollow ports that take the port's colour when hooked, a plus on hover; Add
  node as a menu with search that says where the node lands and connects it; a line dropped on empty canvas offers Add node
  where it fell; Test with the workflow's own event, the result in the SidePanel with numbered steps and the path lit on the
  canvas; the list form with DropLists, no native select; the catalogue in plain words (Agent stops, Agent idle?, Send
  message to agent). The phone screen (design P1 to P5) is task 90.
- **The branch is on origin** as draft pull request 26.

## A failing node in a walk (ruling of 2026-10-16, plan 2)

The walk runs inside the hook's answer. A node that raises, a check on a state nobody foresaw or an action on a row that is gone,
would otherwise fail the whole answer and skip every listener after it, so one bad node could take the inbox, the holds and the
check-ins down with it. The walk therefore catches a node's fault, writes a `walk_failed` entry naming the node, its key and the
fault's words, ends that path and goes on with the others. This is the one place a `try/except` is allowed to catch broadly, and it
does not swallow: the entry is the fault made visible, and the page is to show it per workflow (plan 2, phase 3).

## One workflow per state (ruling of 2026-10-16, afternoon)

Plan 2, one workflow per event, is cancelled at phase 2 with its machinery kept: the catalogue, the checks, the
fillers, the actions, the replay harness and the frozen records, and the seven per-event shipped workflows that
run today. The user's ruling: a workflow per state, with a base workflow for what every state shares, is the state
class drawn, a trigger per event inside it; the state checks leave the branches, two workflows never fight over the
driving, and a workflow may move the agent to its next state through the machine. Plan 3 carries it in three
phases; report 3, five readers against "Find what is missing", is folded into it. The first task rules which state
picks the workflow: the state the machine left, read once into the walk's context right after the machine and
before the engine's holds, found by the state's class and its parents and then the base; the chart feature registers
first for that, so a session start is walked as the state the agent resumes in.

Ruled and built on 2026-10-16: the walk's Context carries the state, set once by the walk listeners and the trial
after the machine has moved; the checks and the fillers read it there and never look the agent up; the walk entry
names it. What is still to come under plan 3: the workflow found by the state's class and its parents and then the
base, the base first and the state's workflow second with one spoken set.

Ruled on 2026-10-16 under plan 3 (task 175): every state has one holder of its conduct, a workflow or the engine,
in the table "Every state, and who holds its conduct" in docs/the-rules.md; the subagent state, which nothing ever
entered, is deleted; the Stop hook's event stays keyed idle and the commands and the trial name it by its title,
Agent stops, beside the state idle.

Ruled on 2026-10-16 under plan 3 (task 176): every line still said outside a workflow is one of three in the rules
doc's table: a law or a guard that stays in code, a feature's own conduct of another kind that stays with it, or a
workflow in phase 3 once its check exists: polling, the reaction, a rule's review, the etiquette reminder and a
plan's changes, each in the base workflow.

Built on 2026-10-16 under plan 3 (phase 2): the seven state workflows, the base first, drawn from the per-event
drawings and the state rules; the older shape retires at boot, whole when unedited, its triggers alone when the user
edited it; Working, Expecting and the running state no longer say their lines; the replays' equal compares the lines
of one answer as a set, since each is an instruction of its own and only the order of the merge changed.

Plan 3, phase 2, complete on 2026-10-16 at the end of the afternoon: the development journal runs the base workflow
and the six state workflows, the older per-event ones retired at boot; thirty-six replays prove them equal to the
frozen records. Phase 2 is the plan's checkpoint: the user looks at the Workflows page before phase 3 deletes the
listeners the workflows carry. The default suite runs in thirty seconds on a loaded machine, with the replays out of
it (python3 -m pytest tests/replays_run.py) and one template journal booted per run; the server per test is what is
left to cut.

Ruling, 2026-10-16: the workflows are the project's, not a user's. A chart is a project row, so every environment
of a journal walks the same workflows, and in a shared journal every user edits the same ones; who made the last
change is on the revision (`revised_by`), and the page shows it. What differs per environment is not the drawing
but the switches: a feature switched off in an environment silences that feature's lines and holds there, since
every shipped line and hold carries its feature's key. A per-user or per-environment workflow is not a thing the
design has, and will not be until a shared journal asks for it.

Plan 3, phase 3, the free part done on 2026-10-16 in the evening: the Workflows page lists by state and notes where
each workflow runs, opens read-only behind an Edit switch, says when each workflow last ran and what last failed in
it, and marks a workflow with no trigger off; every command-line write raises the revision and a default workflow is
edited by command only with --edit-default; a hold a trigger reaches through no check is refused, a wait's workflow
with no release saves with a warning, a shipped workflow cannot be deleted; a tick's walk is recorded only when it
acted; a word from the user frees any wait not owed by the agent; a row event under an owed pause reaches the wait
beneath; the pure state checks retired and a workflow naming an unknown entry is stopped at boot; a feature switched
off silences its holds as well as its lines. The environment scope (Baron Haussmann) and the dictation fix (Mr.
Edison) are merged. What is left of phase 3 is the deletion of the listeners the workflows replaced (118, 142), the
end of listeners.off (181) and the docs after it (119): that waits on the user's look at the Workflows page, the
plan's checkpoint.

Plan 3 complete on 2026-10-16, late evening: the eleven listeners the workflows replaced are deleted in five commits,
one per workflow, each shown equal by the thirty-six replays; listeners.off, the take-over and the drawings' replaced
names are gone; the settings page names the workflow node that reads each option; docs/the-rules.md and
docs/the-chart.md say what the workflows carry and what stays in code. What stays in code: the machine and its
states, the laws, the briefing and the owed pauses, the skills, the shell runner, delivery, and the few feature
listeners that read what no check reads (voices, git, triggers, checks, mcp, plans, sequences, questions' own tool).

Ruling, 2026-10-16 in the evening, on the user's word: no base workflow. Each state's workflow carries what every
state shares, drawn by one shared drawing off the state's own triggers, so every workflow reads whole on its own; the
walk runs the state's workflow and, beneath a pause the agent owes the journal, the workflow of the state it
interrupted, so the inbox, the holds and the waits run under Orienting, AtMark and LoadingSkill. An unedited shipped
workflow is redrawn at boot when the shipping's drawings are newer (`chart.drawings_version`); an edited one is the
user's and stays. The former base is retired at boot like the older shape.

Found on 2026-10-16 in the evening, from the hook's own entries: Claude Code's MessageDisplay hook delivers only a
turn's last text block; a block followed by a tool call in the same turn never reaches it. So the journal reads the
agent's transcript at every other hook (`hooks/transcript_turns.py`, through the provider's `texts_written`), from
the byte it left off at, and handles each block written since as a whole turn before the hook's own event; a reply
written before a command answers its message at that command. The display hook's copy of the last block is matched
by its visible words and recorded once. Codex has no transcript reading yet: its replies still come only from the
display hook.

File edits are rows since 2026-10-16 in the evening, on the user's word: `Edit` is a model (`models/edit.py`), written
by the edits feature when an editing tool finishes (`features/edits`, blocking so the pane's next poll sees it) and by
the shell command for the files a part changed; the last five hundred per environment stay (`repositories/edits.py`);
the edits endpoint reads the rows, so the File edits pane shows the same after a return to the journal.

State changes on the agent's events, 2026-10-16 late: the wait lifted by the agent's own tool use moved from the
Expecting and Stuck states into their workflows (trigger Tool about to run, check The agent's own tool use, action
Release), Stuck gaining a shipped workflow of its own; the states keep only their data. What a state class still
decides on an agent event: Working's bookkeeping of edits and reminders, the owed pauses' refusals, and the word
from the user that frees any wait, which stays in the engine as the way out of an emptied workflow (task 139).
The moves the commands make, a task started, a worker dispatched, a question asked, a sequence stepped, stay
theirs. A workflow's move enters idle, or lays expecting or stuck over the agent's state (task 200).

Ruling, 2026-10-16 at night, on the user's word: one workflow per state per trigger. A chart is bound to a state at an
event and holds that one trigger; the pair has one workflow, forty of them shipped (seven states at the shared events
plus each state's own), titled "Idle at Agent stops" and so on; the walk runs the workflow of the agent's state at
the event, through the state's parents, then the state beneath an owed pause; a workflow of the user's own is for a
pair no default covers. The per-state shape and the older per-event shape retire at boot. The page was designed by
Mr. Eames in Claude Design through two critique rounds and a third cut short on the user's word (the critics are
not to be dispatched afresh per round, and a design needs no three rounds), then built to the orchestrator's own
judgement on 2026-10-16: two lists, states with mark strips and events with their status words, the one workflow
per pair, Turn off and on by the trigger, Start a workflow here and Make its own, faults under the bar by step,
the stale save naming who saved first, Recent runs as a side panel lighting a run's path, the phone the same
through its sheets; the pair logic lives in web/domain/workflowPairs.js for both. The server serves the states
with parents, edited and failed flags, off and on, faults as {node, words}, fillers, a tried flag per trigger
and runs with their nodes; row events are titled in the model's own noun with the right article.

The Profiles page, 2026-10-16 on the user's word (task 209): the agent profiles in .claude/agents listed in the
sidebar after Workflows, each with its model and how often and when last the agent dispatched it (counted from the
Agent tool's calls by subagent_type), opened in a side panel that edits when it is used (the description), its
tools, its model and its instructions, and New profile; the server reads and writes the front-matter files through
ProfileFiles and serves them at /journal/profiles. The journal's own three (researcher, planner, debugger) are marked
shipped and setup puts them back. The critic profile is gone and the designer profile has no critique rounds: a
design is one designer's work, judged by the orchestrator against what the user wants.

Worker reuse, 2026-10-16 on the user's word (task 210), as version 3 reused them since plan 21 (2026-10-21): a
worker keeps the provider's session of its last run, saved the moment the run prints it, and `journal worker send
<n> "<next job>"` gives a worker that reported, or was stopped, its next job in that session and its own worktree
and branch, so its memory of the last job comes with it; each send counts one reuse on its row. A worker still out
takes a message in its live session with `journal worker notify`, Claude only. A dispatch whose brief names files
an idle worker's branch touched is refused in favour of that worker unless `--fresh`, and a dispatch past
workers.idle_kept workers of one profile is refused while one of them is idle; reviewers start fresh. Retiring an
idle worker asks whether it could be reused and keeps the --why as its reason. A worker out silent for twenty
minutes is named once. A worker reaches only its own dispatcher's other workers, with `journal worker peers`, send
and notify. Subagents are rows written from the hook entries: the census counts the running ones against
workers.most_subagents, `journal worker list` shows them, a job on files an idle subagent read is refused with its
SendMessage line, and `journal subagent retire` lets one go.

The plan state, 2026-10-16 at night on the user's word (tasks 211 to 213): Following a plan holds the agent for the
plan's whole life. A checkpoint stands in the plan's state with no task in hand, said as "plan N, readings at a
checkpoint"; the checkpoint branch moved from Idle's stop workflow into Following a plan's own stop and start
workflows, beside the carry-on; Idle keeps nothing of plans. A plan parked or cancelled sends its follower back to
rest; a session that starts at rest while a plan is started follows it, beneath its orienting pause, at the plan's
task in hand. Every wait and a sequence are pauses that keep the state they left, so they return to the plan. A
sequence ends by its own last step and is no wait a workflow must release, so the wait warning leaves it alone.
Every state names itself (title on the class) and the states catalogue lists them all with their parents, so the
Workflows page shows every state the engine has, from the engine and not from a hand-written list; its lists are
headed State and Event and a state's row is its name and its marks. A child state ships only its own events, so
its shared-only workflows never shadow the parent's.

Counts, 2026-10-16 at night on the user's word (task 214): a workflow keeps named numbers for an agent between
events, as rows (models/count.py): Start a count puts one at nought, Count one adds one, and the checks Is a count
over N and Is a count at N read it, the text naming the count then the number or a setting. The user's rule: every
behaviour laid out in a workflow, nothing hidden in a check; task 215 rewrites the shipped conduct onto counts and
retires the hidden tool-use and edit counters, and task 216 is the proposal for moving the engine's remaining state
into workflows.

One line per port, 2026-10-16 at night on the user's word (task 217): a trigger and an action lead on by one line,
a check by one yes and one no, so a workflow is one path read top to bottom and nothing runs side by side; a
second line from a port is refused on save and replaced by command. The shipped workflows chain the state's own
steps first and the event's shared conduct after, every open end joined to the next part (DRAWINGS_VERSION 7). A
step that raises is recorded and passed by its no or then line, so one broken step never silences the chain.
The proposal for moving the engine's state into workflows is report 4, adjusted after four agents' discussion
as report 5; it waits on the user's word before a plan.

Plan 7, Everything through the workflow, approved on 2026-10-16 late at night after the user redrew the model
(messages 1133 to 1143) and three Opus reads were folded in: a workflow answers one trigger and is bound to a state
or to none (always); an event's workflows run in the place order the user drags; the laws and guards become locked
workflows at the head; Run no later workflows ends an event's walk; Orienting, Loading a skill and At a context mark become facts
the agent owes. Phase one so far: a shipped workflow remembers its shipping (drawn_version) and an edited one the
shipping moved past is kept and told so; shipped workflows are named after their drawing (state:event), a retired
one is remembered and reset by state and event draws it back; Chart.place orders an event's workflows, a state is
optional, the walk runs the event's list in order with the nearest state in the lineage replacing its parents';
one move per event, the first hold wins and later holds are recorded unanswered, the new state's workflows run at
their place after a move, the waits are placed before the states they go back to; a Run no later workflows node ends the event's
walk, warned on save for what it skips; the order endpoint and chart order take an event's list at the revisions
read, refusing a stale one naming who saved first; the page is an event list and the event's ordered list, dragged
to reorder, filtered by state; a locked workflow or step is the journal's law: the seed draws the holds locked, a
locked workflow keeps the head of its event's list and is neither deleted nor turned off, a locked step is neither
taken out, reworded (its numbers may change) nor gated by a check or a Run no later workflows of the user's, and the
DRAWINGS_VERSION bump that locks the holds in a readings journal came with the Always workflows: the tool conduct
is the locked the guards at Tool about to run (whole, the holds and the naming around them, since one path cannot be
split), the inbox and the message named are Always workflows per shared event after the locked ones, a state's
shipped workflow carries only its own steps and a state with nothing own at an event ships none there, a readings
journal's copies are released at boot (unedited gone, edited kept as the user's with the shared nodes stripped),
and A message is updated has no conduct to ship, so no Always workflow stands there yet.

Phase one closed on 2026-10-16 late: the counts replaced the engine's hidden counters. Is a count at every Nth joined
the count checks; the row checks Message just read, Task just started by this agent and Log is for the task in hand
read the event's row; counts are the engine's own table, walked by no row event, gone with the session; Always at A
message is created starts uses and namings, the Always workflow at A message is updated (now shipped) starts owed at the first
read owed; the guards count uses, owed and namings on the canvas and Working counts its edits, a held write not
counted, started at nought by a task start and a log line; Working keeps no edits or reminders and the seven counter
checks are gone from the catalogue, a user's workflow naming one rewritten to its count check at boot with the
title saying so, a Working agent's edits carried once into its count; the replays record the counts and were
re-frozen from the workflows, differing by the counts alone, with count_survives_events added; the rules reworded.
A task start moves the agent before the row is written, so the row's walk reads Working. A second boot on a seeded
journal is a no-op (tested). The suite: 230 tests, 16 s of CPU, 35 s of wall on a box at load 5, replays 40 in
about three minutes.

Phase two, in progress on 2026-10-16 late: what the agent owes is a fact on its row. Agent.oriented (false from a
start until journal environment here) and mark_owed (the mark crossed and not decided at) are columns touched
narrowly; a skill owed is a link owes:<name> from the agent, set by the Require a skill node and removed by the read
of the file; the fillers awaiting, skill_owed and skill_path read them. the Always workflow at Session starts requires the journal
skill and marks the agent unoriented, the Always workflow at Prompt sent requires the skills a prompt names, a state's workflow at
Session starts requires its own skill, every Always and Guards workflow at an agent event opens with the context mark,
the guards at Tool about to run hold a write (writes only, after the lockout of 2026-10-16) while a skill, the look or a
mark is owed, and the Always workflow at Agent stops holds a stop while anything is owed, naming it. The requiring, start and
mark listeners are deleted; the three pause states are no longer entered and retire in task 368. Decided (task 367):
a debt never changes which workflows run; it holds writes and stops only. The replays of phase two carry it. The
journal's own commands must never be held, whatever a workflow says: task 406, on the user's ruling.

Phase two closed on 2026-10-17 just after midnight: the three pause states are deleted with the owed-pause
machinery; the first migration, run at boot by the migrator the app now wires, unwraps an agent readings in one
of them with its fact set; a user's workflow bound to one is kept off and named; the holds hold under Codex as
under Claude; CLAUDE.md names the facts beside the state and the pauses as the waits; DRAWINGS_VERSION 9. The
suite: 237 tests, 19 s of CPU and 38 s of wall on a loaded box; the replays: 46 in about twenty seconds now that
no pause state wraps another. The checkpoint note is report 7 on the plan. The dev journal
re-seeded itself at the bump: 9 states, 28 workflows, none behind. The lockout of 2026-10-16 (a skill hold that
held the read paying it) is fixed in the guards and floored by task 406, still open.

Phase three of plan 7, closed on 2026-10-17 in the small hours: the replays for plans and workers, the clock, the
pauses' exits and Ended, and a session's start and end were frozen before anything moved (tasks 372 to 375), and
stand green after it, 58 in about twenty seconds. Send the agent back to what it was doing releases any pause to
the state its resume keeps (376); a state change is named by its outcome, Wait for something outside, Mark the
agent stuck, Change state to Idle, with a wordless wait or stuck refused at the save and a change to Idle from a
state that owns something refused as before; move_to is gone and an older workflow naming a state is rewritten at
boot (377). Ended ships a workflow with its trigger alone, titled Does nothing yet (378). The page shows a run's
state change in words, the answer the agent was given, the number a count check read, and a card's details in
reading mode; Test run says the order and where it would stop, with a dry count ledger (379, 380, 413). The rules
doc is reworded (381). On the user's rulings of the same night: the engine's own moves are not workflows and are
not shown on the page at all (415, after 379 had shown them in grey); delivering a message to the agent is the
engine's, so the two Always workflows at a message's creation and reading are gone and the messages feature types
and counts itself (416); every shipped workflow is titled by what it does (411); every label, title and line is
plain English, swept by a reading subagent and fixed in two commits (412), and CLAUDE.md carries both rules, Plain
English and Workflows drive the agent, the engine keeps it safe, the latter around the test "would a user want it
different, or want to watch it happen". Task 414 sorts the plan's remaining phases by that test before phase four
closes: 388 to 393, 398 and 399 are engine behaviour, 385, 395, 396, 397 and 401 stay workflows. The floor of 406
is in: a journal command and a skill's read are never held. The suite: 245 tests; the replays: 58.

Phase four of plan 7, closed on 2026-10-17 before dawn: each feature declares the checks and actions a workflow
may name, beside its states and nudges, and the chart's catalogue gathers them from the registry and defines none
itself, Entry having moved up to features/entry.py (383); a blocking listener that raises fails open, with an entry
guard_failed, a card in the chat and a line to the agent, and the law text says a hold is never the result of a
fault (384); the content checks Tool is one of, Tool input contains, Prompt contains, Time of day within and
Context over N percent read the event's own content, answered the same for Claude and Codex in one bounded test
(385); a check on time takes its unit and the shipped workflows say minutes, DRAWINGS_VERSION 10 (386); the phone
shows the locks and a card's own number in its title. Phase five has nothing to build: its guards are engine
behaviour by the user's ruling and stay where they are, listed under Kept in code. The suite: 248 tests; the
replays: 58; the dev journal after the restart: 9 states, 27 shipped workflows, none behind, 142 catalogue entries.

Phase five had nothing to build: its guards are engine behaviour by the user's ruling. Phase six of plan 7, closed on
2026-10-17 in the night, turned on the user's rulings of the evening: one concern per workflow in the run order, a held
stop and Run no later workflows ending the walk, a child state running its parent's workflows after its own, the
agent's debts each feature's own code, the counts read from the journal's record and kept by no workflow, two Opus
reviewers' findings applied (task 417). The start block was the Always workflow Tell the agent the journal's rules,
facts and what waits (395) until task 842 made it the engine's, the briefing feature's StartBriefing; the voice is its own workflow (396); the fiftieth-line reminder a workflow at Post tool use
reading the lines said since the last one (397); the silent session's end and the delivery retype stay the engine's
(398, 399); what is unread at a start is delivery (on message 1672). Alongside: the agent events take the providers'
hook names (425), titles say their settings' numbers (424), a card's run-ending steps carry the no later workflows
badge (418, 426), the menu watcher answers Claude Code's menus by the user's rules (420), a start after a compaction
says where the work stands (409), old facts are asked about once a day (410), and a cancel stamps a task finished so
the sidebar counts only open tasks (on message 1729). The rules table is final: every row names its workflow by title
or says the engine keeps it. The suite: 250 tests; the replays: 56.

## The thin supervisor (plan 8, 2026-10-18)

Who owns what, decided at the start of the plan (task 443) on the rulings of messages 1611, 1613 and 1616 and the review in report 11:

- One supervisor runs per agent terminal, as now. The one launched with the journal hosts it: the journal server is a named process in its table. A supervisor started with --no-journal runs its agent only.
- The supervisor starts what its launch file lists, the agent and, on the host, the journal. Once up, the journal asks its host to start the services it declares. Starting a name that is already running does nothing, so a journal restart starts nothing twice. The journal never asks to start itself.
- Every process lives as long as its supervisor: when the host ends, its journal and services end with it, as the journal does today when its parent is gone, and the next launch hosts them again.
- Workers stay outside the protocol: the journal runs them itself.
- Nothing but the agent's own end, or a stop asked for, ends a supervisor (message 6316): a fault in a verb is answered with why, a fault in a turn of the loop is skipped, and each is written to runtime/supervisor.log. A service's group is signalled only while its leader runs, never the group of a process reaped long before.
- send stays in the protocol: it is the message bus of message 1613; its first user comes with a later service.
- "Never another restart" covers new processes and the protocol growing by versioned verbs. The supervisor imports every module at start, so an upgrade that overwrites its files leaves a running one untouched (task 438, a test); since task 1169 a fix to it lands at the end of the agent's next turn, through the launcher's loop (see The launcher's loop below).
- The menu watcher stays a thread in the journal server (question 6, the user's answer): it reads every environment's mirror and shares what it chose with SupervisorLink in memory. Phase 3 proves services through the protocol with the next real one, or a fake one in its test.

The protocol, first version (tasks 436, 437, 439):

- One stream socket per supervisor, in /tmp/journal-<uid>/, a folder only the user can open, the socket itself 0600. A request is one line of JSON, {"verb": ..., ...}; the reply is one line, {"ok": true, ...} or {"ok": false, "error": "<plain words>"}. An unknown verb or a malformed request is answered with an error and the supervisor stays up.
- The announce file runtime/inboxes/<environment> holds {"socket": <path>, "protocol": 1}. An announce file holding a bare path is the old supervisor, which takes the old datagrams (Type, Keys, Stop, RestartAgent, RestartJournal); SupervisorLink speaks to each in its own way until the one restart, then the old way is removed.
- hello answers {"protocol": 1, "verbs": [...]}. The verbs are hello, start, stop, restart, list, keys, type and send. A later version adds verbs and never changes one, so a journal asks hello before using a verb it is not sure of.
- The supervisor's process in front is the one that owns the user's terminal: it gets the keyboard, the resize and the band, and when it ends the supervisor ends, taking every process it started with it.
- send carries text to a named process's input: a service's, or the agent's terminal. The agent is the only terminal process; one started beside it, with its own mirror under runtime/screens, waits for its first user.
- The agent in front owns the terminal: the keyboard, the resize and the band; a restart of it through the protocol fits it again. When it ends, or the journal stops it, the supervisor ends and takes its services, its inbox and its mirror with it, so no stale screen is read. Stopping the agent is the viewer's Stop, a deliberate act; nothing guards it further.
- Features declare the services they need (Service, a name and a module of the package); at boot the journal asks the supervisor hosting it, the environment the launch names in JOURNAL_ENV, to start each. An upgrade restarts the journal, so a new service starts with it and the supervisor runs on. A journal no supervisor hosts, under plain claude or a worker's, starts none and its log says which are off. Workers stay outside the protocol: the journal runs them itself.

## The launcher's loop (task 1169, 2026-10-21)

On messages 11891 and 11894:

- The launcher is `src/supervisor/launcher.sh`, a shell loop of a few lines that never changes and loads no code. It runs `python -m supervisor <launch file>`, starts it again whenever it exits, after a second, and exits when the supervisor exits 0. The journal's Python launch (`Launch.supervise`) runs the loop and waits, then puts the other hooks back and removes the launch file, as before.
- The supervisor's exit codes: 0 (ENDED) when its agent is done: the agent quit, died three times in two minutes, or was stopped, a SIGTERM or a hang-up; also a launch file it cannot read, which would fail again. 75 (RESTART) for its own restart. Any other code, a crash, starts it again too. The agent's own exit code is no longer passed up.
- `restart` with the name `supervisor` (and `resume`, else the conversation running) is the supervisor's own restart: it writes the conversation to resume into the launch file's `front.resume`, stops the agent and every service, and exits 75. The next supervisor starts from the launch file: the agent resumed on its conversation, the journal as a service, and the journal at boot asks again for the services the features declare. A restart of the agent alone writes its resume into the launch file too, so a supervisor started again after a crash resumes the newest conversation.
- `hello` answers `outdated`: whether the supervisor's code on disk (a hash of its `*.py`, `SourceHash`) differs from the code it started with. The supervisor hashes itself, so the journal imports nothing of the supervisor package.
- When it is restarted: at the journal's boot the updates feature's seed `SupervisorCheck` asks each environment's announced supervisor once and keeps the outdated ones (`OutdatedSupervisors`); `SupervisorUpgrade` restarts a kept one at the end of its agent's turn, never in the middle of one, and once. A journal boots after every launch, `journal setup restart` and update, so the answer is fresh where the code can have changed, and no Stop asks anything. An environment with no supervisor announced, or one from before the protocol, is not outdated and is never asked. `journal setup restart` and an update restart the journal at once as before; the supervisor follows at the agent's next turn end, so its code changes land without a new launch. A supervisor from before task 1169 answers no `outdated` and is left as it is until the next launch.

## A reply the transcript never kept (2026-10-17)

A text block written just before a tool call reaches the journal only through the agent's transcript, which the journal reads at every hook. Claude Code sometimes does not save such a block at all: replies to messages 1787, 1795 and 1814 of this session are in no transcript file, while 1790's is. The journal cannot record what never arrives, so the answer hold names `journal message send "<words>" --reply-to N`, which always counts, and the messages skill says why (task 457).

## Secrets (plan 9, 2026-10-17)

A secret is a key or a login the agent may use without seeing it. The row (models/secret.py) holds its fields, which are filled, the programs it may go to and those proposed, whether helpers may have it, and its login's times; never a value. The values live in a NAME="value" file in the private folder (private_folder.py, secret_values.py), named by the project's .journal/project-id, 0600 in a 0700 folder with a .gitignore of *; AGENT_JOURNAL_SECRETS moves it. Secrets kept as files under .journal/project/secret come in as rows once at boot.

Engine, kept in code because no user would want them different: masking every text the connection writes (db/masks.py) and every form of a value in a program's output (features/secrets/output_mask.py); the allow-list, the never-given programs and the search path without the project (features/secrets/programs.py, secret_run.py); the guard that refuses the agent's tools the secrets folder and the MCP keys (listeners/keep_out_of_private.py); telling the agent a program was allowed (listeners/tell_allowed.py); the leak alarm card (listeners/alarm_on_leak.py); the thirty-day purge. A workflow a user may shape: none yet; a nudge to use `journal secret run` at a tool use that names a key would be one.

The agent proposes a program (`journal secret propose`), the user allows it on the Secrets page; no command takes a value, the user fills it on the page. How the viewer proves it is the user is question 8, open.

## A workflow's counts (plan 12, 2026-10-17)

(Superseded where it says per agent or names the readings: see Workflow parts, plan 18, below.)

- A workflow keeps its own counts for each agent, named `charts:<id>:<name>` in the counts table (question 9:
  no sharing by name across workflows). A count started at one event and counted at another is one workflow with
  a trigger for each event (question 10); `Charts.for_event` lists a workflow under every event it holds a
  trigger for.
- Every event still walks a workflow from its trigger; a run never resumes at a node (the three readers of
  report 18 showed resuming skips the count it waits on). Waiting is drawn: Wait here until a count reaches N.
- The readings (edits, uses, owed, namings, lines) stay the journal's, read from the record, and are shown on the
  canvas with what they count; a count may not take a reading's name.
- Raising, starting and setting a count happen in one database transaction; a lock around the walk deadlocked
  against a row's save, which walks its workflows inside the transaction.
- The walk entry records where each path ended with the workflow's counts (`stops`); `GET /journal/chart/<n>/readings`
  serves each agent's last stop, its counts, readings and the numbers checks compare with.
- A count no node names any more is cleared with a card; a user's workflow reading another's count is turned off at
  boot; migration 6 cleared counts of the old shape.
- The replays record what the count checks read in each step, so a change in a reading fails them.

## Plugins (plan 11, 2026-10-17)

The protocol, the manifest and the version 3 mapping are in docs/plugins.md. Decided while building it:

- One listener per kind of event, on the bus from boot, reads the enabled plugins at each event. There is no
  Bus.unlisten, so switching a plugin off between two events neither drops nor doubles one.
- A plugin holds an event only inside the window its manifest declares, `{"event": "tool_starting", "window_ms": 5}`,
  cut to the ceiling `plugins.hold_window_ms` (50 ms); a bare event name takes the ceiling. A hold that fast is answered
  by the plugin's service from what it already knows; judging and sins run on the plugin's own time and ride on the
  next hook. One past its window is cut, its answer dropped and the miss recorded as unanswered, never a fault, so it is asked again next time (messages 11346, 11408; doc 61). This replaced the one shared
  deadline of six seconds on 2026-10-21.
- A plugin's queue (message 11346, task 1142): the folder `queue` under its data folder, one `.json` file per line out
  with `env`, drained at every hook on the answer path, a line for the hook's environment riding on it; a plugin that
  judges asynchronously writes there and never holds. One parser for a queued file and an answer: the protocol's.
- A plugin is asked to hold only while nothing has held the event yet (`asked_while_free` on the listener). After that
  it hears the event after the reply, and a refusal then is recorded as `plugin_unanswered`.
- A stop is held once a turn: Idle carries `held_before` from `stop_hook_active`. There is no count of four in a row.
- The plugin token is made per server run and kept only in the server's memory, never in a column.
- A plugin's message is the journal's side of the chat (`Author.of`). Plan approve still refuses anyone but you.
- Plugin commands carry a step count in a context variable. A row written two steps deep is heard by no plugin, and
  a `plugin_cut` entry records it.
- `plugin.updated` is delivered to a plugin alone when someone else changes its settings. Install writes the settings
  once, so a plugin hears it only on a later change.
- Only the user installs, switches on or configures. The agent upgrades a plugin already installed (message 6307), and
  proposes a new one with `journal plugin propose`. The
  agent's writes into `.journal/plugins` are held. A linked folder is not held, since it is the user's own working copy
  (code-commandments is one); the hash check switches the plugin off when its program changes.
- Services run per environment, one copy under each running supervisor, each on a short socket path in /tmp. The
  program answers when no supervisor runs or the socket is gone.
- A dashboard is lines the plugin writes (`journal dashboard set`), drawn by the viewer's own dashboard. No plugin page
  runs in the viewer.
- A keyed card settles the earlier one in place. A plugin's plain message is drawn as a card of the plugin's.
- What a plugin did is its record: the entries it left (`plugin_said`, `plugin_command`, `plugin_fault`,
  `plugin_unanswered`) and every row change stamped with it.
- Requiring a plugin's skill in a state waits for a workflow action that names a skill.
- The console captures each command's output per context (CapturedStream) and runs commands side by side. A plugin's
  setup step or installed command may itself run `journal` commands while `journal plugin install` runs.

## Rulings of 2026-10-18

- Triggers are engine code. A user trigger never becomes a workflow of its own (message 3400); the Triggers page stays
  as it is.
- Documents are project-wide, never per environment (message 3311): `Doc` is a `Model`, read from every environment; the Documents page also lists the files attached to messages, and its search reads every document.
- The supervisor starts an agent that dies again, resuming its session, and keeps the journal and the services
  running; a clean exit still ends it (message 3331).
- The supervisor stays a very thin process host; a change to it needs the whole process started again, so changes to
  it are kept rare and every other behaviour lives in the journal (message 3423).

## The package's layers, after the sin sweep (2026-10-19, task 598)

Code commandments judges `src/journal` clean (657 files). Decided on the way:

- The packages import one way: `models` and `events` at the bottom, then `db` and `repositories`, `engine`, `providers`,
  `features`, `hooks`, `http` and `console`, with `app.py`, `runtime.py` and `service_start.py` at the top. The bus,
  `Listener`, `AgentListener` and `Decision` live in `events/`; `Said`, `Nudge` and `Deferred` in `engine/`; `Option` in
  `models/`; `Hook` and `HookType` in `providers/`; `PluginRefusalExemption` in `features/`. The runtime and the service start wire the
  features, so they sit beside `app.py`, not in `engine/`: the engine imports nothing from `features/`, and asks
  `FeaturesKnown` (its protocol, which `Registry` implements) for the states and whether a line is switched off.
  CLAUDE.md still lists the runtime among what the engine holds; that line is the user's to change.
- A skill an agent owes is a fact on its row, `skills_owed`, like `oriented` and `mark_owed` (migration 7 moves the old
  one-ended links); a link always has both ends.
- What crosses into the journal is typed where it enters: the viewer's act body (`ActionBody`), a drawing
  (`DrawnNode`, `DrawnLine`), a walk entry (`WalkRecord`, `WalkStop`, `WalkFailure`), a plugin's manifest, settings,
  answer and preview, a transcript row (`ClaudeRow`, `CodexRow`), the supervisor's announcement and replies, the MCP
  check (`HealthReport`). What the page reads back is a `TypedDict` where it is a JSON shape.
- code-commandments v5.19.3: an attribute that overrides a base class's `ClassVar` is a constant, so a feature's
  nudges built from its `name` are in order.

- **Updates (task 28).** `features/updates`: `Updating` reads the v4.* tags from GitHub at most hourly on a thread of its own (first look a minute after boot), and with `updates.auto` on installs the newest release of the same major by running its `install.sh` (`AGENT_JOURNAL_REF`, `AGENT_JOURNAL_YES`) from the project root; the install's own `journal setup` restarts the journal. The code-commandments plugin, when installed, is upgraded first through `Installing.upgrade`. The viewer's `/releases`, `/update` and `/changelog` are in `http/v3/updates_controller.py`. Open: the plugin is pulled to its newest commit, not its newest tag; `src/web/dist` needs a rebuild for the new UpgradeBand.

## Dumps (ported from version 3, 2026-10-19)

`features/dumps`: a `Dump` model and `Dumps` repository, `Filing` (everything done to a dump, shared by the `journal dump` command and the viewer's `DumpActions` in `http/v3`), five listeners that tell the agent (arrival, answer, choice, filed, carry on), and the `journal-dumps` skill. Files are kept under `config.files/dump/<n>`.
- Decided: no collections. Version 4 has no Collection model, so the dump itself is the collection: `journal dump name` renames it, and each row the agent files is a `dump_filed` link from the dump to the row. Removing a dump deletes the docs, reports, tasks and plans linked to it that were made after it was dropped.
- Left out for now: a pasted transcript becoming a dump (needs the message kind transcript); an offered step that runs a command (offers are `{ask, label}` only).

## Rulings of 2026-10-19

- Every read of a scoped model is scoped in the base repository (`ScopedRepository.selected`); no repository writes
  `environment_id = ?` by hand. A read with no environment set is refused. A read across environments says so by
  name: `across_environments`, `selected_everywhere`, `agents.everywhere()`, `with_project` for the project's own rows.
  A seed whose rows belong to environments is an `EnvironmentSeed`, run once inside each environment's scope.
- The supervisor restarts a kept service however often it dies, the wait capped at 30 seconds; it never gives up.
- Workflows are behaviour toward the agent only: keeping it going, holding its stop, nudging it. A hint on a command's
  output is the engine's (a feature's listener), never a workflow's, and no workflow changes a command's output.
- Sorting a dump is a state of the engine (`SortingDump`, a pause), not a sequence and not a workflow: a dump the user
  drops moves the agent into it, the stop is held until the dump is filed, save while the user's answer is awaited.
- A blocked task never blocks its plan; a plan whose every task left is blocked blocks itself and opens when one opens.
  `journal plan block` and `journal task block` take `--on` and `--until "<command>"`; an `--until` command is a check
  kept off the lists, and one that cannot run holds every stop with its error.
- A face on a message answers it, whatever its length. A line the user types in the agent's terminal is their message
  in the chat, read already and never owed a tagged answer.
- A question's options name who acts, the agent or the user, never I, we or you.
- Docstrings: one short line at the top of a class; none on fields or methods.
- Helper classes leave their domain's folder: `<domain>/support/` when only that domain uses them, `src/journal/support/`
  when several do (task 729, after the viewer's API is moved).
- An agent marked ended after an hour's silence comes back the moment it takes a prompt or uses a tool; the machine
  refuses an agent with no session.
- A worker outlives a restart of the journal: its output goes to files, its process id is on its row, and at boot every
  worker still out is watched again.
- Words the hooks missed are swept from the transcript each tick, read on from the hooks' own position past the
  seconds the hooks have (`messages.sweep_after`, 10 by default).

## Rulings of 2026-10-20

- A workflow is self-contained: it checks every condition it acts on itself, auto mode among them, and never counts on
  an earlier workflow stopping the walk to keep it from acting. Stop the later workflows (formerly Run no later
  workflows) is a side effect a workflow may opt into. The shipped checkpoint wait checks auto mode is off, the
  carry-on and the log ask check a task is in hand, and no shipped workflow stops the later ones any more (message 7165).
- The state of an agent that ran `journal await` is named Waiting, beside Waiting on a question and Waiting on a worker.
- A setting's help says what it does in plain words; the workflows that read it show under it as links (message 7014).
- Tunler's version and domains, and the MCP servers' check, are kept for an hour and asked again after a change.
- The phone (plan 17) ports version 3's server side as it was, which worked; its screens are the viewer's own pages
  and components with phone styling, not version 3's separate app; only what touch needs gets a phone component
  (messages 7314, 7327; tasks 901 to 903). Plan 17 may be merged by the agent once landed and tested, and released as
  4.2.0; plan 18 waits for Sir Jesse to merge (message 7301).
- The phone after its review (task 909): a phone's reads are named one by one, as its writes are, never every read
  but a few; no read that starts a program (the MCP check) and no page that sets how the journal runs. A project file
  is never read from a hidden folder (.env, .journal) nor outside the project, on the desk too. The push keys live in
  the private folder beside the MCP keys. The clock closes the tunnel once a code or a phone runs out, and a paired
  phone keeps the tunnel, and its button in the top bar, even with sharing off. The phone sends text only: a file is
  attached on the computer. A failed push is tried again a minute later; an address the service no longer knows is
  forgotten. A file opened on the phone is sandboxed. Left as it is: anyone who reaches the tunnel can void an open
  pairing code with ten wrong tries; the user makes another, and a code lives ten minutes.

## Rulings of 2026-10-20, evening (on the development branch)

- The journal follows a branch when Settings, Updates, Follow this branch names one, or `journal update follow
  <branch>`: the check reads the branch's head on GitHub and compares it with the commit the installer recorded in
  `.journal/src/commit`; only a pushed commit counts, never a working tree. This checkout's journal follows
  development.
- Lines typed to the agent go at most once a window, `delivery.batch_seconds` (5): a line within the window of the
  last is held in the typing funnel, SupervisorLink.type, never in a workflow, and the tick types the held lines as
  one marked line, the instructions joined with " | ". The window and the hold until a line is seen back are the
  same hold; 0 types each line at once, which the tests about other conduct set.
- A settings save from the viewer names only the keys it sets, null clearing one; the server never unsets a key
  by its absence. Before, a pane layout or colour scheme save dropped every other viewer key, the tour's finished
  mark among them, so the tour replayed after every update.
- A pin above the chat whose link is a row's ref (`--link docs:55`), or the journal's own address opening one,
  opens the row in place as its card does; an outside address opens a new tab.
- A comment on a document's passage is read with the passage: `journal message read` prints the quoted lines under
  the comment when the message is no reply; a reply's quote of the message it answers is still left out.
- The chart goes (task 979, plan 19, doc 55): the states carry the journal's conduct on a stack machine. Settled
  with Sir Jesse in messages 9364 to 9427: a stack of states with push and pop, the trail; one BaseState with the
  mechanism and the shared listeners (compaction pushes Compacting, the session's end pushes Ended); listeners are
  methods named on_<moment>, bound to their event by the annotation and found by type, overridden on purpose; a
  journal panic command always allowed; Tuning as a frozen readings of the options; Readings on the stop and the
  tick. Plan 19 waits for his approval. Later the same evening (messages 9491 to 9516): only the states move the
  agent, answering events; a command writes rows and the feature dispatches a named event beside the write
  (PlanStarted, TaskClosed, QuestionAnswered, WorkerBack), and a state never reads a row as it was before; the
  state machine is the engine's alone, `journal panic` the one hand on it from outside; the class is StateMachine;
  the options reach a state as a frozen Settings value; the lifecycle hooks on_push, on_suspend, on_resume and
  on_pop are always called, and on_push may refuse the push; no docstring and no comment inside a method, and none
  on a field, a class keeps its one line at the top. Six reviews of plan 19 (four on Opus by phase, two critiques)
  were filed into it the same night: 40 tasks, 24 briefs rewritten, the phases retitled, phase 2 in three steps
  each ending with the replays green, the repositories and the judge before the live check and the pull request.
- Also that evening: JOURNAL_ACTOR (agent, sub-agent, worker-agent) read by the hook and command shims, a hook with
  a subagent's agent_id returning at once; a subagent's shell is the agent's whole, so its commands are told apart
  by the server later (task 1032), for Codex by the thread id; the journal's own update installs the journal and
  nothing else, never a plugin, and takes its marker down when its thread fails; five plain-code-words rules under
  .commandments/custom (poetic names, docstrings in methods and under fields, the state machine outside the engine),
  1591 findings left for the rewrite by Sir Jesse's word; the worker and subagent chat draws the same Turn bubbles
  as the main chat, from transcript turns shaped like messages (kind and text).

## Workflow parts (plan 18, 2026-10-20)

- Sir Jesse's answers (message 7237): a workflow's values are kept per environment, in its own record, and no
  workflow reads another's. Counts and times are rows named `charts:<workflow>:<name>` (ValueName, one home), in
  the counts and noted_times tables, kept out of the timeline since they change on nearly every tool use.
- A value lives as long as its workflow: a session's end, a restart, a takeover and an edit that keeps its step
  leave it; the last step naming it gone, a reset or a deletion clear it, in every environment. Two agents in one
  environment share its values; a row event sets a value once however many agents it walks about.
- Times are read through Clock.now(), which every tick, log time and background check reads too, so the replays
  drive one clock. A time never noted has no since: Has N passed since a noted time? answers no, and Was a time
  noted? says so. Has N passed is at least N, as the quiet check it replaces was.
- A workflow's place is per event it holds a trigger for, on its own record (Chart.places), kept in step with its
  triggers; a row per event was not made, since it would need a link back to its workflow and the places are the
  workflow's own data. Chart.event stays the event it was made for, the key a shipped drawing is known by.
- The shipped workflows are drawn from parts (DRAWINGS_VERSION 28). Each quiet clock is still bound to its state and
  notes its time on the move that starts its wait and on the agent's own session start, prompt, tool use and stop;
  quiet now means no event of the agent's own, where it meant no change to the agent's row. A reminder repeats by
  its line's repeat window, as before, not by noting its time again. The log ask forgets its time for a task a plan
  took in hand (Follows a plan?), so it asks at once as an empty Working.logged_at did. The log ask's start trigger
  now belongs to the stop's workflow, so at a session start the log line comes before carry on: the one change in
  what the agent is told, and only in order.
- Retired: Has the agent been quiet for N?, Is the log older than N?, Has a command run in the background longer
  than N?, and the readings edits, uses, owed, namings and lines. A user's workflow, or an edited shipped copy,
  naming one is stopped at boot with its title saying which; it is not rewritten to the parts, since a clock needs
  triggers the user's drawing does not have. At the upgrade the times are seeded from what the retired checks read
  (ValuesAtUpgrade); counts start at zero.
- Journal line said and the others no row speaks for are agent events (Await, Command moved to the background,
  Background command ended, Commit made); a task's or a message's move is its row's trigger with a check naming
  the move. A path from Journal line said may not say a line, or it would start itself again.
- The run order changes in a mode of its own on its column, since the page's Edit folds the lists for the canvas.
  The workflows page stays on the computer, as the phone leaves every page that sets how the journal runs there.
- The blocked-task ask after an hour of quiet never speaks, since an hour of quiet ends the session first: task 911.
- Tool held already? sees the holds of workflows only: a write held by the engine's own debts (a skill, the look, a
  mark) or by a plugin still counts toward a workflow's writes, where the retired edits reading left it out. Left as
  it is: such a hold is paid within a step or two, and the count is at most that many ahead.
- Journal line said is told on the bus after the reply, on the worker thread, so a line said never walks inside the
  hook or the walk that said it; its walks that only count are not recorded.
- A downgrade past 4.3.0 is not supported: migrations 15 and 16 merge the agents' counts per environment and move a
  workflow's one place onto each of its events, and an older version reads neither.

## Plan 19, phase 1, as built (2026-10-20, night)

- The stack machine's values, `Stack`, `Transition`, `Held`, `Hooked`, `Settings`, `SnapshotReaders`, live under
  `engine/support/`, not `support/`: only the engine builds them, and `support/` may not import the engine. `Readings`
  is an event's payload and lives in `events/readings.py`.
- Until phase 2 moves the features' conduct, the old `AgentState` extends `BaseState` and the pause chain (`Paused.resume`)
  stays what the old states express; the stack on the agent's row is kept as its mirror: a pause that resumes the top is
  pushed on it, a resume that names the state beneath pops to it, anything else stands on its own chain with Idle at the
  floor. `StateMachine.move` is that bridge and goes with the commands' moves.
- Every change of the stack is a trail entry of kind `state`, with the stack before and after, the cause (the event's name,
  `a feature moved the agent`, or the panic command's words) and a refused push with its line; the agents page carries
  `stack` top first and `trail`.
- `journal panic` lives under `console/commands/`, since the engine imports nothing from the console; the rule that keeps
  the state machine inside the engine excepts it and `runtime.py`.
- One nudge registry (`engine/nudge_registry.py`): every feature's nudges and the engine's are registered at boot, the
  nudger refuses an unregistered one, `journal nudge list` prints them. A nudge's name says what the line does; a
  hundred and four were renamed by one map, the replay records and the shipped drawings rewritten by it.
- Twelve guard rules under the custom `stack-machine` skill and two more poetry rules (parameters and variables); the
  custom docstring rule looks at a statement's own literal. The worklist the judge writes is cleared on purpose: the
  pre-existing findings are phase 4's (task 1052).
- Phase 1's commits were pushed to `development` as they landed, since this journal follows that branch; the plan's
  "nothing pushed until the migration is proved" was not kept, and task 1053 still proves the migration on a copy before
  the pull request.
- The files of task 1002 were wiped from the working tree before their commit while a worker's commit was taken into the
  branch (task 1082); they were written again from the record.

## Plan 19, phase 2, task 1035: the speaking listeners become conduct (2026-10-21)

- Voices, etiquette, pins, migration, git, checks, triggers and plugins each have a conduct mixin and, where the lines need facts, a readings reader: the voice's instruction, the lines said since the last reminder, the pinned and lately suggested links, whether a version 3 journal waits, every trigger, the plugins folder. The listeners that said those lines are gone: IntroduceAtStart, SayVoiceWhenChanged, ReadTurn, UnpinnedLink, UnpinnedLinkInOutput, LinkSuggestions, HoldPluginFolders; the drawings say_voice, remind_what_a_line_is and tell_of_version_3 with them.
- A setting's write, a check's run and a user's message are row events the models carry: SettingChanged, CheckRan, MessageArrived. A row that is new when it carries its event has no environment or time yet, so the repository's carried() places the event by the saved row (RowEvent.placed_by); that is the one place it happens.
- A commit stays an agent event: SpotCommit records the card, closes the tasks the trailer names and dispatches CommitMade with what it closed and the task open next; the git conduct says the lines, and because they ride the reply of the command that committed (never typed, as ruled on 2026-10-17), CommitMade answers the hook and SpotCommit hands the machine's decision back. The dispatch in SpotCommit is the one agent event a feature listener makes; the DispatchOutsideFunnels rule still names it, and phase 6 gives the rule a principled reject for an agent event that answers a hook.
- The tool call carries the paths it writes (ToolStarting.written_paths, filled in the hook translation from the provider), so the plugins conduct holds a write into the plugins folder with nothing but the event and the readings.
- PluginsHearAgents stays a listener on purpose: it is the funnel through which each plugin's own words and holds reach the agent, never the journal's conduct. Watching still hands back the first step of a sequence a trigger starts; task 1034 makes sequences states and takes that line with it. Both are named by the FeatureListenerSpeaks rule until then.
- AfterAClose answers with the next open task as a value (OpenTask, in models); the task command and the git conduct each render the line from it.
- A stopped runtime takes its conducts off the base state, so a hand-built state in a test answers with its own listeners alone.

## Plan 19, phase 2, task 1059: messages, laws, shell, secrets, questions, profiles and workers speak as conduct (2026-10-21)

- Each of the seven features has a conduct mixin; the readings carries what the lines need: for messages the unread, the unanswered and the folders of their files, the agent's own tool uses since the newest message came, how often the unread were named since, and its uses while a read message stays unanswered, all derived from the entries and the nudge lines said, never kept as counts; for shell the background commands and since when, the untold ended ones, the shapes of the last reads of outputs by hand, the project's readers and the reader tips said; for workers the subagents running besides the newest dispatch, every dispatch of the session, the reports waiting and the workers' worktrees; for profiles every profile by name, the subagents' and the workers'; for secrets the private folders by every spelling.
- The four inbox workflows are one conduct: the inbox named every so many own tool uses since the newest message, a write held once the unread were named often enough, the tools held past so many uses with a read message unanswered and an answer asked for before that. A journal command and a read of the message's own files pass the unanswered hold, as before.
- A reaction (ReactionGiven, by the Reaction model), a secret let go to new programs (SecretAllowed, by the Secret model) and a worker's report (WorkerBack now names the worker and its report message) are row events; a user's message (MessageArrived) came with task 1035.
- The tool call carries the paths it reads and the lines of the file the read tool reads whole (ToolStarting.read_paths, file_lines), filled in the hook translation from the provider, so the shell conduct holds a whole read of a long file without touching the disk.
- MarkOutputsTold is the one listener left that records for the shell conduct: it marks the ended outputs told at the tick the conduct names them.
- DeliverMessage and DeliverUnreadAtStart stay the engine's delivery in the messages feature; TellInbox is their base and the FeatureListenerSpeaks rule still names it. The two one-line listeners of one body for two events (the inbox at a prompt and at a stop, the reports at a stop and on the tick) are named by the duplication rule; a listener answers one event type, so each stays.
- The ten drawings of the inbox, the reports, the background check and the report-came line are gone from the shipped chart.
- A state silences a conduct listener by defining a method of the same name: the dispatch leaves out a conduct method whose name the state or its bases have, so Awaiting answers a worker's report itself and the workers conduct's line stays quiet while the agent waits on workers.
- The custom poetic rules ban poetry, not coding words (messages 10144 to 10163): the words of speech and story, mood and magic, craft and journey, the vague fillers, and the past participles that say nothing of the thing (made, done, seen, taken, heard, noted, got, met, gone, lost). Plain coding words such as created, deleted, written, moved, pushed, fetched and merged stay. The judge found 329 such names on 2026-10-21; task 1095 in phase 6 renames them.

## Plan 19, phase 2, task 1060: the skill, look and mark debts are conduct (2026-10-21)

- The debts stay facts on the agent's row, set by recording listeners: OweSkills notes the skills a start or a prompt calls for, OweTheLookAtStart sets the look owed, TakeTheMark takes a crossed context mark. The lines and the holds are the skills, briefing and memory conducts', from the readings: which skills are owed, loaded by hash and shipped (SkillsSnapshot with the catalogue, so the conduct works out what a start or a prompt calls for with the state's own name and no repository), whether the agent has looked and what the start block names (BriefingSnapshot), the mark owed and taken and every fact, rule and reminder with its keywords (MemorySnapshot).
- The rows that pay a debt carry its event: the agent row carries LookTaken, MarkDecided and SkillRead (Agent.look_taken, mark_decided, skill_read), a rule carries RuleMade with who made it. Every row event gets the row's number on save (RowEvent.row_id, filled by the repository with the environment and the time), so a new row's event can name it.
- What a start or a prompt owes is worked out once, on SkillsSnapshot (due_at_start, named_in); the conduct says it and OweSkills records it from the same reading. The same for the mark (Memory.mark_due) and the whisper (MemorySnapshot.whispered_by): the conduct types the line, MarkWhispered shows the card.
- A transition's typed lines are typed by the machine after the event's delay, so the introduction is the voices conduct's on the session start, typed four seconds after the start block; JournalStarted and AnnounceStart are gone.
- The whisper and the question about a new rule are typed lines now, where they were the hook's context and the command's output.

## The mend after tasks 1059 and 1060 (2026-10-21, night)

- A test run that ends in a pipe reports the pipe's exit code, not pytest's: twenty failures hid behind a tail. A test run never ends in a pipe; the pytest reader (journal output read N --reader pytest) picks the failures out of the kept output.
- The tests of the chart drawings removed on purpose are gone with the drawings (twelve tests, chart-only).
- A skill read is recorded under the write lock, its event carried: Repository.rewritten(row, by, change) re-reads the row, applies the model's change, writes what differs and carries the events, so two reads sent together both stay.
- A prompt typed in the terminal is watched as a prompt; its record as a message (RecordTypedPrompt) is not watched again, or a trigger started its sequence twice.
- Awaiting hears each worker's return and stop (WorkerBack, WorkerStopped) itself, tells it, and pops on the last with the waited-on line; the two awaiting drawings are gone. The workers conduct tells a report only to the agent that dispatched the worker (the row event names the session it reaches, RowEvent.session, and the worker names who dispatched it).
- The machine types lines one at a time, as the terminal takes them: a line with breaks would be pasted and typed again.
- A fact, rule or reminder is whispered once per context window: the lines whispered since the last compaction travel on the memory readings, and the card follows the line said (MarkWhispered on LineSaid, which now carries the line's values).
- The rule question is a typed line, as the whisper is; the test reads it from the typed lines.
- The resume chain lives on the stack since phase 1; the unwrap test reads the stack.
- The custom rules ban poetry in names (PoeticVariable/Parameter/Method/TypeNameDetector) and sentences as method names (SentenceMethodNameDetector): articles, pronouns, adverbs and preposition phrases in a name. Tasks 1095, 1101 and 1105 rename what they catch. Since task 1102 the banned words sit in .commandments/custom/lists.json, which the plugin reads since v5.27.0: `poetic` holds the 261 words every name rule bans, written capitalised so the type rule matches them in a class name, `poetic_values` the 177 words banned in parameters and variables but allowed as methods, and a rule names a list as `${poetic}` in its matcher; the method rule's 64 own words and the type rule's 98 own class names stay inline. A banned word is added to the list once.

## Plan 19, phase 2, task 983: Idle is the plan's (2026-10-21)

- Idle keeps quiet_since and parked_asked; a start, a prompt and a tool use make it active again. on_stop holds in the order parked, broken wait, approved plan, next open task in auto mode, and passes a stop held once this turn; on_ticked asks about a parked task once after a minute of quiet, a blocked task with no wait after 45 minutes, and checks in after half an hour in auto mode. The listener is on_stop though the event is still named Idle: the event's rename to Stop waits for the chart's deletion, since the chart keys its triggers by the event's name.
- The tasks readings names what the stop and the tick read in words: parked_named, broken_waits_named, blocked_without_wait (a blocked task with no wait link, nothing the journal can see that opens it) and next_open; the plans readings's approved plans. Plans.APPROVED_UNSTARTED is a nudge of the plans feature now.
- The seven idle drawings are gone; the approved-plan drawing stays for Working until task 984.
- The riddle nudges are named for what they do: parked_task_asked_about, blocked_task_asked_about, check_in_after_quiet, parked_task_named_at_close; TaskOpenedAgain and PlanOpenedAgain are TaskReopened and PlanReopened.
- A state prints with the fields set past their defaults and no times: working(task_id=3), idle; the panic command and the trail read it from BaseState.printed.
- The 71 tests of the chart itself are dropped ahead of phase 3, since the suite carried every chart walk; the shell's short and shown limits are 400 characters (message 10389); the code-commandments plugin runs v5.20.1.

## Plan 19, phase 2, task 984: Working is the plan's (2026-10-21)

- Working keeps edits and active_at beside task_id, what and logged_at. A write past tasks.log_after is refused until the log line; at tasks.first_nudge_after edits behind it the log is asked for, and every tasks.name_every the task in hand is repeated; the asks read the edits already made, so "5 edits since you logged" comes on the sixth write. A stop is refused while an approved plan is not started, with the log line first when the log is ten minutes old, else with carry on, and a stop held once this turn is refused again: with a task in hand there is no escape by stopping twice (the standing test), where doc 55 let the second stop pass. A session start says carry on, and after a compaction where the work stands, from the tasks readings's last log line and the git readings's uncommitted files. A quiet quarter hour is told the task is still open. TaskLogged keeps logged_at, TaskClosed pops, and on_resume pops when the task is no longer in hand, else says carry on.
- The machine hands a resumed state the agent's readings (through_hooks takes it; a move by hand reads it inside the agent's environment). A refusal of a switched-off feature passes: the machine asks the nudger whether the nudge is silenced before refusing.
- The nine working drawings are gone, the approved-plan drawing with them.
- Standing is Readings everywhere (messages 10270, 10423): Readings, <Feature>Readings, <Feature>SnapshotReader, event.readings, SnapshotReaders. The look stays until its column migration (task 1101: oriented becomes overview_read, LookTaken becomes OverviewRead).
- Names renamed on the way: task_in_hand_repeated, last_log_line, the *_summary fields, rules_numbered, facts_numbered, reminders_numbered, last_other_session_at; the rules ban held, hold, named, back and forth as well.

## Plan 19, phase 2, task 985: FollowingPlan is the plan's (2026-10-21)

- FollowingPlan extends Working with plan_id, approved, moved_from, at_checkpoint and phase. A push of an unapproved plan is refused (PLAN_NOT_APPROVED). At a checkpoint a stop is refused in auto mode with the phase complete and go on, else told the user looks first; a session start says the same; a tool use counts nothing. A task's close keeps the state with no task in hand, at the checkpoint when the readings says so; the next task's start, by the plan or by number, keeps the top as that task; PlanDone pops with the plan done line.
- Only a state moves the agent: Idle pushes Working on TaskStarted and FollowingPlan on PlanStarted (or on a task of the started plan); Working becomes FollowingPlan when its task's plan starts; a blocked task carries its close like a done or parked one, so the state lets it go. InHand.start and the plan control's start only write rows; AdvancePlan only writes the next task, finding the follower by the stacks on the agent rows, and the plan's end is PlanDone carried by Plan.done(at).
- The three following-plan drawings are gone. A plan parked or abandoned still moves the agent by the plan control until task 1061.

## Plan 19, phase 2, the last tasks and the replays (2026-10-21, early morning)

- A closing command prints the next task (number, title, brief) itself; the plans conduct types the plan's next task only for a start the agent did not cause: every row event carries the actor's stamp (RowEvent.actor, by_agent) (task 1076).
- One tool-use counter per session lives on the agent's row (Agent.tool_uses), moved as a plain tool use of the agent's own is placed (hooks ToolUses) and carried on ToolStarting and ToolFinished as tool_use; a journal command and a subagent's use carry the unchanged number, lift no wait and earn no inbox reminder. The inbox counts from the mark a message's arrival leaves (Agent.inbox_mark, set by MarkInboxArrival on MessageArrived) and from the count a message was read at (Message.read_mark); the namings since a message are nudge entries with a tool_use at or past the mark (Entries.nudge_count); the pin suggestions count the same way (task 1085).
- A paused session ends its turn: PausedByUser refuses every tool but a read of the user's messages, the messages conduct names the inbox at a stop only where tools are not all refused (BaseState.refuses_every_tool), and the inbox is named again on resume (task 1088).
- Awaiting (features/tasks/states) is the one wait on something outside the chat: what in words, ends_on as table:id refs (workers, outputs, checks, tasks, questions), start_time, reminder_time, next_task_named, outcomes. A worker's dispatch pushes it (Awaiting.on_workers) and widens it; a wait on workers stands through the agent's own tool use, any other is lifted by it; the last row settling pops it with WAIT_OVER. Expecting and the workers' Awaiting are gone (task 1096).
- The ToolCall is the one reading of a line: its parts carry reads_output and read_shape, Running.names and AnnouncedCommands compare parts, RecordEdit and SpotCommit read the call, and a tool entry records the call (Entry.recorded_call, is_write) beside the raw hook; nothing outside the provider's call() reads a line into parts but the shell runner, which runs it (tasks 1111 to 1114, 1112).
- Working says nothing on resume (the wait that popped said what came; the start block names the task after a compaction), counts its still-open reminder from the agent's quiet time, and says the name-back beside the log line. The machine types a tick's lines; the clock only dispatches.
- The replay harness runs one journal (played) and lists what differs from the record; a step records the stack, not the chart's counts; records are re-frozen only where the conduct changed on purpose, each reason in task 991's log; the replay fixture switches the chart feature off (tasks 1043, 991).
- The name rules match a word anywhere in a name, ignore case, forbid prepositions, pronouns, adverbs, verb forms, slang nouns and the journal's voice, have sentence rules for parameters and class names, and flag a string standing alone at the top of a file; report 32 holds the two readers' findings. by is forbidden too: the briefing says save(row, actor) and task 1135 renames it. A quantity names its unit (task 1133).

## The ruling: the workflows are gone (2026-10-21, phase 3 of plan 19)

- The chart feature, its models, repositories, support, controller, routes, page, command, skill and docs are deleted; the states and the conducts carry every line (docs/the-rules.md is generated from the source and names each state and each line's sayer).
- Migration 19 keeps a workflow the user made or edited as a document, 'Workflow: <title>', from its nodes and lines, then drops charts, nodes, counts and noted_times, the node_of, yes, no and then links, the settings listeners.off, chart.drawings_version and features.chart, and the walk entries. The migrations 6, 15 and 16, which touched the chart's tables, are deleted; migration 13 indexes no counts.
- The keeping of the user's workflows as documents was the orchestrator's choice; the pull request says so.

## Plan 19, phases 8 and 9 and the morning's rulings (2026-10-21)

- The compacting state is on the stack at last: the chart's leftover `AgentState` answered the compaction with
  stay and the catalogue did not know `Compacting`, so no compaction had ever pushed it. `AgentState` is gone;
  `Idle` and `Working` extend `BaseState`.
- A listener may stop an event's propagation, `event.stop_propagation()`, and the listeners after it never hear
  it; the walk starts again at the next `on`. The compacting state uses none of it.
- A state entering or leaving the stack is handed the typist, `on_enter(typist)` and `on_exit(typist)`, the
  lifecycle handlers that come first in a state class (rule 2, detector `lifecycle-handler-not-first`). The
  typist has pause and resume (queue, then type as one), disable and enable (queue nothing), and clear. The
  compacting state clears and disables on entering and enables on leaving: a line the journal would type while
  the context compacts is dropped, since the look at the next start brings the agent up to date. The tool-use
  count and the inbox mark go back to zero at a compaction.
- The work mode is the floor state: `Idle` is the builder's, `Orchestrating` and `Soloing` are swapped in by the
  `workers.mode` setting at a session start, at the setting's change and on resume, through `Workers.MODE_STATES`,
  never an if on the mode. A floor pushes its own family: the orchestrator's pushes `OrchestratingPlan` and
  `Delegating`, whose lines say hand it to a worker where the builder's say carry on; the orchestrator's floor
  answers a stop, a long quiet and a worker's report with the open tasks across the plans and the workers to
  dispatch. The solo floor refuses a worker's dispatch at the floor. Proven by a test driving an orchestrator
  through a plan of twenty tasks with three workers out at once.
- The plan's listener finds its follower by the state's class, `isinstance(state, FollowingPlan)`, never by the
  state's name: by name, the orchestrator's plan state never advanced the plan.
- A fact, rule or reminder carries its presence in the agent's context window. The start block hands every row
  over at a session start (a listener sets them all), the look hands them all over, and `journal <noun> read <n>`
  hands one over; a keyword hit on a row not in the context tells the agent to read it, never its words. The
  funnel is `MemoryContext`.
- A secret's field shown while typing is no secret: its value is kept for the programs and named in the shown
  file beside the values, and only a hidden field's value becomes a mask.
- Still open: the
  plugins upgraded by a `journal.updated` event (task 1167); the remote journal two people share (task 1164); the
  rest of the name sweep (task 1052) and the custom name detectors' noise on every `on_` listener.

## Plan 19, phase 5, the live checks (2026-10-21, late morning)

- A real Claude session on Sonnet and a real Codex session, headless and resumed at every step, each walked a
  scratch journal (port 8765) through a task, a log, a question answered from the user's side, a worker whose
  real report popped Awaiting, an await on a flag, a plan with a checkpoint approved from the user's side, refused
  to start while a task was in hand, done through its checkpoint in auto mode with the stop held by the parked
  task, the parked task resumed and done, and `journal panic now compacting` from the user's side popped by the
  next start. The nudge keys match doc 55's table; the rail has no Workflows entry; the chart route answers 404.
- Found on the way and fixed: `journal question show` crashed on an answered question's link (a Ref has a type,
  not a table); the chart drop counted a shipped workflow's revisions as the user's edits and wrote documents for
  them, now only workflows a user or an agent last wrote are kept.
- Noted: Codex sends no session-start hook, so a Codex session cannot end an earlier one that still runs in its
  environment; a scratch set up from a source checkout needs `.journal/journal` for the global command to find
  it; the Building-a-plan sequence stays open on its first step when the agent builds the plan by commands.
- Environments: on a second and a fresh third environment, Claude and Codex each put every row where it belongs
  and nothing on the first; the old fault of Codex going to main is gone.
- Two records from before the chart's removal, backed up from other journals on this machine, upgraded in-process
  through App and Config: 22 migrations, the chart tables gone, every live agent's stack seeded.

## The type check passes (task 1173, 2026-10-21)

- `python3 -m mypy src/journal` finds no error, and it stays that way: an Optional the design always has is made
  certain where it is born, never cast or ignored.
- A saved row answers `row.row_id`, `row.creation_time`, `row.update_time` and `row.creation_actor`; each raises
  `UnsavedRow` on a row not yet saved, so code that needs a saved row says so and `Model.id` stays `int | None`.
- `Conduct` extends `BaseState`, not the other way round: a conduct's listener runs with the state as itself, so
  it is typed as one, and the answers `none`, `swap`, `push`, `pop`, `forward` and `refuse` live on `BaseState`.
  A conduct holds its `on_` listeners and nothing else; a helper one listener merges is a module function that
  takes the state.
- A setting is read by its option's kind: `settings.integer`, `decimal`, `texts`, and `SettingRows.mapping` for a
  raw key, each raising `WrongSettingType` on a stored value of another kind.
- An entry's data is a dict, empty when it has none. A phone's and a pairing code's expiry is required.
- A route answers `Answer`, a JSON response, a file or a stream; `Router.page` is what a phone may reach, never a
  stream.

## The task in hand per agent (task 1232, 2026-10-21)

- Each agent has its own task in hand: an `in_hand` link from its holder to the task, written by `Tasks.holder_started`
  (and `assign_holder` for a plan's start, before the plan's row moves) wherever a task starts, the one-task
  refusal checked per holder there. `Tasks.current(agent)` is the started task the agent holds.
- The holder: a worker's command makes the worker row the holder, since a worker's hooks never reach the journal and
  it has no agent row; an agent's command its own agent row; the user, at the terminal or in the viewer, the
  environment's agent at work; a plan's next task, whoever held the task that closed. A task started by another
  moves to it, and the link from the one before goes.
- The tasks data carries `agent_tasks`, the tasks this agent holds; Ready, PlansReady and FollowingPlan push or swap
  only for a task of the agent's own, and the plan's next-task line goes to the agent that holds it. SingleTaskRule
  is gone: the refusal lives where the holder is known.
- The viewer's task inspector shows "Held by" on a started task: a worker by number and name, an agent by program
  and session.

## The shared journal

- **Environments are matched by key, never renamed (task 1558, 2026-10-23, Sir Jesse's word).** An environment
  carries a random key, made with it and never changed, uniquely indexed. Its `name` is a local field
  (`Model.local_fields`): it never leaves the machine, so joining a team changes no name on this machine and moves no
  worktree. Its `team_name`, the owner's prefix before the name, is what the team server and other machines know; a
  pulled environment takes its team name as its local name. A join's download re-owns this machine's environments by
  key, or makes them anew under their team names. The rename this replaced left a joined journal unable to find the
  environment its running agent had started in.

Plan 24 builds it on the branch shared-journal, from doc 62 and report 42.

- **What is shared and what stays on one machine.** Every model has `shared`, true by default. Kept on one machine: Entry (the hook and timeline log), Agent (the state stack), Statistic, CommandOutput, DashboardRow, Secret, Phone, PhoneCode, MigratedRow, Version3Migration, JournalVersion, ReleaseMessage, BrowserSession (a hosted journal's sign-ins), PoolJob (a worker the team's pool offered this machine), ScheduledJob (a prompt an agent scheduled in its own program, which lives only in that session), ReaderReport (what the reader judge found of a run on this machine), ReaderSuggestion (a part the journal suggested a reader for on this machine), TestTurn (a worker's turn to run tests within the test budget, on this machine), Verifier (an agent the journal sent on this machine to judge one dismissal) and Reviewer (an agent the journal sent on this machine to review a clocked-out worker's work), and also Plugin and McpServer: a plugin is a program installed on the machine and an MCP server's command and keys are the machine's own. Alias is shared: the team runs the same project commands.
- **The two lists, as the code stands (task 1488).** Shared: aliases, checks, collections, doc_revisions, docs, dumps, edits, environments, facts, links, messages, notices, phases, plan_reviews, plans, proofs, questions, reactions, reminders, reports, rules, sequences, settings (the team's scope alone), shares, subagents, suggestions, task_logs, tasks, templates, triggers, users, worker_todos, workers. On one machine: agents, browser_sessions, command_outputs, dashboard_rows, entries, id_blocks, journal_versions, mcp_servers, migrated_rows, outgoing_changes, pending_uploads, phone_codes, phones, plugins, release_messages, secrets, statistics, version3_migrations. A worker's, a worktree's and a process's row is shared, but the process, its worktree and its branch belong to the one machine that runs it (the worker's device), and only that machine acts on them. .journal/team.json holds this machine's device token, mode 600, so it is never committed and never synced.
- **What a state hears from another machine.** A pulled creation fires SyncedCreation and the row's creation events, so a state hears a task or message made on another machine as if it were made here; a pulled update fires SyncedUpdate alone and a pulled deletion SyncedDeletion, which no state hears, so an edit made elsewhere never moves an agent here. A write that skips a repository is not synced at all, which is why no write may (WriteOutsideRepositoryDetector).
- **The admin's upgrade, step by step.** 1. journal team upgrade <version> pins the team; every member's status bar asks for it and, with versions exact, every journal on the old version stops syncing, its writes waiting in its queue. 2. The first member to run journal update apply takes the upgrade lease, sends and pulls everything, installs, migrates and uploads the migrated copy; the server keeps the copy it replaced in backups/. 3. Every other journal installs the version, boots, migrates its own copy, is told to take the team's copy, takes it, lays its waiting writes on top (a renamed column renamed in them too) and sends them. A member offline through all of it does step 3 when they come back. The team server's image is upgraded on its own (host/install.sh again, or docker pull and restart); an older server is named in every member's status bar by the protocol check.
- **The outgoing queue.** Every write to a shared row is queued as an OutgoingChange (local, out of the timeline) by RecordOutgoingChange, a ModelEvent listener in the write's own transaction, but only once the journal has joined a team, which is the file .journal/team.json the join writes (TeamAccount). A creation carries every stored column, an update only the columns it changed with updated_at and updater, a deletion none; each field keeps when it was changed, so a merge never lets an early field win. Waiting changes to one row fold into one: two updates one, a creation and its updates one creation, a creation then a deletion nothing, an update then a deletion a deletion. A change being sent (is_sending) is never folded into; a later write starts a new one.
- **Row numbers from blocks.** Once joined, a new row of a shared model takes its number from an IdBlock (local, out of the timeline) the team server handed this machine for its table; a local model, IdBlock itself among them, is still numbered by SQLite. The base Repository reaches the numbers through the bus, not its constructor: `_insert` dispatches NumberRequest and takes the first answer, which BlockNumbers gives from IdBlocks, so no repository depends on IdBlocks and the container has no cycle; with no answer SQLite numbers the row. A used block is removed. A table wants a new block once fewer numbers are left than its biggest block and a fifth of one, so a full reserve block is always held; how big a block is per table (messages and links far bigger than plans) is the server's to say. A write that finds every block used, after days offline, is refused with a line saying the journal has to reach the team server first: a number another machine might give is never made up.
- **Pulled changes.** IncomingChanges writes each TeamChange the server passes on through SharedTables, a plain TableRows repository per shared table (AllModels is a tuple, so this is the one map from table to repository). A pulled creation upserts the row (Query.upsert) and fires SyncedCreation and the row's creation events, so a pulled task opens; a pulled update writes only the fields it carries and fires SyncedUpdate; a pulled deletion fires SyncedDeletion, removes the row's links itself and drops this machine's waiting change to the row. A pulled row's updated_at is the moment it was applied here, not the edit's own time, which the server keeps and settles by, so the viewer, which fetches rows newer than the newest it holds, finds an edit made a moment before its last poll. None of them fires Created, Updated or Deleted, so no listener that acts on a local write runs and nothing is queued back; RecordChanges records the Synced kinds so the viewer refreshes, and PulledSettings clears the settings cache. A field this machine's own queue still holds is skipped: its value is sent and the server settles it by time. A column this machine does not know yet is left out; an upgrade that adds a column needs that table copied whole from the server again (open, for the full copy in phase 2).
- **No write skips the repository's events.** SQL stays in repositories (the custom WriteOutsideRepositoryDetector), and the raw delete is now `_purged`, private to them. A delete of many rows at once, an environment's wipe or a row's links, goes through `Repository.purged_rows(model, query, actor)`, which names every row it removed in a Purged event; RecordPurge queues each shared one as a deletion of its own, so the server's copy, which a new person downloads, keeps no ghost rows. A pulled wipe needs no wipe of its own: every row it removed arrives as a deletion. Only the local Entry log still trims with `_purged`. Migrations write raw SQL, but run the same on every machine. `touch` writes past `_update` but fires Updated, so it is queued.
- **A worker belongs to the machine that runs it.** A worker row carries `device`, stamped by WorkerRunner.start from TeamAccount.device (the device id in .journal/team.json, empty in a journal in no team). WorkersSeed hands the watch only this device's workers, and WorkerActions finds every worker through `local`, which refuses another device's: send, notify, stop, complete, release, check and merge. Subagent rows hold no process, so they carry no device. The viewer hiding those buttons waits for task 1503; team create stamping the first journal's existing workers waits for task 1463.
- **Shipped shared rows are written by one machine.** BuiltinTemplates and BuiltinSequences insert shared rows, so two machines booting a new release would write the same template under two numbers. In a team they run only on the machine that holds the team's upgrade (TeamAccount.is_seed_writer: upgrade true in team.json, set by the upgrade under its lease, task 1516); every other machine gets them in the team's copy. ClosedPlans only updates rows, which settle like any edit, and SubagentsSeed runs only while the table is empty, which a joined journal's never is; the other seeds write local rows.
- **Settings have a scope (doc 62's open question 9, settled).** Every Option has `scope`, OptionScope.TEAM unless it says otherwise. MACHINE: the tunler host, the update repository, branch and auto install, and the worktree step and its preparation and completion commands, which name this machine's tools. PERSON: every voices option and the work mode, which shape how one person's agent is treated. RecordOutgoingChange queues a setting only when SettingScopes says its key is the team's, so a machine's or a person's setting never leaves the machine. A person's settings following them to another machine waits for the person's own environment (phase 4, tasks 1469 and 1497).
- **The team server, src/sync_server.** A stdlib-only package that knows no journal concept, one class per file, copied into .journal/src by install.sh beside journal and supervisor. It is layered like the journal: SQL text lives only in sync_server/db, the Store (its one door, one writer at a time), ServerSchema (its own numbered migrations and version) and one rows class per table; Accounts, Devices, ChangeLog and IdRanges hold the rules above it. The custom rules SqlOutsideDatabaseLayerDetector and QueryOutsideRepositoryDetector name src/sync_server/db beside src/journal/db. Passwords are a salted PBKDF2 hash in sync_server/password.py, which the journal's share links import too, so the hashing is written once. A login trades an email and a password for a device token kept only as a hash; five failed logins from one address in fifteen minutes shut it out for fifteen minutes, the address being the one the proxy forwards. The log keeps every change in order and every row's current value; a device never pulls its own changes. Number blocks start above every number handed out and above the highest a journal had when it became shared.
- **A push is settled field by field.** PushHandler stamps every change with the account and device of the token, never with what the request says; a change whose actor is user:N for another person refuses the whole push before anything is kept, while agent, worker, plugin and system actors are the sender's. The device measures its clock offset, the server's time from its last answer minus its own clock at receipt, and sends it with each push; the server adds it to every changed_at, so all times are on the server's clock. A creation and a deletion are kept whole; an update to a deleted row is dropped and sent back as a rejected row; an update keeps each field whose edit is not older than the one the server holds, an equal time going to the later push, and every older field is sent back as a RejectedField with the value and time that stand. The answer names the sequence each change took, zero for one dropped, and the server's time.
- **The server's HTTP.** TeamServer puts the server together over team.db in its data folder (python -m sync_server --data <folder> --port 8470) and serves it with a ThreadingHTTPServer, so a held pull never stops another request. POST /login {email, password, device_name} answers a device token; POST /push {changes, clock_offset} and GET /pull?after=<sequence>&wait=<seconds> and GET /copy carry the token as Authorization: Bearer. A pull answers the changes past the sequence, not the device's own, holding the request up to 25 seconds while none are new and answering the moment one is logged; it records the sequence the device holds (devices.pulled_sequence, which the log trimming of task 1487 reads). /copy answers every row not deleted and the sequence they stand at, read in one transaction. Every answer carries the server's time. A refusal is a 403 with its line, an unknown path a 404. The login address is the first X-Forwarded-For entry the proxy sets, else the peer's.
- **The sync client.** A joined journal (.journal/team.json, mode 600, written whole through a draft: address, token, device, sequence) is carried by the sync service (below). Its send loop takes the desk's batch of up to 200 queued changes oldest first, marked sending, pushes the body the desk builds and hands the answer back, the desk removing them only once the server answered; a commit that queues a change is posted to the service as change_queued, so the change goes at once, and an idle loop looks again every five seconds. Its receive loop long-polls with the desk's query; the desk applies the answer through IncomingChanges, records the new sequence, and measures the clock offset from the answer's server time (ClockOffset); the next push carries it. On a network fault or a refusal both loops wait 1, 2, 4 seconds and so on up to 30 and try again, and the service reports the fault, which SyncStatus shows on the status bar (GET /journal/sync); in a journal in no team the line is empty. Closing the team server releases every held pull, so the clients notice at once.
- **The account is kept per team (task 3136).** A join writes .journal/teams/<team key>.json, with the team's key and its number T beside the token; TeamAccount reads the one file there. An account from before teams had keys stays in .journal/team.json until the sync desk's refresh asks the team server's /team for the key and records it, which moves the file; nothing is renumbered. A team server made since draws T between 1 and 2^21 - 1 so T * 2^32 + n stays below 2^53; a server from before stores none and reads T = 0. The pull answer was left alone, since an older journal refuses an answer with fields it does not know. Open: one team per journal until TeamAccounts lists several.
- **Several teams (task 3132).** TeamAccounts lists one account and token per team (teams/<key>.json), the home team's marked home, the first joined. A join adds a further team beside the others: refused for a team held already or one whose number T is held, so a journal holds one team of T = 0. A new further team takes its hub and uploads it with a TeamServerLink bound to that team's account; one with rows is laid beside, refused while any incoming number is one this journal uses, until task 3158 gives each team its own number space. The person a viewer, CLI or shell write is stamped with is their account in the team of the environment the request names (TeamAccounts.person_in), else the home team's. Each OutgoingChange records its team key, and the sync desk's batch takes the home team's and no team's alone, so another team's change never reaches the home server. Open: one team-root.crt and one team-prefix are shared by all teams; users rows are numbered by account and can clash across teams. A team server takes only journals of its repository unless made with serve --any-repository or untied by its admin with journal team repository untied (team_details repository_tie, /team/repository, TeamSummary.tied_to_repository).
- **Each team on its own carrier, numbers apart (task 3133).** A team server hands out blocks from T * 2^32 on (IdRanges), and a journal holds one team of each T, so two teams' numbers never meet. A block on the journal names its team (IdBlock.team_key, none for the home team), and BlockNumbers takes a new row's number from the blocks of the team TeamPlacement gives it when that is a further team, the home team's otherwise, refilled through a BlockSupply bound to that team. The sync service runs TeamCarriers beside the home carrier: one Carrier per further team the journal lists at /journal/sync/teams, its JournalDoors naming the team, whose doors answer from that team's TeamDesk (its sequence, its queued changes, its pulls and its full copy, laid in place of that team's rows alone). The home team keeps files, host requests, leases, the upgrade and the sync state. Open: a further team's carrier sends no files and reports no state; a further team's changes are applied with the home team's person for what a withdrawal keeps.
- **Leaving and removal (task 3157).** sync_server/departure.py frees every lease the person holds, clears driver and driver_agent on hub tasks and plans that name them, and withdraws each environment they share (owner link users:N, kind local with a team key) with its rows and the links touching them, kept_by user:N: colleagues' journals delete them, the person's own keeps them. The admin's journal team remove <account> (POST /people/remove) runs it at the server, where the person may be offline. A journal's team leave asks POST /people/leave first and unbinds its drives. When the server cannot be reached the journal still leaves and says so: its drives lapse by themselves and its shared environments stay until an admin removes the person. A read-only hub document of theirs stays editable by an admin (task 3121); local copies never were on the server.
- **A join keeps the journal's own rows (task 3165).** The refusal and --replace-mine are gone. A journal joining a team that holds a journal first moves every row of its shared tables (users aside) into its new blocks with RowRenumbering, in one transaction: ids, every environment_id (local tables too), link ends, task_logs.task_id and workers.edited_task, user:1 stamps to the person's account, and attachment folders. Then JournalCopy.laid_beside lays the team's copy in, deleting nothing; a team environment with the key of a kept one is left out and its rows go into the kept one, and a kept team-scope setting gives way to the team's. Kept environments the team lacks are sent with their owner links, as the old join did; their older rows stay local. Phase 1 lays in the team's whole copy, since TeamPlacement (3112, 3113) does not exist yet to pick the hub's rows. Open: ids inside message data, and task ids an agent's state stack holds, are not renumbered.
- **TeamPlacement decides (task 3112).** src/journal/sync/team_placement.py answers the team key a row belongs to, or none: an environment when it is a hub, a session or shared; a scoped row with its environment (environment 0 in none); a link when both ends are in one team; a user in the home team; a setting of team scope in the home team when the project's, else with its environment; anything else, rules and templates among them, and every row kept on one machine, in none. It dispatches by the row's class through a table, not an if per kind.
- **Only a hub team's rows are sent (task 3113).** The team server marks a team on the hub in team_details (hub = on): a server made since is, one from before is once task 3116 has moved it (TeamDetails.record_on_hub). /team answers on_hub, the join keeps it in the account file, and TeamPlacement.is_sent asks placement on a hub team and the old rule (every shared row but a person's or machine's setting) on any other. RecordOutgoingChange, RecordPurge and JournalCopy.rows ask is_sent; Purged now carries the purged rows, parsed from the read the purge already made, so a purge is placed too. BlockNumbers is unchanged. Tests that start a team server for today's sync mark it before the hub (tests/before_the_hub.py). Open: a deleted link whose ends are already gone places in no team, so its deletion is not sent; RecordWithdrawal still reads SettingScopes; Hosts still sends a viewer write in the hub to the hosted journal (task 3166).
- **Where sync runs (task 2967, 2026-10-24).** The journal server and the sync service are standalone programs that know nothing of the supervisor, which keeps both alive and ends them. The launch file names the journal service alone; the sync service is the team feature's declared service (Service("sync", "sync_service"), python3 -m sync_service in the project's folder), which ServiceStart asks the hosting supervisor to start at every boot of the server, one already running left alone, so an install or an upgrade brings it without a relaunch (task 3026: a launch file is written at launch, so one written before the upgrade named the journal alone and the journal stood at Connecting to the team server). The server's SyncDesk writes everything sync brings and takes; src/sync_service, standard library only, importing no journal code and opening no database, only carries. It reaches the server over /journal/sync (JournalDoors: the port file and runtime/sync-secret read on every call, no environment named, a server that is down, starting or on a new secret a quiet wait, JournalBusy): /team says whether the journal is in a team and how to reach the team server (address, headers, certificate authority, least protocol), /batch hands the push the desk builds, every team answer goes back raw, and /state takes the service's fault each second, a service that has reported and then stays quiet for 10 seconds showing as not running, and one that has not yet reported as connecting. The server offers service hooks (ServiceHooks, src/journal/services): a service registers at POST /journal/services with the service secret, naming its address and its events, and the server posts each event to it on a thread of its own (change_queued, team_joined, team_left, and upgrade_preparing, which the updater waits on while the service sends the queue and pulls to the head under the upgrade lease, then upgrade_abandoned when the install is refused). Registrations live in memory; the service registers again whenever the secret is new. Its event listener answers GET /health with 200 while its loops live. Nothing under src/journal starts or stops a process for sync, and the supervisor has no child services any more; the custom rules SupervisorServiceVerbDetector, ParentPidWatchDetector, ParentPidVariableDetector, SupervisorImportOutsideLauncherDetector, SyncServiceImportsJournalDetector and SyncServiceOpensDatabaseDetector keep it so.
- **A rejected edit is put right and named.** The server keeps, beside each row's fields and times, the account that wrote each field (rows.writers), and a RejectedField carries the name of the person whose value stands. After a push the client applies what came back through RejectedEdits: a field takes the value that stands unless this machine has edited it again since, a row deleted meanwhile is deleted here with its links, and a card of the new kind conflicts (Show in chat: Your edits a colleague's newer edit replaced) in the row's environment says whose edit was kept. The server's Store fetches and closes under its lock, since its request threads share one SQLite connection.
- **A push sent again is kept once.** Every pushed change carries local_number, the OutgoingChange's row number, which merging keeps and which a change being sent is never merged into. The server records its answer for each (device, local number) in push_results in the same transaction as the log entry, and answers a repeat with that first answer, rejections included, so a push whose answer was lost is never logged twice nor rejected by itself. A pull never returns the device's own changes. A held pull waits on the newest sequence ChangeLog keeps in memory, never on the database, since a push wakes the pulls while it holds the store.
- **Every person's write names them.** TeamAccount.user_number, the account_id in team.json and 1 in a journal in no team, is the one source of the person. Identity stamps the viewer's writes with it, the shell and CLI controllers hand it to CallerVariables.caller (Caller.person, whose actor is user:<person>), and the typed prompt and the updater stamp with it; LOCAL_USER stays only as that default. The team's admin is the server's account 1, so a journal that becomes the first shared one keeps its user:1 stamps true. The server checks only user:N actors against the sender; agent, worker, plugin, phone, external and system actors are taken as the sending device's person, and the change records that person's account beside them. The join writes the person's User row (task 1463). A phone is numbered per machine, so on a shared journal a write a phone makes through the viewer is stamped with the person whose machine it is paired to (TeamAccount.phone_actor), while the phone's own rows, which are local, keep phone:N; a plugin's stamp names a program and an external one a sender, which mean the same on every machine.
- **The team server's administration.** POST /invite (admin) hands out a code for one email, kept as a hash, used once and gone after a week; POST /accept turns it into a member account with the password typed twice (refused when the two differ) and the first device token. GET /devices, POST /devices/revoke and POST /people/remove are an admin's; removing a person revokes every device of theirs and refuses their logins. POST /blocks hands a device a block per table it names: 500 rows, 5000 for messages, links and edits, 2000 for reactions and task logs, 1000 for document revisions; the sync client asks before each batch for every shared table that holds less than a block and a fifth. POST /upload (admin) takes the first full copy of a journal that becomes the team's, every row as a creation and each table's highest number as the floor of its blocks, and is refused once the log holds anything (phase 8 needs a re-upload). Every route refuses a missing, revoked or removed person's token, and a body that is not what the route takes, as a 403 with its line.
- **The team server's image.** docker/team-server/Dockerfile, built from the repository root (its .dockerignore lets in only src/sync_server and docker/team-server): python 3.13 slim with the server package, and the caddy binary copied from the caddy image. run.sh starts the server on 127.0.0.1:8470 and Caddy in front of it, and ends the container when either ends, so Docker restarts both (run with --restart unless-stopped). TEAM_ADDRESS is the name Caddy gets and renews a certificate for; TEAM_PLAIN_HTTP=1 serves plain HTTP on port 80 for a private network; neither set is refused with a line. All state lives in the /data volume: /data/team/team.db and Caddy's certificates under /data/caddy. Caddy sets X-Forwarded-For, which the login lock-out reads. tests/team_image_run.py builds the image, logs in over HTTPS on localhost (Caddy's own authority), restarts it and logs in again; it needs Docker and is not in the default run. - **One command sets up a team server: host/install.sh.** Run on the server, also as curl | sh, since its prompts read the terminal; TEAM_SETUP_STDIN=1 reads them from standard input for a test. It asks the project's name, the admin's name, email and password twice without echo, and the address; makes the volume agent-journal-<project>, refusing a project set up already; runs python -m sync_server setup in a one-off container, the answers as JSON on standard input so the password is never on a command line, which makes the admin, account 1, and a join code for the admin's own email; starts the server with --restart unless-stopped on 80 and 443; waits until it answers over HTTPS, and if the certificate cannot be got says so with Caddy's last lines; and prints journal team join <address> --code <code>. A bare IP address gets no public certificate, so Caddy serves its own (TEAM_CERTIFICATE=internal, with default_sni set, since a client sends no server name for an address) and serves its authority at /root.crt, and the join line carries --fingerprint, the SHA-256 of that authority, which the join checks (task 1463). The image defaults to ghcr.io/jessegall/agent-journal-team:latest, published by task 1500; TEAM_IMAGE names another.
- **journal team.** The team feature's command has join, login, invite, status, devices and revoke; create is not a verb of its own, since the first journal to join a team whose server holds no rows uploads itself whole (TeamJoin.uploaded: every shared row with its stored columns, each table's highest number and the repository's first commit) and stamps its device on its workers, while every later one downloads the copy, applies it through the tables' repositories and writes its person's User row as a queued creation. Join checks, before it makes any account, that the server's repository is this checkout's (GET /team, open to anyone), and with --fingerprint first fetches the server's certificate authority, checks its SHA-256 and keeps it as .journal/team-root.crt, which TeamServerLink trusts from then on. The password never stands on a command line: the journal shim asks it unseen when a person runs team join or team login in a terminal and adds it to the words it posts; without it the command says to run it yourself. The sync client starts once the join is done. Joining a team that has a journal replaces this journal's: the whole database is first copied to .journal/journal-before-team-<time>.db (JournalBackup), every shared table, the outgoing queue and the hook log (Entry) are emptied without events, the team's copy is applied, and every Agent row, which holds a running session's stack and so is kept, is moved to the team's environment of the same name. A joined journal never makes environment main at boot; environments made on demand by name are phase 4's (task 1502).
- **Each environment has an owner and names its person.** An owner link, Link(users:N, environments:M, kind owner), is written by EnvironmentOwnerRecord for every environment created on this machine, owned by this machine's person; a colleague's environment arrives with its own link, since a pulled row fires no Created. EnvironmentOwners (in repositories, since it only reads links and users) answers an environment's owner and whether a user actor is a colleague there. The join writes .journal/team-prefix, the person's first name in lowercase, and environment.sh puts it before every environment name a shell works out itself (jesse-main, jesse-<worktree>), so hooks, commands and the viewer ask for the person's own environment; a name JOURNAL_ENV sets, as the launcher does, stays as it is. The first journal of a team links its environments to its admin, renames them with the prefix and names the admin's user row before it uploads, all before it counts as joined, so they take local numbers and travel in the upload; the sidebar shows each environment by its name, which carries its person, and EnvironmentData carries the owner's name for the viewer (task 1503). A join fetches its number blocks before it writes any new row. Invitation codes are hexadecimal, since a code beginning with a dash read as an option.
- **No agent starts in a colleague's environment.** EnvironmentOwners.start_refusal is the one rule: an environment owned by another person refuses an agent, naming its owner. The viewer's Start button (EnvironmentController.launch) asks it directly and answers the refusal; the launcher, which both the picker and the Start button end in, reads it from the refusal field of the rows journal environment json gives, prints it and exits with 1. With no terminal to pick in, the launcher starts in the person's own main (<prefix>-main) on a joined journal.
- **A colleague's visit marks nothing read.** Messages.read leaves a message as it is when the reader is a user who is not the owner of the message's environment, so a colleague opening a chat never changes its owner's unread count; an agent's read and the owner's go on as before. Naming people relative to the viewer (you, Anna de Vries, Anna's agent) is task 1503's.
- **In a colleague's environment a person only comments.** ColleagueWriteGuard hears every Saving and Deleting and refuses, before anything is written, a user's write of a shared row in an environment another person owns, the environment row itself included; a message passes, with the links it brings, and becomes a comment in phase 5. The rule is EnvironmentOwners.write_refusal, which the viewer's stop of a colleague's agent asks too. Only a user stamp is ever a colleague: a phone writes as its person on a shared journal, and this machine's own records, such as the hook log, are no colleague's. Agents, workers, plugins and the journal itself write as before.
- **Environment names never clash across machines.** On a joined journal every name a person gives a new environment carries their prefix: environment.sh for the names shells work out, TeamAccount.personal_name for the viewer's New environment and journal environment create; a name the launcher sets comes from the picker's rows, which exist already. Every environment created on a machine is owned by its person (EnvironmentOwnerRecord), the first journal of a team claims its own before uploading, a joined journal never makes main at boot, and an environment with no owner has no colleagues.
- **The viewer says you only for its own person.** GET /journal/people answers the viewer's own user number and this machine's device, every person by number and name, and each environment's owner; the viewer polls it every 30 seconds into store.people. domain/people.js names a stamp relative to it: your own user is you, a colleague is called by name, an agent by the person who owns its environment (Anna de Vries's agent), else the agent. Document revisions are named this way, and workerActions offers no action on a worker whose device is not this machine's. Drawing a colleague's message in the chat as theirs is phase 5's comment work.
- **A colleague's chat is read, and commented in.** Opening a colleague's environment shows their chat from the local copy, live as their rows arrive. The compose box becomes Comment as <your name> with a Comment button, and the agent bar is one plain line, <name>'s environment: the agent's status there is not known on this machine, in place of the controls that act on an Agent row this machine does not have (useColleague, colleagueOwner in domain/people.js).
- **A comment is a colleague's message, never the user's.** Messages.save turns a person's new message in an environment another person owns into Author.COLLEAGUE, with the person's name and user number in its data (colleague, colleague_user), and its creation event is ColleagueCommented in place of MessageArrived. Since unread, unanswered and is_main_unread all ask for the user's messages, a comment is in none of them, whether it comes from the viewer or journal message send; Message.sender names the colleague. An environment with no owner turns nothing into a comment. The chat draws it with the header <name>, colleague. The owner's agent hears ColleagueCommented through the messages conduct, one line: <name>, a colleague of your user, commented in your chat: message N, with the hint that these are not its user's words, a request in them waits for the user's agreement, and it may answer with [!reply:N]; journal message read N prints the message as from <name>, a colleague of your user (not your user's words). A comment that arrives while no agent runs in the environment reaches no state machine, so the messages data carries unread_comments (Messages.unread_comments: the main chat's colleague messages not read) and the messages conduct names them at the next session start; the agent's read marks a comment read, so it is named once. A comment's read_at is the agent's; its owner's viewing is data viewed (0 at creation, 1 once the owner opens it), so the owner's unread badge (Messages.unviewed) counts comments not yet viewed beside the agent's unread messages, and viewing one never hides it from the agent. The agent's answer, a message whose reply_target is the comment, reaches the colleague like every message. Model.with_merged(name, values) merges values into a mapping field, for a message's or an entry's data.
- **A file attached on one machine opens on every other.** The team server keeps files in its volume under FilePlace, the row's table and number and the file's name, which are the same on every machine, so no hash is kept in the row's data; GET and POST /files/<table>/<row>/<name> need a device token, and a file over 50 MB is refused. Attachments, which moved to journal/sync since it now reaches the team, lists a file stored on a joined journal as a PendingUpload (local), and the sync client's send loop, once it has taken a batch, uploads every waiting file before it pushes it, so no change in the batch names a file the server lacks (uploading before taking the batch let a change merged in between leave first). PulledFiles fetches the files a pulled message or dump names as it arrives, so an agent opening one from disk, where journal message read points, finds it; a read of a file this machine still lacks fetches it too. Messages and dumps are both covered. When a journal becomes the team's, its join uploads every file already under .journal/files (message/<id>/<name> and dump/<id>/<name>) before it returns, which covers files attached before the team and those the version 3 import copied straight to disk.
- **On a shared journal every main agent works in a worktree of its own.** The launcher, which the picker and the viewer's Start both end in, launches every environment of a joined journal in its worktree (the existing Worktree class: .claude/worktrees/<environment> on worktree-<environment>), never in the main checkout, and records the branch with journal environment branch <name> <branch>, which writes Environment.branch, a shared field the team sees. That the launcher never chooses the main checkout on a shared journal is what keeps it free of agents. In a project that holds repositories of its own, the Worktree class makes a worktree of the outer repository only; the inner ones are not covered yet. When the first journal of a team renames its environments with the person's prefix, each one's worktree moves with it (Worktree.renamed: the folder, its branch and its tips ref). A name a session started before the join still sends, such as main, finds the person's own environment through EnvironmentNames, which the hook receiver, the console and the subagent commands resolve names through: the environment of that name, else the person's own of that name, else one made under the person's name. A resume launched in the worktree copies the session's transcript from the main checkout's project folder into the worktree's (Provider.copy_session; Codex keeps sessions by id, so needs nothing), and if it cannot be found the launch says plainly that it starts a fresh session. Moving agents at a join puts them in the person's own environment of their name.
- **The Team chat is a real environment named team, owned by no one.** Environment 0 cannot hold it (a falsy environment_id is taken for the writer's own, and project rows are read into every environment), so the first journal of a team makes an Environment named team of kind session, carrying the team's key, when it becomes the team's (task 3135 moved the old is_team_chat flag into the kind); EnvironmentOwnerRecord gives it no owner. With no owner it has no colleagues, so everyone's words there are users' words, nobody's write is refused, and the launcher may start an agent in it; who may hold it is the claim of task 1481. The viewer lists it in the sidebar as Team chat and opens it like any environment's chat, where everyone types; a message by another person carries its writer's name in its header (the joining test posts from two people and finds both on both machines). While no agent holds it, its messages wait as any unread message does.
- **The team server keeps named leases, one device at a time.** Leases know no journal concept: a device acquires a name nobody holds, or one whose holder has not renewed it for 90 seconds (LAPSE_SECONDS), renews it by acquiring it again, and releases it; two devices racing for one name are settled inside one store transaction, so exactly one wins. The answer, a Lease, names the holder (the person's name), the device, when it was last renewed and whether it has lapsed. POST /leases/take and /leases/release with {name}, and GET /leases?name=<name>, all behind the device token. The chat claim (task 1481) and the upgrade lock (task 1516) use them.
- **One person claims the Team chat and their machine runs its agent.** The claim is the team-chat lease (TeamChat): journal team claim, or the Claim button in the Team chat's bar, acquires it, marks this machine the holder in team.json (is_chat_holder) and starts the Team chat's agent in the team environment's worktree; the sync client renews the lease about every 30 seconds while this machine holds it. Only the holder's machine may start an agent in the Team chat (TeamChat.start_refusal, which the launcher's rows and the viewer's Start ask beside the owner rule). journal team chat, and the bar the viewer draws in place of the agent bar there, say Held by <name>, or offline since <time> once the lease lapses, when anyone may claim it. TeamRequests.reached turns a team server refusal or a network fault into a refusal a person reads, for the command and the viewer alike.
- **The team is pinned to one journal version.** The team server keeps it beside the repository (team_details): the first copy's journal sets it, journal team upgrade <version> (admins) moves it, /team and every pull answer name it, and a pin wakes held pulls. A joined journal keeps it in team.json as team_version; its status bar says "Your team is on version X: journal update apply installs it" while it runs an older one, and both the updater and the launcher's prompt offer only that version (TeamAccount.allows), so one member's newer release never runs ahead of the team. Release moved to journal/support so the sync side can compare versions.
- **An upgrade migrates under a team lock.** journal update apply on a joined journal (Updater.install_newest, the old code) takes the server's upgrade lease, sends its whole queue and pulls to the head, and sets upgrade true in team.json before it installs; while the lease is held the server refuses every other device's push, which stays in its queue. The new version boots, migrates and seeds (the upgrader alone is the seed writer), and before the sync loops start TeamUpgrade.finish renews the lease and, only when the team's migration is older than its own, uploads its migrated copy with POST /upgrade naming the sequence it pulled to. The server refuses it when its head moved, writes backups/team-before-upgrade-<time>.db first (restore with python -m sync_server restore), replaces its rows, records the migration and raises the lowest sequence a pull may go on from to the new head, so every other device is told copy_needed (1517). Then the lease and the mark go. Open: an install that takes past the lease's 90 seconds lets another device push before the upload, which is then refused; the upgrader keeps its migrated journal and takes the team's copy like the rest.
- **Every other journal takes the migrated copy.** A pull from below the lowest sequence a pull may go on from (checked after a held pull too) answers copy_needed; SyncClient downloads the full copy and JournalCopy.replace clears its shared tables, loads the copy, and lays its own queued writes on top (a deletion deletes, an update updates, a row the copy lacks is created), so a local migration that stamped different values leaves no trace and unsent work still shows. Local-only tables are never touched. Joining uses the same replace with an emptied queue.
- **Waiting writes follow a column rename.** Migration.column_rename, the one place a column is renamed, renames it too in the fields and changed_at of every write of that table still in the outgoing queue, values kept whole, so a person offline through an upgrade sends their writes under the new names. A migration that changes values rather than names leaves queued values as written; such a migration must also rewrite the queue.
- **Syncing requires the team's exact version by default.** Every request names the journal's version (X-Journal-Version); the server refuses a push or pull from a journal on any other version than the pinned one, older or newer, with "this journal runs X and the team Y: install Y with journal update apply", unless the admin ran journal team versions any (journal team versions exact restores it; a team detail, exact by default). The device holding the upgrade lease is let through on its old version, so it can send and pull before it upgrades. Pinning a new version therefore holds every member's sync until they install it, their writes waiting in their queues.
- **A join happens at the team's version.** journal team join reads the team's pinned version and refuses a journal on another one with the install line for that version (curl … install.sh | AGENT_JOURNAL_REF=vX sh), so the copy always loads into the schema it was written in; where the team allows any version, a journal on the team's migration may join. The join does not install the version itself: installing restarts the journal, so it is the person's step before joining again.
- **The server trims its log.** At most once a minute a pull trims the changes table of every change at or below the lowest sequence that every device not revoked and that has pulled at least once has pulled from, always keeping the newest so the head stands, and raises the lowest sequence a pull may go on from to it; a device below it is told copy_needed and takes the full copy. The rows table, deleted rows among them as markers, is never trimmed, so a deletion still wins over a later edit and a new device joins from the full copy as before. A device that logged in and never pulled does not hold the log back.
- **A journal behind the team's migration may not sync.** Every request names the journal's migration (X-Journal-Migration, Schema.version()); the server keeps the team's migration from the first copy (and from an upgrade's copy, 1516) and refuses a push or pull from a journal on an older one with "this journal is on migration N and the team on M: upgrade it to version X with journal update apply"; the line reaches the status bar as the sync's fault and the changes stay queued. The team's pinned version, not the newest migration anyone ran, is what members install, so one person cannot lock the team out. At each session start, while the team is pinned to a newer version, the team feature's conduct tells the agent once that the journal is behind its team.
- **Sync speaks a protocol version.** sync_server/protocol.py holds PROTOCOL; every request carries it in X-Journal-Protocol and every answer carries the server's. A server answers a journal on an older protocol (or none) with 426 and "upgrade the journal with journal update apply"; a journal refuses an answer from a server on an older protocol (or none) with "upgrade the team server's image". Either line reaches the status bar through the sync loops' fault. Raise PROTOCOL whenever a request or answer changes shape.
- **The Team chat changes hands.** journal team release lets the lease go and stops the Team chat's agent on that machine. A holder that stops renewing for the server's 90 seconds (the lease's lapse; no setting of its own) may be claimed over; when it comes back its renewal sees another device holding the lease, drops holds_chat and stops its agent instead of fighting for it. The agent the new holder starts reads the Team chat's last ten messages and answers (user words and agent replies), each cut to 200 characters, named by writer, in its start block; the overview it owes before writing shows the rest. A release stops the agent, then commits every file of the Team chat's worktree and pushes it, then lets the lease go; a claim resets the claimer's worktree to the last push when it is clean. A claim over a lapsed holder puts a card in the Team chat saying what that holder had not pushed stayed on their machine.
- **The Team chat's files are one branch.** The holder's journal commits its worktree of the Team chat (.claude/worktrees/team) once its files have not changed for 15 seconds and pushes it to journal/team-chat on origin; every member's checkout is a clone of the team's repository, so origin is the one remote all of them fetch from, and only the holder pushes. Every other machine's journal looks at that branch every ten seconds and resets its own worktree of the Team chat to the holder's last push when the worktree has no changes of its own; when it has, the worktree stays and a card in the Team chat names the machine. git add -A commits only what git does not ignore, so the journal's folder (excluded), the linked skills and any ignored secret never leave the machine. Repositories inside the project are not part of an environment's worktree and are not shared through it. A push that fails, such as one a new holder's branch is behind for, is shown as the sync's failure.
- **The Team chat's agent hears everyone, named.** In the Team chat any person's message is a user message, since it has no owner, stamped with its writer's name (data teammate, EnvironmentOwners.is_teammate), so journal message read names them: <name>, one of the people you work for in the Team chat. DeliverMessage now hears pulled creations as well as local ones, inside the message's environment's scope, so a message posted on another machine is typed into the agent the holder's machine runs there, and it counts as unread there; the reminders and holds are those of any chat. Messages.save places a message in its environment before it decides whether it is a colleague's comment or a teammate's message, since a message from the viewer gets its environment only when saved; before this a comment made from a colleague's viewer stayed a user message.
- **Workers branch from and merge into the environment's worktree.** On a joined journal WorkerBranch.checkout is the worker's environment's own worktree (.claude/worktrees/<environment>, when it exists) instead of the main checkout: a worker's worktree is cut from that branch, with the main agent's unmerged work, its work merges back into it, a worker with no worktree of its own works there, and main is untouched. Worker branch names, worker/<number>-<name>, never clash across people, since worker numbers come from each machine's blocks (task 1479).
- **Chat marks and docked cards sync; outputs stay.** A command's card is a message whose data carries its title, progress, picked lines and docked state, so it syncs like any message, while CommandOutput rows and output files are local. WatchRefresh now reads again, once a second, the card of every watched output and of every one still running in the background (CommandOutputs.all_carded), and rewrites it only when its view changed, so a card is written at most once a second. The server does not prune a card's older data, since it knows no journal concept; while a push is under way the queue folds a card's waiting updates into one, and the log trimming of task 1487 drops what every device has pulled. In a colleague's environment the viewer draws every command card from its message alone: the live progress poll asks this machine for nothing there (output numbers are per machine), and opening a card or its dock says the output stays on the colleague's machine.
- **People talk beside a chat in a side thread no agent reads (message 17305).** One side thread per environment: messages whose agent_role is AgentRole.PEOPLE, a thread no agent reads. Every agent-facing query reads the main chat (agent_role main), so a side message is never typed to an agent, never unread or unanswered for it, never in the look; it has no MessageArrived, and a colleague's word there stays a person's message rather than a comment. GET and POST /journal/side-thread list and post it in the viewer's environment, and the viewer's Side thread view, which any pane can open, shows it with each writer named relative to the viewer. A thread per project or between two people is left for when it is asked for.
- **A hosted journal signs each person in (phase 9, task 1535).** The mark .journal/hosted, which only the team image writes (Hosting reads it; task 1547 replaced the team.hosted setting, which Settings showed as a switch that could shut a person's own viewer behind a sign-in), turns on LoginGate in the HTTP handler: every request but /sign-in, /sign-out, /hooks/, /cli and /shell/ needs a browser session; a page request without one is sent to /sign-in (303), an API request is answered 401, and the viewer's transport sends the browser to /sign-in on a 401. LoginController shows the form and checks the email and password with the team server's /login (each sign-in is a device on the server, named a browser on the hosted journal), then opens a BrowserSession (local-only: the cookie key's hash, the account number and name) and sets the journal_session cookie, HttpOnly, SameSite=Lax, Secure when X-Forwarded-Proto is https, for 30 days. Identity.build turns the cookie into Actor.user(person), so the people endpoint's me, a launch refusal and every viewer write name whoever signed in (request.actor, never TeamAccount.user_number, for a viewer request). The sign-in routes are unscoped (Router.get_unscoped), since a browser that has not signed in names no environment.
- **A hosted journal starts no agent (task 1536).** StartRule (features/team/support) is the one rule for starting an agent here: never on a hosted journal (team.hosted, an option of its own module, hosted_option.py, so the rule and the login gate import it without a cycle), never in a colleague's environment (EnvironmentOwners.start_refusal), in the Team chat only on its holder's machine (TeamChat.start_refusal). The viewer's launch and the launcher's rows (journal environment json, which the picker and the viewer's Start read) ask refusal; journal team claim and journal worker dispatch ask hosted_refusal.
- **The hosted journal follows the team's pinned version (task 1538).** On a hosted journal the updater installs on its own (as if updates.auto were on), offered only the pinned version as every shared journal is, and its tick checks at once whenever team.json's team_version moves to one it does not run, instead of waiting for the hourly check; it never takes the upgrade lease (install_newest skips prepare_upgrade), so it never uploads a migrated copy and takes the team's copy like any member once a member's upgrade lands. The option team.hosted lives in journal/sync/hosted_option.py, below the team and updates features, which both read it. Open: if the hosted journal installs before any member upgrades, the writes it sends in the new schema reach the upgrader's old journal before it migrates, and a column the old schema lacks is dropped there.
- **The hosted journal leads the team's version when its auto-update is on (task 1557).** The setting updates.check_minutes (default 60) sets how often the updater asks GitHub; the team image's hosted.sh turns updates.auto on and sets the check to one minute at the hosted journal's first start. A hosted journal with updates.auto on and no branch followed is offered every newer release of its major version, not only the pinned one, installs it and pins the team to it before it restarts, and pins the team to its own version at each check while the team is behind it, so a failed pin is tried again. The team server lets its relay account pin the version as an admin may. With updates.auto off it follows the admin's pin as before.
- **One team URL joins (task 1571, 2026-10-23).** Joining takes a team URL, an email (git's user.email filled in) and a password; the name the team sees is git's user.name. A team server with no account takes its first connection by its bare URL as its install (POST /install): that person becomes its admin and the journal the team's, so the setup step and its code are gone, and the server's log says it waits for its admin. Once it has an admin, a person joins by an invitation URL, <address>/join?code=<code>&fingerprint=<sha256>, which journal team invite prints and the Team tab shows to copy; a bare URL is then refused. A first connection to an https IP address with no fingerprint trusts the certificate authority the server serves, since nothing else could be the server's yet. Every new password is checked on the server: 12 characters mixing three of lower case, upper case, digits and symbols, or 20 or more, never holding the email's name; the form's Generate button makes a 22-character one. A join to a team that holds a journal is refused when this journal has tasks or messages of its own (task 1569); --replace-mine takes the team's copy on purpose.
- **The team-server image runs the hosted journal (task 1537).** The image carries the journal's source (journal, supervisor, sync_server, journal.py, journal.sh, web/dist and install.sh) beside the sync server. run.sh starts the sync server and Caddy, and keeps docker/team-server/hosted.sh running in a loop: it installs the journal into /data/journal from the image's copy, waits (python -m sync_server hosted) until the team holds a journal, so the hosted journal never uploads one, installs the team's pinned version when it differs from the image's, turns team.hosted on and joins with an invitation for the service account hosted-journal@team.server (its password made by the server and kept in /data/team/hosted.json), then serves on 127.0.0.1:8421. A hosted journal skips the join's repository check, since it has no checkout. routes.caddy, imported by all three Caddyfiles, sends the sync server's paths to it, /hooks, /cli and /shell to no one (404), and every other path to the hosted journal.
- **The hosted journal relays everyone's writes (task 1533).** The team server refuses a change that names a person other than the device's own account, so the hosted journal's service account has the role relay (made by python -m sync_server hosted before it invites it; accept then logs the existing account in), and PushHandler.may_send lets a relay alone send writes stamped with whoever signed in to it. The log's writer of each field is the relay's account, so a conflict card names the Hosted journal, while the row's creator and updater name the person. The viewer shows Sign out in the status bar when /journal/people says hosted. The image test signs in at the hosted address, finds a member's task, and finds a message posted there on the team server within 3 seconds, stamped as the person who signed in.
- **The viewer connects a journal to a team (task 1543).** Settings has a Team tab. In a journal in no team it shows the join form (address, code, name, password; the fingerprint only for a bare address), which posts to /journal/team/join, the same TeamJoin as journal team join, and shows its outcome or refusal as a line. In a joined journal it shows the team server, the sync line and the team's version, and the admin's invitation (/journal/team/invite), answered with the join line, which TeamAccount.join_line builds for the command and the page alike.
- **The Team page, as designed (task 1545).** Designed in Claude Design and built without a second pass: Sync (the status dot and line, the update command to copy when the team is on another version, the team server, the team's version, this journal's and the changes waiting), Team chat (holder line with Claim or Release, Open), People (each person with their role, presence and environments, a colleague's opening from here, own environments marked In the sidebar), and for admins Invite a person and Devices with a confirmed Revoke. The server gained what it needed: every device keeps when it last pulled (migration 8, pulled_at), any team device may GET /people (each person's role and latest pull), and a login answers the account's role, which the join keeps in team.json. Presence is a pull in the last two minutes. A colleague's environment shows no agent state, since agents are local and this machine cannot know it. Before its first contact the sync line says Connecting to the team server, and after a join the viewer moves to the environment's new prefixed name.
- **Backups, restores and upgrades of a team server.** docker exec agent-journal-<project> python -m sync_server backup --data /data/team copies the live database with SQLite's online backup into /data/team/backups/team-<time>.db (or --to) and prints the path; restore --from <file> puts a copy in place of the database and is run in a one-off container on a volume no server runs on. An upgrade is docker pull and a restart: the server runs its own migrations at boot. Several projects on one host are several containers and volumes, but only one can have ports 80 and 443, which a public certificate needs; any further one takes ports of its own (TEAM_HTTPS_PORT and TEAM_HTTP_PORT in host/install.sh) with the server's own certificate, or TEAM_PLAIN_HTTP=1 behind a proxy the person runs. tests/team_image_run.py backs up a running server, restores it into a new volume and container, and finds the same rows.
- **Every write in an environment is made by its host (task 2585, messages 39904, 39918, 40419).** Hosts (journal/sync/hosts.py) is the one rule: a journal in no team hosts every environment; in a team every journal makes its own writes in the Team chat, since its agent already hears pulled messages and a chat nobody holds must still let people talk, and any other environment's host is the machine of the person who owns it (the owner link), and one nobody owns the hosted journal. A message posted from the viewer of a journal that is not the host is not made there: the controller asks the host through the team server (POST /host-requests, kind message, the message's text, reply target and idempotency key, answered 202), the hosted journal naming the person signed in to it and anyone else only themselves. The server keeps the request (migration host_requests) and hands it to the host with the host's next pull, which names the keys of the environments it hosts; a new request wakes a held pull. The host's HostDesk makes the message as the person who asked (Messages.posted, which finds one already made by its idempotency key), so MessageArrived and everything after it are dispatched and handled on the host, where the agent runs, then says it is made (POST /host-requests/done); the row reaches every other journal, the asking page's outbox among them, by sync. A host that has made a write a person asked of it may send that person's writes from then on, since it sends the message in the asker's name. Every push carries a pull: the push names the sequence the journal holds and the keys it hosts, and its answer (SyncAnswer) brings the team's changes and the waiting requests with it, so a busy journal needs no second request; the send and receive loops apply one answer at a time and only changes past the sequence held. These shapes raised the protocol to 2. An ask the team server cannot take answers 500, a fault, so the page's outbox keeps the message and sends it again under the same key (task 2600); once asked, the outbox does not ask again, and a message with files waits for the host's message to come back, found by its key at GET /journal/messages/sent/<key>, then uploads its files to it, which reach the host like any attachment. Open: a person with two machines hosts their environments on both, the idempotency key keeping a message single; other writes than the user's messages still go where they are made.
- **The team image is published with each release.** The Docker image workflow has a second job, team-image, which builds docker/team-server/Dockerfile for amd64 and arm64, pushes ghcr.io/jessegall/agent-journal-team tagged with the release (v4.x.y) and latest, signs it with cosign like the server image, and attaches to the release a copy of host/install.sh whose TEAM_VERSION default is that tag, so curl .../releases/latest/download/install.sh | sh pulls the matching server. Both jobs check the tag against src/journal/version.py, the version's one place: the root VERSION file, which still said 4.1.0, made every release since 4.1.0 fail that check, so the journal-on-a-server image has not been published since; the file is gone, and docker/Dockerfile no longer copies it. That fix reaches main with this plan's pull request, which restarts the server image's publishing too.

## The worker pool, as built (plan 1025, 2026-10-23)

- A machine gives the team's pool `workers.pool_slots` worker slots (its own setting, 0 by default); `workers.pool_profiles` (the team's) names the profiles a pool worker may use. Every pull names the slots, the free ones and the version; a push names them only when slots are offered, since an older team server refuses fields it does not know.
- `journal worker dispatch --pool` pushes the environment's head to origin as `journal/pool/<id>-<name>-base` and asks the pool. Refused without a joined team, without `--worktree`, with `--model` (the machine that runs it uses its profile's model), for a profile outside `workers.pool_profiles`, with `--needs-secrets` (the job uses this machine's secrets), and in a project that holds repositories of its own, which origin does not carry.
- The team server offers a pool request to every machine with a free slot on the version it names; the first claim wins, a decline offers it to the others, and one nobody claims in ten minutes goes back to its environment's host as `pool_unclaimed`.
- The machine that takes it keeps a pool job row (machine-local), claims it, fetches the base, declines when the libraries it links were installed from lockfiles that differ from the base's (`node_modules` against `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`; `.venv` against `uv.lock`, `poetry.lock`, `Pipfile.lock`, `requirements.txt`; `vendor` against `composer.lock`), cuts the worktree from the base, and runs the worker with a short list of variables (no cloud or API keys); its own preparation and completion commands run inside the pool worktree. At clock-out the branch goes to origin as `journal/pool/<id>-<name>`.
- Every write is made by its host: on a machine that does not host the worker's environment, clock-in, clock-out with the report and the run's end are host requests (`worker_ready`, `worker_delivered`, `worker_ended`) the host makes, so the dispatcher's agent hears them. Proofs are written where the worker runs and sync, so its own clock-out check sees them at once.
- Pool workers do not count against `workers.most_out`: that limit guards the load of the machine that runs them, and a pool worker runs on another.

## The state machine answers; the delivery types (task 1542, 2026-10-23)

Sir Jesse, message 18488: the state machine decided and delivered at once. Now StateMachine only holds and moves each agent's stack and answers an event with a MachineReply: the agent as it stands, the decision, the lines to type, the remarks to queue and the moves the states entering and leaving the stack asked of the terminal (the Typist only records them). Delivery (engine/delivery.py) is the engine's one way to the supervisor for those replies: it makes the moves, types the lines and remarks, marks the agent working, resting or with a refused stop, handles the silence between hooks, and folds the queued lines into a hook's answer. HookAnswer is the blocking listener on every agent event (machine, then delivery); RowEventDelivery, journal panic and the boot's ending of compactions deliver the replies they get. StateMachine imports nothing of supervisor_link, and a Stack replacing another tells its leaving and arriving states, so the machine never walks a stack's states itself.
- **No two running environments work on one branch (task 1531, 2026-10-23).** An environment works on its own worktree's branch, or on the main checkout's branch when it has no worktree of its own. While its agent runs it holds that branch: StartRule refuses to start another environment on the same branch, naming the one running there and suggesting a worktree of its own, and the git conduct refuses a git checkout or git switch onto a branch another running environment works on (BranchHolders, read through the BranchEnvironments part only when a command switches branches). Environments that are not running hold nothing, so several environments may share the main checkout as long as one runs at a time.
- **The agent bar reaches the team as agent views (task 2637).** Each journal in a team sends POST /agent-views every time what its agent bar shows for an environment it hosts changes (checked every 2 s, sent again every 30 s), the rows AgentActivity builds for /api/agents; the Team chat is left out. The team server keeps the latest per environment key in memory only and hands it out for a minute, so a host gone offline shows no agent. A journal that does not host an environment (the hosted journal, or a colleague's) answers /api/agents from GET /agent-views, read at most once a second, each row marked remote, and reads the agent's edits by its session from the synced edit rows. The owner's model, effort, pause and resume there go to the host as the host requests agent_control, agent_pause and agent_resume (AgentBarWrites), which the host makes only for the environment's owner, through the same code as at home; anyone else is refused on both sides. A colleague sees the bar read only, with no pause button. Each agent row carries its newest 50 terminal lines, which the remote side strips from the bar and serves to the Terminal pane alone, and a line typed there goes to the host as agent_shell, checked against the owner like the rest (task 2667).
- **journal remote install user@host installs the team server on a machine over SSH (task 2602).** The one server form is the team server with its hosted journal, so there is no separate --team: the command runs `ssh -t user@host "curl -fsSL <this release's install.sh> | TEAM_VERSION=<this version> sh"`, so the installer's questions (project, admin, password, address) are asked in the user's terminal and it prints the address and the join line itself; --version picks another release. It runs in the shim's local path beside claude and setup, never in the server, and refuses a shell without a terminal, as an agent's is. tests/remote_install_run.py drives it against a fake ssh on the PATH.
- **A new environment can carry on from a kept conversation (task 1406, merged into development on 2026-10-23 for Sir Jesse to test).** No environment is made by itself: the boot, the viewer's summary and the launcher's list no longer fall back on main, and the viewer opens New environment while the journal has none. Each provider lists the project's kept sessions (session_files, past_sessions: newest first, the first prompt read from the file's head, its line count). POST /api/environments with provider and session fills a new environment's chat through SessionHydration: TranscriptChat turns the transcript's prompts and replies into messages at their own times, the user's marked read so none reaches the agent as new, folds the tool calls between two of them into one line counting them by tool, and leaves thinking, injected lines and summaries out; the session becomes the environment's ended agent, so the launcher resumes it on the first launch, and a hydration mark closes the chat. The hydration feature tells the first session there, once, to read the chat and record what is still true or open; the mark then records the request. An existing environment is never filled. Tests build their own journals through tests/main_journal.py, which makes main as a user would.

## Chat marks are written only by listeners (ruling of 2026-10-24, messages 46145 and 46148)

A call to MomentCards or ProcessCards outside features/*/listeners is a sin, judged by MarkWrittenOutsideListenerDetector; a Message built with author system outside the models and the two card writers, by SystemMessageOutsideListenerDetector. A process card class builds a ProcessMark and a listener hands it to ProcessCards. A moment no row's save and no hook carries is dispatched by the Announcer as an event under events/moments and heard by the feature's listener. The key lock of ProcessCards is the write transaction.

- **The developer numbers live in memory (task 2994).** The timings, the rolling log of the newest thousand, the slowest times and the read counts are kept by DeveloperTally in the server's memory and written to no row; they start empty at each boot and reset clears them. Migration 43 drops the timings table and the developer.* statistics rows. The Statistic table stays for the profiles' use counts.

## Every route and hook is timed before a commit (task 2992, message 50484)

- **tests/route_times_run.py**, outside the default run, is run alone by .githooks/pre-commit under a 300-second limit. It generates its cases from the router: every registered route, each list with its list parameters (limit, closed, before, after, since, ids), each write with an empty body, ones that take a row away last, and every HookType posted to /hooks/claude. Each is timed in-process against the saved full project, and one over the budget the server judges it by (SlowRequests.budget: the faults read, write and hook budgets) fails the run. A route that leaves the process (team server, tunnel, supervisor, a program, the network, a stream) is left out by name with why in LEFT_OUT, beside what the server itself never judges (outward routes, the developer and sync doors); one left out that is no longer registered fails. When the machine is busier than its cores, as SlowRequests.is_busy says and the server itself then judges nothing, a reading over budget is skipped with the readings named, since a load only lengthens a time.
- **The full project is generated, never copied (tests/full_project.py).** A fixed seed and a list of plain words make about 5,000 messages, 15,000 entries, 1,700 links, 40 workers, 30 plans with phases, 730 tasks, docs, reports, checks and memory, packed as tests/fixtures/full_project.db.gz (2 MB), the same file every run. Built again when the schema moves too far for it to boot: PYTHONPATH=src python3 -m tests.full_project.
- **Every answer spends at most 30 points on the full project (tests/route_points_run.py, task 3022).** A row loaded, a write and a started kilobyte loaded are a point each, counted on the thread that began the count alone, so deferred work that carries the request's context never counts against it. A write by save or touch leaves the row's read by its id, and any other read its repository finds it by that the cache held with it alone (an agent's session read), answered with the row as a load would return it once the transaction commits, unless another write moves the table first or a secret was masked out of it; so one answer reads its agent's row once. The agent lists a session start reads (running peers, recent peers, ended agents with sequence runs) filter in SQL. A plan's phases are read without their links, in the order they were added, and its outline's phase in hand and checkpoint come from its tasks' state counts (PhaseStates), never their rows; its tree reads each task once.
- **What a live journal reads cold is measured cold (task 3253, check 1171).** The lists the viewer reads whole when a page opens (documents, reports, notices, reactions) and the commands run as a session starts (environment overview, check list) are counted against a cold cache, and the hooks are answered as the agent orchestrates, the mode whose listeners read the most. A list of documents, reports, notices or reactions is a page of ten, with up to ten open rows before it (Listing.capped, Controller.page_rows), a document or report listed without its body, a report without its items (Query.without), read whole by its number. The status bar reads the session's last sixteen tool and part entries, their payload keys left out (Query.without_keys, PAYLOAD_KEYS). The orchestrator's load keeps the refs of its oldest eight waiting items and a count of the rest, so its agent row stays small. A stop names the three oldest reports and documents of each kind never acted on, filtered in SQL, and reads the merges since the suite last passed only once a whole run failed since. The saved full project holds sixty notices, five open, and a whole passing run of the suite as every third command output.
- **Open after task 3253.** On the full project the environment overview spends about 1700 points: it lists every open task, unread message, rule, fact and reminder, and admits every memory row as read; it needs a cap per section with a count, which is a decision on what the overview says. The session start and a displayed message spend about 150 points reading every rule, fact and reminder to name them. After a compaction the session start answers its start block twice: Compacting pops and hands the event down, and the lines of both answers are delivered and recorded (StateMachine.reply), 24 nudge writes in the live journal.

## A dismissed reader report is judged by a verifier the journal sends (task 3005, messages 50997 to 51051)

- **The journal sends the verifier, never the agent.** ReaderReport.dismissed carries ReaderReportDismissed; the verification feature's VerifierStart hears it and VerifierDispatch makes a Worker named "Diogenes, lamp-bearer of the honest reason", with no dispatcher, so the agent waits on nothing, linked to the report as verifies, which link alone makes it a verifier (no column on workers, so no route reads a byte more), on the journal-medior profile's model without its instructions, and starts it. Its brief is DismissalEvidence alone: the report, the agent's reason, the reader as written and the run's last 400 output lines.
- **The state machine holds it.** A verifier's agent row is made in the role verifier (AgentRole.VERIFIER) when its worker has the verifies link (WorkerHooks.bind, VerifierDispatch.role); the verifier role has its own conduct set (Feature.verifier_conduct), and VerifierConduct pushes Verifying at its session start. Verifying is conduct-free and is never left: every tool but `journal verdict` is refused, file edits among them, and the verdict's ReaderReportJudged pushes Ended. AgentRole.is_sent names a worker or a verifier wherever the engine took a worker's headless path.
- **The verdict.** `journal verdict yes|no "<reason>"`, a verifier's alone: yes keeps the dismissal; no reopens the report (dismissal cleared, is_refuted) and the shell demand REPORT_REFUTED, span zero, holds the agent's next write at once with the verdict until the reader's file is newer than the verdict; a refuted report is never dismissed again. VerifierEnd retires the verifier's worker and stops its process.
- **CommandPart.journal_noun is a property**, as its two readers took it; as a method it never matched, so a skill's command debts and the pins check on `journal message` silently never fired before.

## In orchestrator mode a reviewer the journal sends checks each worker's work (task 3186, messages 54456, 54481 and 54531)

- **The Reviewer switch, reviewing.reviewer, replaces Auto on the plan bar in orchestrator mode.** With it on (ReviewRouting: orchestrator mode and the switch), WorkerReports.delivered files a clock-out with Worker.review_requested, which carries WorkerReviewRequested instead of WorkerDelivered, so the orchestrator hears no clock-out and the work is not ready to check (Workers.checkable_workers) while review_pending.
- **The reviewer is a Reviewer row in sent_agents, actor reviewer:N, resting on Reviewing**, which refuses file edits and a stop before `journal review "<one line per point>"`; it never merges, since merge is not among its verbs. ReviewerDispatch reuses the idle one in its own session, as VerifierDispatch does; both run on HelperRunner, and the process always runs in the project folder so a resumed session is found, its brief naming the worker's folder for the tests.
- **The orchestrator decides.** The report reaches it as reviewing.work_reviewed and resolves a wait on the worker; it sends the work back or merges it. A reviewer that ends without a report, or runs past its 20 minutes, hands the work back in ReviewerRunner.ended (Worker.review_failed, reviewing.review_failed), before the reviewer is marked ended.
- **The reviewer pane on Home (task 3187, messages 54627 and 54649)** is the view reviewer, usable only while the reviewer is on in orchestrator mode. It opens beside the chat's pane, never in place of it, stays shut once you close it until the switch is turned on again, and goes when the switch is off; it moves and closes like any other view. It is not a chat: it lists the reviewer's steps from its own chat (GET /journal/reviewers, then each one's /chats/{session}), oldest first. The steps are moment cards of kind review_step in the reviewer's role (MomentCards.show_role_card, since a reviewer's session has no agent row before its first hook), written by listeners: ReviewerStart (review started), ReviewerTestPassed and ReviewerTestFailed (each test run, by ActivityLabel.test_runs), and ReviewReportSteps (each point of the report, parsed by ReviewReport, and the report).
- **Reviews queue for the reviewers the orchestrator adds (task 3203, messages 55168 and 55189).** A clock-out with the reviewer on sets the worker's review_queued_at; Workers.queued_reviews reads the queue in that order, in SQL. ReviewQueue.assigned, the one place reviews are handed out, gives each idle reviewer the next one, and adds a first reviewer when the queue has work and there is none at all. It runs at each clock-out (ReviewerStart), when a reviewer reports (ReviewerRetirement) or ends (ReviewerLoss, on ReviewerEnded), and on journal reviewer add. journal reviewer retire lets an idle one go (state retired), and journal reviewer list names the reviewers and the queue. At a stop and on the tick the orchestrator is told reviews waiting for a reviewer: N; reviewers: M, from the reviewing data part, read only when asked. With the reviewer off there is no queue: a clock-out waits for the orchestrator as before.
- **A reviewer signs off and the worker goes on (task 3204, messages 55223 and 55457).** A reviewer runs on workers.reviewer_model, the fast model haiku by default, set on each review. Its brief holds the task's brief as given, each proof, and the output of the test runs the worker made, its own command outputs whose label is testing. When it made none, the reviewer runs the tests the proofs name. It reads the diff only where a proof is unclear. ReviewReport reads each point as passed, short or undecided. Every point passed signs the work off (ReviewSignOff checks each point and merges through WorkerActions.merge, which sends the worker on to its queued task); a point short is checked short with the reviewer's reason (WorkerActions.short_checks marks several at once, the last save sending the worker back with all the reasons); a report with no point short that leaves one undecided or unnamed raises WorkerReviewUndecided, the one review line the orchestrator gets. WorkerReviewed is no longer a resolution, so a decided review neither ends a wait nor speaks. A merge no longer tells the orchestrator a place is free: only WorkerQueueEmpty, raised when a merged worker has no queued task, says so, once (the place-free line when tasks are open, else worker_has_no_work_left). Open: picking the worker's test runs by their label is done in Python, since outputs store no label.
- **Each mode button's hover panel holds the mode's settings (task 3196, messages 54981, 56049 and 56068).** The panel is the plan bar's own tooltip, no new menu: its words may carry toggles, which TipBubble shows as switches below the one-line description, and it stays open while the pointer is on it. The Orchestrator's are declared once in web/src/domain/modes.js: may write plans (workers.orchestrator_writes_plans, on), approves plans (workers.orchestrator_approves_plans), whose choice shows indented under it only while it is on (workers.orchestrator_plan_approval: only its own plans, plans the user made, all plans, the default; task 3262 replaced the switch approves only plans it did not write, which migration 55 carries over as plans the user made), may release (workers.orchestrator_releases, off) and the Reviewer (reviewing.reviewer); the approval switch and the Reviewer switch are gone from the plan bar, which in orchestrator mode shows no switch beside the mode buttons. Each toggle has a line under it saying what it does, and the panel holds no fitness: the score and the measures off the ideal live in the status bar's fitness dropdown with the timeline (task 3262). Each is set by the user alone. plan create refuses the orchestrator with may write plans off; plan approve reads the plan's author by kind, so a plan the main agent wrote is its own across sessions. Decided: may release means cutting a version release, since releases wait for the user's word; with it off, the workers conduct refuses the orchestrator's git tag <name> and gh release create lines (ReleaseLines).
- **The workers panel shows the test turns (task 3201).** With How workers test set to Test budget, WorkerList shows Test turns: the budget's numbers from the workers settings, then each turn running, then each waiting, oldest first, with its worker's name, its test ids and how long it has run (TestTurn.started_at, set when it starts) or waited (since it was made). GET /journal/test_turns lists only turns not ended. Decided: the panel's How workers test control still offers its two choices, as its test pins; the budget is turned on from the Settings page.
- **Fitness follows the switch:** with it on, the orchestrator is scored on WorkersProfiles.REVIEWED_ORCHESTRATOR, without merge preparation, and a worker's answer time runs from the review.
- **Open: subagent reports are not routed to the reviewer**; Claude Code returns them to the orchestrator as the Agent tool's result, and a subagent changes nothing to test.
- **Open: the backend still reads tasks.auto in orchestrator mode**; with Auto off before the switch to orchestrator, the agent still stops between tasks, and the switch to turn it back on is hidden there. Pool workers are not reviewed, their work being on another machine.

## A command run with no server writes for the team as the server does (task 3057)

- **TeamWrites is the one place that hooks the team's numbering and queue onto the bus.** BlockNumbers and RecordOutgoingChange were heard only in the server's boot, so a command the shim ran in-process (no server up: a first `journal claude`, a join from a terminal while the journal is down) numbered its rows with SQLite and queued none. That is how the user's main came to be environment 3 under the key 79ceeebf on a joined journal: the join's downloaded path made it anew after the team's copy, numbered 3 by SQLite and never queued, while the messages the server wrote in it later went out. Runtime.boot and App.console_without_server, which journal.py runs, both call TeamWrites.listen.
- **Open: a journal already holding such a row heals by leaving and joining again** (`journal team leave`, then `journal team join --replace-mine '<invitation>'`); no repair re-sends it, since its number may already be one the team handed to another machine.

## An environment shared with the whole team (task 3056)

- **A column, not a link.** A shared environment is a local one carrying the team's key in `environments.team_key` (task 3135 replaced is_shared_with_team), which syncs as any field does. `Environment.shared_with_team(team_key)` refuses a session or the hub, which are everyone's already. Migration 52 moved the flags into kind and team_key, the key read from the account file, or unknown when the account has not learnt it yet; SyncDesk.keyed names it once the server does. It also puts every document and revision from before documents had an environment (task 3168) in environment 0. EnvironmentSharing (features/team/support) is the one way to share or take back, from `journal environment share|unshare <name>` and POST /api/environments/{id}/share|unshare alike: only on a joined journal and only by the owner.
- **What sharing changes.** The sidebar (sidebarEnvironments, environmentLabel in domain/people.js) lists a colleague's shared environment with their name after it, without a start button, since an agent still starts only on its owner's machine. In its chat a colleague writes as in the Team chat (EnvironmentOwners.is_teammate), so the message reaches the owner's agent; unshared, a colleague only comments (is_commenter). Tasks and every other row stay the owner's to write.
- **The button** is Share with the team / Stop sharing on Settings › Environments, shown on a joined journal for your own environments.

## A launch whose server a newer launch stopped is told so (task 3103)

- **The guard keeps what it stopped.** InstanceGuard.replaced_version is the version of a journal on other code it stopped, "" otherwise. Runtime.started announces ServerReplaced once serving, and the updates feature's CarriedLaunchNotice tells each environment whose launch still runs (SupervisorLink.running): a mark in its chat, shown under the new chat kind updates, and the moment LaunchCarriedOver on its agent's row, which UpdatesConduct answers with the remark LAUNCH_CARRIED_OVER, so the line waits for the agent's next hook rather than being typed.

## A hub plan or task bound to a local environment (plan 1029 phase 5, task 3123)

- **A binding is a link the environment reads.** A link of kind bound_to (`repositories/scope.py` BOUND_LINK) from a hub task or plan to a local environment makes that row the environment's work with no local row: Scope.bound answers the rows bound to the environment in scope, and ScopedRepository's reads take, beside the environment's own rows, the rows bound to it and the rows a member link (a repository's member_links: a task's in_plan, a phase's phase_of) puts in a bound row, so a bound plan brings its tasks and phases. With nothing bound, a read is as before. The binding is read unlisted, so a list being paged never trips the relation guard, and Query.filter_alternatives now keeps its alternatives' subquery tables, so a cached read with a member subquery is cleared when links change. Scope takes Links as it takes Environments; no base Repository reads bindings, which would be a cycle through Links.
- **Its events are heard in the environment too.** A scoped repository places a row event with the environments its row is bound to, directly or through its plan (RowEvent.bound_environment_ids, read by Scope.binders), and the state machine's audience is the agents of the row's environment and of those. The row keeps its hub environment, so its change is sent to the team server as any hub row and reaches the other journals with their next pull; the binding link places in no team, since its ends are in different teams, so it never leaves the machine.
- **Open.** A pulled change to a bound row is applied as SyncedUpdate and reaches no agent, as for any pulled update. There is no command to bind yet.

## Driving a hub plan or task, one environment at a time (task 3124)

- **A lease per row.** `journal task drive <n>` and `journal plan drive <n>` take the team server's lease drive:tasks:<n> or drive:plans:<n> through POST /leases/take-free, which is refused while another device holds it, lapsed or not, and bind the row to the environment the command runs in (PlanBindings, features/plans/support, writing the bound_to link). A lease now carries its own lapse (leases.lapse_seconds, server migration 17, 90 seconds unless the request names one); a drive's is 15 minutes, and HubDrives (journal/sync) renews every lease this machine drives each minute from SyncDesk.refresh. Every lease answer names the person and the device holding it (Lease.device_name), and so does every refusal.
- **Takeover only with the flag.** `--take-over` takes the lease through the plain POST /leases/take, which has a lapsed lease as it always did, so a takeover works only once the holder has not renewed for 15 minutes; a drive without it is refused even then. The machine that lost a lease lets its binding go at its next renewal, when the server refuses it. A release lets the lease, the binding and the driver go; `journal task|plan release <n>`.
- **One environment per machine.** The server cannot tell two environments of one device apart, so PlanBindings refuses a second environment on the same machine before the lease is asked, naming who drives it and from which environment.
- **The hub row names its driver.** Task and Plan carry driver (the person) and driver_agent (the agent of <environment> on <device>), written on the hub row, so they sync to every journal; the hub board's cards and the hub home's plans show Driven by. The hosted journal refuses a drive, since it runs no agent; the viewer has no Drive button at all, so drive is a command.
- **Open.** A journal on a version from before device_name reads a lease answer from a newer server and fails on the unknown field. A lapsed driver's name stays on the row until the row is taken over or released.

## A driving agent names the hub row with its team (task 3125)

- **The working state carries the noun.** Working keeps task_noun, task unless it was pushed for a hub task, then acme task, from the tasks data's task_nouns (RowLabels.hub_nouns, the one place a hub row's noun is made; RowLabels.name and noun build on it). Every line the agent gets while working (carry on, log requests, the reminders, the compaction summary) names it as acme task 57, and the plan states keep it as they swap.
- **The card reaches the driving environment.** A task's move card names it with RowLabels and is written in every environment its event is heard in: its own, the hub, and each environment it is bound to.
- **Open.** Other task nudges (task opened, paused, next) still say task {n}; a worker's Working, pushed at clock-in, names its task plainly.

## A pulled change to a driven hub row reaches its driver (task 3149)

- **The model names what a pulled change means.** Model.pulled_events(previous) answers nothing; Task answers, by the state the pulled row reached, the events the same change made here would carry, by replaying it on the row as it stood (PULLED_MOVES: started, delegated, finished, cancelled, paused, blocked), so each event is built in its one place. Repository.pulled_update reads the row before it writes it, and SyncedUpdate carries it as previous. Pulled changes are written through SharedTables' plain TableRows, never the scoped repositories, so the tasks feature's PulledTaskMoves listener hears SyncedUpdate and hands a task and its previous row to Tasks.pulled_dispatched.
- **Heard where the row is driven, and nowhere else.** A scoped repository dispatches those events once into each environment the row is bound to, directly or through its plan (Scope.binders), as that environment's own (RowEvent.with_environment), never into the hub: the writing journal's listeners already wrote the hub's cards, so this journal's answer, the card among it, stays in the local environment. A row nobody here drives fires nothing, as before.
- **Open.** A pulled plan fires no event, and a task moved back to open (unblocked or released) neither.

## A drive ends cleanly when its row or its lease is lost (task 3150)

- **Three endings, one way out.** A drive ends here when its hub row is deleted on another journal (DrivenRowDeletions, on SyncedDeletion, before the incoming change removes the row's links), closed there (DrivenRowClosures, on SyncedUpdate, heard after the tasks feature has passed the closure to the driving environment, since Tasks comes before Plans), or its lease is found taken over at a renewal (HubDrives.renewed, naming the new holder and device from the lease). Each calls PlanBindings.end, which replaces the bound_to link with a drive_ended link saved with DriveEnded, so the event goes out through the links repository, placed in the environment that drove the row.
- **One line to the agent.** PlansConduct answers DriveEnded with PlansNudges.DRIVE_ENDED: what the row is, why (Bob took it over on desktop; Bob marked it done on another journal), and that its writes here are refused. A pulled change's doer is named by EnvironmentOwners.person_name, or someone when it was not a person.
- **Writes refused.** EndedDriveWriteGuard, blocking, refuses this machine's save or deletion of a row with a drive_ended link; a drive binds the row again and removes that link first, so driving it again lifts the refusal.
- **Open.** The lease of a row closed elsewhere is not released, so it lapses on its own after 15 minutes.

## Driving offline (task 3151)

- **Refused before anything is written.** A drive asks the team server for the row's lease before it binds the row or names its driver, and a release asks before it unbinds, both through TeamRequests.reached, so with the server away each is refused with "the team server could not be reached: ..." and the links stay as they were. An edit of a hub row made offline is queued like any other and sent once the server answers again; nothing in the drive code holds it.

## A driven hub task is the environment's task in hand (task 3152)

- **What it changes.** A main agent's write never needed a task (the user's ruling, test_a_write_needs_no_task), so driving changes nothing there. What needs a task in hand is the log line: `journal task log <n>` from the main agent is refused for a task that is not started, unless the environment in scope drives it (Tasks.is_driven, from Scope.bound), so a driving agent logs on the hub row with no local task, and after the release the refusal holds again. A log line and a proof take their task's environment, so both land on the hub row; a worker proves on the hub task it holds as on any other.

## A new row says where it lands (task 3159)

- **Hub or local.** A task added to a plan takes its plan's environment (plan add did already), so one added to a driven hub plan is a hub row; a log line and a proof take their task's; a report about a hub task or plan now lands in that hub (RowDestination.hub_environment_id, src/journal/support/row_destination.py). Every other row made while driving, a document among them, is placed in the environment in scope as always, so it stays on this machine.
- **The answer says so.** While the environment in scope drives a hub row, the answers of task create, plan add, doc create and report create end with ", on the acme hub" or ", kept in main on this machine" (RowDestination.phrase); with nothing driven they are as they were, so the frozen command outputs hold. plan add names its rows with RowLabels, acme task 58 added to acme plan 12. The viewer's New dialog says "Lands on the acme hub" or "Stays in main, on this machine" for the open environment (domain/hub.js destination), and nothing in a journal with no hub; src/web/dist is not rebuilt.

## A session is held by one machine at a time (plan 1029 phase 7, task 3129)

- **SessionLeases (journal/sync).** `journal session start <name>` (the team feature's SessionCommand) takes the team server's lease session:<name> first, so a start is refused while another machine holds it and, with the server unreachable, refused with "the team server could not be reached" before anything is written; then it makes the session on the team's hub, Environment.session with the team's key and its own branch journal/session-<name>, or finds the one the team has, and records the name in this machine's team.json (sessions). The lease takes the server's own lapse and is renewed with the sync every 30 seconds; one another machine has taken since is let go at its renewal. The Team chat is not started this way: journal team claim holds it.
- **The host is the holder.** Hosts counts the sessions this machine holds as its own, beside the hubs and the Team chat, which every journal still writes in; a session another machine holds is asked of its host as any other environment is.
- **The Team chat is the session with no branch.** Environments.team_chats is the sessions with no branch, and the SingleTeamChat seed and the join's team_chat_ready read only those, so a session of its own, which has a branch, is never dropped as a duplicate Team chat or renamed to it. Environments.session_rows finds sessions of their own by name.
- **Open.** The branch is named on the row; making it, its worktree and pushing it are not done here. No release or stop of a session yet.

## A member's message in a session reaches its agent (task 3130)

- **As in the Team chat.** A person's message in any session is a teammate's (EnvironmentOwners.is_teammate already covers every session), stamped with the writer's name, and DeliverMessage hears it pulled as it hears a local one, in the session's environment on the machine that runs its agent. The line typed to that agent now names the writer, "new message 57 from Bob" (MessagesNudges.TEAMMATE_MESSAGE, chosen by MessagesNudges.arrival), and `journal message read` names him as before.
- **The agent runs on the holder.** StartRule asks SessionLeases.start_refusal: a session's agent starts only on the machine holding its lease. TeamChat.start_refusal now asks Environment.is_team_chat, the session with no branch of its own, so the Team chat claim governs the Team chat alone.

## A session drives a hub plan (task 3131)

- **As a local environment does.** HubDrives drives from an environment of this machine's own or a session it holds (SessionLeases.is_hosted_session), never the hub or the Team chat; the session is bound like any environment, its reads take the hub plan and its tasks, and every change is made on the hub rows, nothing in the session.
- **A binding never leaves the machine.** A link from a hub row to a session has both its ends in one team, so it would have been sent; TeamPlacement now places bound_to and drive_ended links (MACHINE_LINKS) in no team by their kind, whatever their ends.

## A session whose holder is offline (task 3155)

- **The message waits.** A message posted in a session this journal does not host is asked of its host through the team server, as any environment's is, and the server keeps it until a machine hosting the session pulls; since the host is the lease's holder, the next machine to hold the session makes it, as the person who wrote it, and its agent hears it named.
- **The writer is told.** The 202 answer to that post carries a notice, Hosts.waiting_notice from SessionLeases: "session review is held by Ada, offline since 10:42: your message waits on the team server and reaches the session's agent once a machine holds it; journal session start review claims it", or held by no one; nothing while the holder renews. The viewer's outbox hands it to the thread, which shows it above the composer.
- **The claim.** journal session start takes the session's lease with the server's lapse, so another machine's start is refused for a minute and a half after the holder's last renewal and takes it after, as the Team chat's claim does.

## A session driving a plan takes the plan's lease too (task 3156)

- `journal session start <name> --plan <n>` checks the plan's binding on this machine first (PlanBindings.check, against the session if it exists), so a plan a local environment drives refuses the start before the session is touched; then it takes the session's lease and drives the plan from the session through HubDrives, which takes the plan's lease and binds it there. A local environment's drive of a plan a session drives is refused by the same binding, and a drive from another machine by the lease, so a local environment and a session never drive one plan at once.

## The chat's mark kinds are registered once (task 3277, messages 59306 and 59316)

- **MarkKinds (src/journal/support/mark_kinds.py) registers every kind of chat mark beside CardType**: each CardType and the turn kinds only the viewer draws (thoughts, visitors, acknowledgements, the agents talking; a receipt is a mark of what was filed), with its label, icon, group, whether it is a main mark of its group or a detail (a sequence's steps, acknowledgements, sync conflicts) and whether it starts shown (every kind does since the chat marks redesign; a pane still holding the former default hidden list reads as the new default). The groups are registered too. The manifest serves it as marks, and the viewer's chatVisibility.js builds Show in chat, the defaults and the turn mapping from it alone; src/web/tests/fixtures/markKinds.json is the served registry the viewer's tests read, held equal to it by a server test.
- **Chat marks lists the groups, each with a switch that shows or hides all of it**, and opens a group only while it is on, with Only its main marks when it has details, and then its kinds one by one.

## Workers work through a queue without interrupting the dispatcher (plan 1032, 2026-10-25)

- A worker's report choice is a field on its row: each (the default, and what an older row or teammate reads as), queue, or every <n> of two or more. `journal worker dispatch` and `journal worker queue` take `--report`; the worker page sets it through the same action. A pool worker takes only each for now.
- A clock-out whose report point is not reached finishes the task instead: its holder link turns into a finished-unmerged link, the next queued task is handed over and its brief printed, in the same session, with nothing in the dispatcher's chat; the move is on the worker's trail and restarts its time limit. A point proved not done, or a blocked next task, makes it report at once.
- A worker whose process ends after such a move is sent on with the task it is on (WorkerQueueTurnEnded, an UNFINISHED state with no dispatcher line). An end of a run never takes commits in any more: its report lists them as waiting, unchecked (law L10).
- One merge takes every finished task in, refused while any has an unchecked point (named with `--task`); `journal worker check --task N --short` puts the worker back on that task. `release` refuses while finished tasks wait, unless `--drop`.
- A merge is a background journal command (a feature command's `background_verbs`), streamed line by line from the server through the shim, printing `step n/5`, which the shipped worker-merge reader shows as progress. A merge re-reads its worker after the plugin gate. The shim waits as long as a command runs and falls back to the package only when no server could be reached.
- Interruptions: each clock-out is kept on the dispatcher's row with the open work then (open tasks of approved and started plans, `Plans.open_work_count`, the one definition). The reports an hour filed while plenty was open are scored between a full and a no-score rate, once two such reports are in the window. A report within a minute of its job's start with plenty open drops the fitness at once, tells the dispatcher to queue that worker several tasks (once in ten minutes), and recovers straight over its minutes; the timeline names the cause and the recovery. A stuck clock-out (a point not done) costs nothing.
- Task size is one definition (`TaskSizes`, by a brief's points): several small tasks reported each are told `--report queue` fits and cost a misfit drop, unless another cause's drop still recovers.
- In orchestrator mode, workers with merges over the window are scored on their queues: empty while tasks are open, or holding more than they drain in the hours set, lowers the score with the remedy. Every number is a Fitness setting, opened from the fitness panel's cogwheel.

## The event simulator (plan 1033, 2026-10-26)

- One clock: every write, hook and worker move reads TimeSource; a replay or a simulation pins it, and the custom rule WallClockOutsideTimeSourceDetector flags any other clock read.
- tests/simulation plays a scenario in-process from a seed: a simulated user writes at its rate, simulated workers clock out after their job length, the engine's own moments (pauses, compaction, sessions) come at their rate, and the main agent plays a policy (builder, orchestrator, solo, careless) through the same hooks a real agent sends, every journal command as a shell tool use with its own tool_use_id. Two runs with one seed give the same trace.
- Invariants are checked after every step (progress, holds that lift, locks, longest stays, livelocks of forty refusals, contradictions); a random run that breaks one writes a replayable trace and the shrinker cuts it to the fewest actions.
- Commands: `journal suite tests/simulation_run.py` (SIM_SEED, SIM_RUNS, SIM_MINUTES to vary it); offline rescoring of recorded runs over candidate profiles is tests/simulation/rescoring.py, a sweep over all profiles in seconds.
- The known policies answer the user's messages first, reuse a worker whose work was merged by queuing it the next task, and the task spree scenarios (30 tasks open, 30 messages an hour, 3-minute jobs, two hours) pair a known-good policy with a known-bad one per mode.
- What phase 4 showed: today's tool-use window (50 uses in the mode) leaves most runs unmeasured, since answering 30 messages an hour takes half the agent's actions; the measures are rebuilt on minutes and the load by plan 1034 (doc 1065, reports 1076 and 1077), so the old profiles were not retuned.

## Helpers (plan 1035, 2026-10-26)

- Every helper (worker, reviewer, verifier, Claude Code subagent) rests on the engine's Void: it can run a journal command and nothing else until the journal gives it its job. A worker is pushed WorkingTask when it clocks in (WorkerAssigner, through HelperAssignment); a reviewer, a verifier and a subagent start on their file's first state (Reviewing, Verifying, Researching) over Void. A panic reset keeps Void and the job; a compaction goes over the job and pops back to it.
- One file per helper role, src/journal/helpers/<role>_helper.py, says everything that reaches it: `features` turned on whole (each feature gives a role what it declares in `helper_conduct` and `helper_listeners`, and its data part), `listeners` turned on alone, and `commands` as (command class, verb) pairs. Helpers.ALL is handed to the Registry at boot, which refuses a role with no file or two and a listener named alone that a whole feature already gives (HelperFilesInvalid). The Helper base class lives in features so the registry needs no import of the helpers package.
- The funnels: HelperListeners for a helper's hooks, deferred listeners and command events (the engine reaches it through AgentEventAudience); StateMachine.audience asks receives_row_event, and every row event names its feature (RowEvent.feature_name, engine by default); DataReaders refuses a helper the parts of features its file does not turn on (HelperPartViolation); the console refuses a verb a helper's file does not name, naming the file (VerbRules); PluginRelay reaches a helper only for plugins whose manifest names its role (workers, reviewers, verifiers, subagents) and whose file turns Plugins on.
- Caller has a role (AgentRole, now in support) and a session role (a subagent's is its parent's); CallerKind, Command.callers and is_worker_listener are gone. SessionAgents is the one funnel that makes agent rows, on the floor of the row's role.
- A subagent's PreToolUse, PostToolUse and PostToolUseFailure are re-addressed to its own session, main session:agent_id, on a SUBAGENT row; hook.sh sends its PostToolUse since this plan. Its SubagentStop and its main session's end end the row; the main agent keeps SubagentStarted and SubagentEnded for its cards.
- Decided while building: a whole feature never grants commands, so a helper's verbs are only its pairs; the worker's file turns Workers, Tasks, Edits and Plugins on whole, since WorkingTask and its waits read those parts, and only the listeners each declares for the worker reach it, never the main agent's load and fitness recorders.

## Fitness measures (plan 1034, 2026-10-26)

- The design is doc 1065; the baseline on today's measures is report 1081: nothing settled in any scenario.
- The load is two queues, the workers' items and the user's messages (task 3488). The pressure band (low, normal, high) moves on the smoothed worker queue ρ by `BandRule`, per mode from `BandRules`; solo has none, and a mode's first band, after the upgrade or a change from solo, is normal. High is left once no worker item has waited five minutes and is never entered on a queue empty that long.
- Each mode's measures are one table, `MODE_SPECS` in `features/workers/support/mode_measures.py`: key, fail and pass levels, a `MeasureSource` reader, closeness kind and weight, smoothing only for idle places. Their states (value, measured or not, failing, when it changed, when its line was sent) are on the agent row and on `WorkersPart`. The score is worked out from them, version 2, after 30 minutes measured in the mode.
- Where each measure line speaks and which way it pushes is the one table `LineBands`; the simulator's opposed pairs come from it.
- Band margins (task 3492), chosen by `PYTHONPATH=src python3 scripts/band_replay.py` over 2026-10-19 to 2026-10-26 of the development environment, 657 worker items, every day rebuilt from the workers' rows with today's clearings (kept load inputs covered only 2026-10-26, with no worker items). The margins hardly change the count; the least stay does. The defaults are the shortest stay that keeps to one change an hour with the fewest changes there: a 10-minute stay, the orchestrator high from 0.8 to under 0.65 and low under 0.5 to 0.65, the builder high from 0.5 to under 0.4 and low under 0.3 to 0.4.

| mode | margin | stay (min) | changes an hour | longest normal (min) | longest high (min) |
|---|---|---|---|---|---|
| orchestrator | 0.15 | 0 | 1.07 | 71 | 340 |
| orchestrator | 0.15 | 5 | 1.07 | 71 | 336 |
| orchestrator | 0.15 | 10 | 0.94 | 71 | 331 |
| orchestrator | 0.15 | 20 | 0.74 | 71 | 321 |
| builder | 0.10 | 0 | 1.10 | 68 | 341 |
| builder | 0.10 | 5 | 1.07 | 68 | 337 |
| builder | 0.10 | 10 | 0.95 | 76 | 332 |
| builder | 0.10 | 20 | 0.78 | 68 | 322 |

- Before the replay, a band could leave high on an empty queue and enter it again one stay later while the smoothed ρ was still high, five changes an hour; entering high now needs a waiting item.
- What went in phase 6 (task 3507) and why: the old score worked out from the newest fifty tool uses (the mode profiles, their tool-use shares, the fitness levels and the low-score and fall lines) never settled and steered by tool counts, not by work, so the score is the measure states' alone; the quick-report, tiny-job and misfit point drops punished one event with a lasting dent the measures cannot see, so they and the report use they kept are gone; the load lines (rising and drain) and the check reminder spoke whatever the band and were replaced by the measures' clear and check lines; the alignment lines of every mode went with their measures. Migrations 61 and 62 drop the agent columns only they read. The model fits and plan waits are still recorded, to be shown on the page (task 3509).

## Tests drive the real path (task 3572, message 64931)

- The project's test commandments live with its custom detectors in `.commandments/custom`, under the skill tests-drive-the-real-path. `tests/` is not among the judged paths, so they run only when judged by name: `journal suite` (scripts/suite.py) judges `tests` with that skill beside the shards and fails the run on a sin, and the commit gate fails with it.
- The first, TestSettingWriteDetector, flags a test that writes a setting's row with `SettingRows.set`; `user_set` in tests/user_settings.py runs `journal settings set` as the user instead. The full project fixture and the data-layer tests are left out: their subject is the rows.
- Not yet a detector: a hook posting a `journal` command line as if it ran it, and a repository save standing in for a command. Report 1080 found them hard to tell from fair setup by pattern; they are judged by review until a rule tells them apart.

## Task assigners named by states (plan 1041, 2026-10-26)

- A state names the task assigner the engine asks for the agent's next task: `assigner = DefaultTaskAssigner` on Ready,
  PlanStartTaskAssigner on PlansReady (own paused, then an approved plan, then a free task), PlanTaskAssigner on
  FollowingPlan, OrchestratorTaskAssigner on Orchestrating, NoTaskAssigner on the waits, compaction, Void and the
  helpers' states; a state with `assigner = None` (ExternalWait, DemandBlock, which holds tools and not the work) inherits the one beneath, and PlanStartTaskAssigner continues the started plan a closed task was in before an approved plan or free work. AssignerResolution walks the
  stack top down. Doc 1068 holds the table of who takes what next; tests/test_assignment.py proves it.
- The engine asks before the stack answers a hook event (a stop), and after every other listener when a task closes
  (RowAssignment, registered last at boot), so the close is committed and the holder link still readable.
- Only the assigners read auto mode or pick a next task; readers and lines take their pure queries
  (DefaultTaskAssigner.offered, paused_work, OrchestratorTaskAssigner.delegable_tasks). The custom rule
  NextTaskOutsideAssignerDetector guards it.
- The builder is handed its next task; the orchestrator asks with `journal task next --quantity <n>` and is never
  started on one. A worker's next task is still its queue (WorkerActions.send_next); AdvancePlan starts a plan's next
  task only for a close no agent's assigner answers.
- The builder's idle stop names paused tasks and broken waits only; a blocked task is neither started nor named. The
  orchestrator's stop asks about the blocked tasks it can move, then names the tasks to dispatch. The approved-plan
  stop line is gone: an approved plan is the assigner's to start.

## Only background runs get a reader and a card (task 3684, messages 67892 to 67906, 2026-10-26)

- A reader, a watch and a process card belong to a run the journal moved to the background. The runner no longer watches a foreground run as it starts because some reader names its command, which is how every grep got a "Searching the files" card from a project reader that named grep.
- CommandMarkPolicy is the one place that says whether a run may have a mark and a reader; StrayCommandMarkCleanup and StrayReaderCleanup apply it at every start (message 67987). The name word Mark is allowed again, since a chat mark is the project's noun for a bubble.
- A git or GitHub line (GitCommands.is_git_line: every part git or gh) is never watched, never given a reader and shows no card, moved or not, unless it failed; its commit and push marks say what it did. The shipped git-push reader is retired.
- A reader whose commands are all searches, reads or git and GitHub commands (CommandMarkPolicy.takes_no_reader) is refused by journal reader add and removed at boot by the StrayReaderCleanup seed, so a journal that updates is rid of them.

## Plan 1042, phase 1: faults that held or misled the agent (2026-10-26)

- No reader rule holds the agent (task 3689, messages 68009 and 68018): a run with no reader, a reader report, a report read and a refuted dismissal are each told once; the shell demands and their three options are gone. A reader the journal or a plugin ships is never judged.
- A message is corrected in place with journal message edit (task 3687). The rows a message of the agent's refers to with their kind are looked up on the deferred worker after each save; the ones that do not exist are kept in the message's own data (missing_rows), never on the agent's row, which other writers save whole and would put back.
- A plan's next task is its first paused task whose waits are over, else its next open one; a blocked task or a paused one still waiting never stops the plan (task 3690).
- Count forms never take a number before a unit of time as a total; a run whose count moved five times or more raises no stall finding for one slow stretch (task 3683). Only test runs and builds get the buffering hint, and a pause (sleep, alone or with an echo) gets no mark.
- Two races behind the load flakes (task 3678): a helper's end was checked and written in two transactions, so a reviewer handed a new review in between was ended with its old process; and the team account file was changed by unlocked read, merge and write, so the sync thread's sequence number put back an old list of held sessions. The first is one transaction now; the second goes through TeamAccount.merged under a file lock.

## Plan 1042, phase 2: the release check (task 3674, messages 67375, 67926 and 67934)

- The tags are read through the GitHub CLI when it is installed and logged in, else over HTTP without a login. A 403 or 429 for asking too often raises ReleaseRefusal with GitHub's reset time: nothing is said to the user, and the next look waits until then.
- Every look and refusal is stored for the whole machine in release-check.json of the machine folder (AGENT_JOURNAL_MACHINE, else ~/.journal; tests point it at a scratch folder). A journal that starts counts its next look from that stored one and keeps its tags, so a restart never looks at its start; the launcher's boot menu always looks.
- The changelog page has a button that runs the install command from the README (raw.githubusercontent.com, not counted by the API's limit), ref main; the page reloads once the journal answers as another version or a newly started process (started_at).

## Sequences on the stack (plan 1042 phase 3, tasks 3581 and 3521)

- A sequence step is a record, SequenceStep: title, instructions, file_edits_allowed and allowed_commands (patterns on the shell line); reads and journal commands always go through. Stored strings became records by migration 67, and a string still reads as its instructions.
- A running sequence is the state FollowingSequence on the agent's stack, its run (steps as they were at the start, step, subject, end condition, pause reason, times) its one field. It is pushed by SequencesConduct on SequenceRunStarted and moved by row events on the agent: SequenceStepFollowed, SequenceStepFinished, SequenceStepSkipped, SequenceRunPaused, SequenceRunAbandoned, SequenceRunCancelled, SequenceRunCannotFinish. One started inside another is pushed over it; when it pops, the one beneath says its step in on_resume, typed to the agent rather than printed by the command.
- RunTracker is the one path that starts and moves runs, by those events; StackedRuns reads the runs from the stack. Agent.sequence_runs is gone; migration 68 put kept runs on the stack. The run cards come from listeners on the events (RunStartCard, RunStepCard, RunEndCard).

## The choice of paused work (plan 1043, reports 1087, 1088 and 1089, 2026-10-26)

- A paused task resumes by itself only once its wait ended: `Task.wait_ended_at` is set by `wait_ended` and cleared by a
  start or a pause, a column the schema adds at boot with no migration. Tasks paused before the upgrade carry no mark and
  go to the choice. With no free open task the first paused task is taken up, as there is nothing to choose.
- Paused work the agent may choose (not delegated, not of a draft or paused plan, held by no live other agent or worker,
  waiting on nothing) holds the free task back unless the free one is more urgent than every paused one. Blocked work never
  holds it: the agent cannot move a blocked task, so the choice only names blocked tasks with no wait for information.
- An approved plan and the next task of the closed task's plan start before the gate.
- `ChoosingPausedWork` is pushed by the idle floor at a stop in auto mode, the pushing stop counted as its first of two
  refusals; then the floor's assigner takes the first paused task up. It names no assigner of its own, forwards the agent's
  own task start and a plan start to the floor, and pops on a decline, on empty lists and on a switch of the work mode
  (the workers conduct, through `BaseState.is_mode_bound`). The orchestrator's floor pushes no choice.
- A decline (`journal task skip-paused`, or the user's own words while choosing) is a fact on the agent row,
  `paused_declined`, not a field on Ready: a command writes rows and cannot set a state's field, and Ready cannot learn why
  the choice popped. It lets the free task through until the next close, which ends it at once and asks again.
- A task just paused with `journal task pause` is offered at the next stop among the others; that is the choice, not a loop.

## Memories that fade (plan 1044, 2026-10-27)

- Facts become memories: a row with a weight from 1 to 10 that every compaction lowers by one; at nought it is no longer shown, and a removed one stays on its row. `journal memory add`, `weigh`, `list`, `remove` and `skip`; migration 72 made every standing fact a memory of weight 5. Doc 1070 is the design, report 1091 the review.
- The context marks are 50, 80 and 90 percent. A reading under the highest mark taken means the window was compacted, so the marks start again; a compaction clears the mark owed.
- At a mark the memory conduct pushes WeighingMemories over the work: writes and stops wait, reads and journal commands go through, a memory command or skip pops it (ContextDecided). A mark reached while the top takes no pushes stays owed on the row (threshold_due) and is pushed once it can be. A compaction over it pops it in on_resume. A subagent's events never push it.
- The memories always open the overview after a compaction, a fixed part, never one of the look commands (message 69528).

## One classifier for every command reader (plan 1045 phase 3, task 3773, 2026-10-27)

- A call's parts are classified where the hook is translated (`Provider.call` takes the `CommandClassifier`): each part's
  write flag and files are filled from its classification, so a stored part keeps its shape and an old entry reads back as
  written. Unknown is no write; uncertain is a write; an interpreter row (`interpreted`) is a write only by its content
  markers; the journal's own commands never write. The old write rule's verdicts on the corpus are frozen in
  `tests/shell_corpus_reading/writes_before.json` and the classifier's differences in `write_disagreements.json`.
- The table carries what the hand lists held: row labels (`label`, `bare_label`, `redirected_label`, modifier labels),
  `runs_script_file`, `starts_processes`, the `scripts` rows a test script is known by, and wrappers with several
  subcommands, an end word, lookup flags, a code check and `limits_time`. `ActivityLabel` is a container class reading
  its labels through the classifier; `CommandLines` holds a line's read, code-read and code-write readings, the disk step
  after the table. States read `part.classification` (test runs, test or build, reads) from the event.
- Task 3782: `CommandShape` is a container class over the table: its runners (`runs_script_file`), launchers, launcher
  subcommands, the wrappers a shape skips (`dropped_from_shape`, `may_follow_a_script`) and the redirects (`redirects.reads`
  beside `writes`, one pattern the table compiles) are the table's. Each part carries its shape and the call its shape and
  bare name, so conduct reads them from the event; Readers matches a reader's commands, AliasLines an alias, by those shapes.
  The stored shapes stay as they were: `shapes_before.json` freezes every corpus line's old shape, one line changed
  (`env -C dir journal …` is now named for the journal command), frozen in `shape_disagreements.json`. No migration.
- CommandPart keeps writes, files, reads_output and read_shape as stored fields beside the classification: writes and
  files are filled from it, the output read's two from the line. Stored doing labels stay as history. The mark rules read
  the corpus as before (`mark_readings_before.json`); only seven reads the table now reads through (`\ls`, `command ls`,
  a sed of a log) are newly quick reads, so a mark of one of those may go at boot.
- Task 3783: `ClassificationTable(config, schema)` merges a project's own `.journal/command_table.json` (programs,
  wrappers, scripts) over the shipped table when it follows the schema (`TableSchema`, the schema read into `SchemaNode`s,
  the one checker the table's own test uses too); one off its schema is left out, its faults kept. The version stays the
  shipped table's, so an installed and a fresh journal of a release stamp the same one; the table is a file of the package
  install.sh copies whole. The classifier keeps the last 4096 readings. A Codex line handed to a shell carries the shell on
  its ShellLine; a shell that is not POSIX (pwsh, python3 -c) has its line read whole, so its code is never split as a
  shell line.
- Task 3776: the six reader lines are one, `READER_DRAFT`, said by the shell conduct with the line naming ended outputs
  or the end of a watch, never while a run runs. `ReaderDrafts` picks the offers into `ShellData.reader_drafts`: a run
  moved to the background and ended, whose first part earns a reader by its kind (`StartingReaders.starting`: test run,
  build, install or a long process) or by two hand reads, never the journal's own or a plugin alias's, once per project
  and part (the nudge lines said, `Entries.environment_lines`), three per session, none to a worker. It names the part
  and a `journal reader add` filled from the run's output. ShellRunner.watch_lines says no reader line.
- Task 3777: a new reader is also tried by the kind of run it reads (`ReaderKindChecks`, after the judge's misses on the
  two newest runs): its --progress must match a line of the newest ended run, and a test run's reader must show the
  counts of the newest passing run in its finished card and of the newest failing run in its failed card when both are
  stored. A reader stored before, a script and a reader an alias names are never refused by these; a locked reader is
  refused before any trial. The measures live in a "Shell readers" section of the Developer tab's numbers
  (`ReaderMeasures`, GET /journal/developer/readers, per environment): background runs read by a project reader
  (watch_reader set) over all moved runs, reports per reader per ten of its runs, the reader suggestions (the
  READER_DRAFT nudge entries, their part in the values) a reader now reads, and suggestions per session that moved a run.
  The drafts said once per part read the part from the nudge's values, not its line.
- Task 3784: the draft's numbers are two settings the conduct reads, `shell.reader_suggestions` (the most in a session,
  0 turns them off) and `shell.reader_suggestion_runs` (runs of a part since it was told before it is told again, 0 only
  once). The told parts are `ReaderSuggestion` rows, one per part for the whole journal, written by ReaderSuggestionRecord
  when the line is delivered and taken away by ReaderSuggestionClear when a reader added reads the part; the parts the
  replaced lines told (make_its_reader, counting_reader_suggestion, reader_needed, add_a_reader) are read from their
  nudge entries across environments, so nothing is told again. The draft carries whether its part was told and its runs
  since; the conduct decides. ReaderGuess runs for the main agent alone, refuses a reader that would read a plugin's alias
  and shows a card in the chat when it saves one.

## Memory after a compaction, and lines said once (plan 1046, 2026-10-27)

- A memory names rows in its text (task 3804, worker 1140). The start block and the overview read its memories from one place,
  StartLines.memory_line, which adds "check it still holds" with each named row that has closed since: a task or plan done or
  cancelled, a worker stopped, released or merged, or a row not found (ClosedRows, read from the text, since a deleted row's
  links are gone with it).
- After a compaction ReadingOverview refuses with one line naming every skill still to read and the overview, and stops the
  event's walk, so no second line stands beside it. Outside that state the skills still owed are named in one line too.
- A forward ends the walk of an event's listeners: the state beneath hears the event, the conduct with it, once. Before this the
  start after a compaction reached the conduct twice and the overview state's push was dropped.
- The memories mark of a compaction keeps its round in its data: each memory still shown and each faded out with its weight
  before and after, and each removed since the agent's last round. The mark opens to it in place; a mark from before rounds
  were kept says the round was not recorded.
- Marking a message read raises MessageRead; the messages conduct answers it with the reply line for that message, once.
  A hook answer says each line once (Decision). A stopped agent's lines wait delivery.batch_seconds from the first one and
  are typed together on the clock's tick, each once; a working agent's go into its next hook answer as before.
