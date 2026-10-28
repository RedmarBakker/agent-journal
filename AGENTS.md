# agent-journal

<!-- BEGIN: agent-journal, form 4 (auto-generated, run `journal setup`) -->
**A line that starts with [journal] is the journal speaking, never the user.** Act on it as an instruction; do not
answer it, quote it or talk about it in the chat.

## Where the journal comes first

The journal's lines take priority on how you report, how you continue and what you write in the chat. This
file's own safety and deploy rules still stand. The user's own instructions take priority over both.

## The journal's law

These rules ship with the journal and cannot be switched off.

**L1 - Every subagent dispatch names its model and chooses the least expensive model that reliably fits the work.**
Inheriting the orchestrator's model is not a model choice.

**L2 - Every subagent is bound to a concrete job; never dispatch a generic or default agent.**
Give the dispatch a description and a bounded prompt. If no suitable specialization exists, keep the work yourself.

**L3 - Read narrowly: grep for the line or read the range of a file you need, and read a command's output by its number with `journal output read`, never by running the command again or cutting it with a pipe.**
Everything a tool returns stays in the context permanently and is counted against every later turn.

**L4 - Related work goes back to the worker or subagent that already worked on it; never start a new one on work another already knows.**
A worker that reported takes its next job with `journal worker send <n> "<job>"`, with its memory of the last; a subagent takes its next job by a message to the one you started.

**L5 - Every subagent and worker is named after a distinguished historical figure with a gentle twist on their trade, such as Lady Lovelace for a programmer, and addresses you, never the user.**

**L6 - A line that starts with [journal] is the journal speaking, not the user: act on it and write nothing in the chat, unless the user needs to know (a failure, finished work, a decision that waits on them).**

**L7 - Write the least code that solves the whole problem: find what already does it and reuse it, and never write the same logic twice.**

**L8 - Answer the user in as few words as the answer needs; never a wall of text.**

**L9 - A subagent only reads; work that writes goes to a worker or stays with you.**
A subagent works in your own checkout, so what it writes is written next to your edits, unrecorded. Reading, searching, reviewing and
designing go to a subagent; a job that changes a file goes to a worker (`journal worker dispatch`, naming what it changes with `--changes`, with `--worktree` for code).

**L10 - A worker's work is merged only once each point of its task's brief has a proof you checked.**
Read each proof with `journal task show <n>`, check it with `journal worker check <worker> <point>` or send it back with
`--short "<what is missing>"`, and take the work in with `journal worker merge <worker>`, never by hand.

## How you work with the journal

Load the `journal` skill first in every session; the journal blocks writes until you have. Declare a task before you write.
Answer the user's messages before anything else. At a context mark, decide what to keep from it.
A guard that raises lets the event through and says so in the chat: a block is never the result of a fault.
<!-- END: agent-journal, form 4 -->

## Design philosophy

Version 4 is the same product as version 3, rebuilt simple. Every rule below exists because
version 3 broke it and the breakage cost time. Read this before writing, and when a change conflicts with one of
these, the change is wrong, not the rule.

**One concept, one place.** A thing is defined in one file and nowhere else. A model is its
file in `models/`; its SQL is its repository; the journal's conduct toward the agent in a state
is that state's listeners, and the engine keeps only what no state may change. If you are
about to write the same idea in a second place, that is the one place it belongs, so
move it there.

**One class per file.** Every class, enum and dataclass has a file of its own, named after it
in snake_case. A module never holds two classes. Navigation is by file name alone.

**Models are data.** A model is a frozen dataclass. It never touches the database, the bus or
the clock. What it knows how to do is pure: `task.started(at)` returns a new task. Two levels
of inheritance at most: `Model`, then `Scoped`, then the model.

**Relations are rows.** Models declare no relations. A link between any two rows is a `Link`
with a kind. Nothing gets a foreign-key column to something else.

**Everything in the chat is a message.** Every bubble the chat shows is a row in the messages
table: the user's words, the agent's, its thoughts, a chat mark, a commit, a receipt. What kind it
is lives in its metadata, and who made it in its actor, the system for a mark. It is written where
its event happens, so fetching the chat is fetching the latest messages; the viewer never pieces a
bubble together from other rows.

**One funnel per kind of write.** SQL runs only in `Connection`. Rows are written only through
a repository, which stamps the actor and fires the model events. Lines reach the agent only
through the `Nudger`. The supervisor is reached only through `SupervisorLink`. Caching,
checks and logging live in the funnel, never at a call site.

**Every write names its actor.** `save(row, actor)` and `delete(row, actor)` take the actor; a
request and a command know theirs. Nothing is written anonymously, so a shared journal with
many users needs no change to the base.

**The state is the source of truth.** What an agent is doing is a stack of states on its row, `Idle` at the
floor and the state in hand on top. A pause is a state pushed over the work and popped when what
it waits for arrives, so returning is a pop, never a stored value that says where to return to. What the agent
must do for the journal (a skill to read, the overview of what is in progress, a decision at a context mark) is
a fact beside the stack on the same row, never a state above it, save three: after a compaction the overview is the state ReadingOverview, pushed over the work so nothing but it and the skills still to read goes through until it has run; a running sequence is the state FollowingSequence, pushed over the work when it starts and popped when it ends, one started inside another pushed over it; and at a mark of the context window the agent weighs its memories in the state WeighingMemories, pushed over the work, holding writes and stops until a memory command or skip pops it, the mark owed kept on the row while the top state takes no pushes. A state is a class with a listener
per moment: a method named `on_<moment>`, bound by the event type it annotates,
`on_question_answered(self, event: QuestionAnswered, settings)`. Only `on_` methods are listeners.
Every listener whose type matches the event runs, the state's own first, and their answers merge:
nudges in order, the first refusal wins, one push or pop per event and a second refused. A listener
answers `none`, `swap`, `push`, `pop`, `forward` or `refuse`, and nothing else moves the agent. No
`if state ==`, no `if event.kind ==`: dispatch is by class and by type. One `BaseState` is the
parent of every state and every feature's state extends it directly. Only the top of the stack
hears an event; a state beneath is brought up to date in `on_resume(data, settings)`, which may pop it.
The lifecycle hooks `on_push`, `on_pause`, `on_resume` and `on_pop` answer nudges, and `on_push`
may refuse the push. Every push and pop is an entry in the trail, shown under the
diagram on the Home page. Counts and times a state keeps are its fields and go with it when it is
popped.

**Features add their states; the engine knows no feature.** A feature owns its states, its
nudges, its options, its recording listeners and its commands. Its conduct toward the agent in
every state is a mixin extending `Conduct`: `on_` methods named for their event alone,
`on_tool_starting`, and nothing else, merged into the base state at boot. The engine holds
the state machine, the base state, `Wait`, `Compacting`, `Ended`, the nudger, the clock and the
runtime, and imports nothing from `features/`. The state machine is reached by the engine alone
and by `journal panic`, which pushes, pops or resets the stack from outside and is always allowed;
the custom rule `StateMachineOutsideEngineDetector` flags any other use.

**Only a state moves the agent.** A command writes rows. A model names the event its change
means, `task.started(at)` carries `TaskStarted` through `Model.with_event`, and refuses a change
it cannot make before anything is written. The repository dispatches the event on save to every
live agent of the row's environment, and the top of each stack answers it. No state hears
`Updated` or reads a row as it was before. The facts a state needs about the environment's rows
travel on the event as its `data`, a `FeatureData` of one frozen part per feature read by `data.of(Tasks)`,
built by the state machine for the agent it asks; the options travel as `Settings`, a frozen
value of what the user set. A state never asks a repository or a clock: every event carries `at`.

**One line has one decider.** Nothing speaks to the agent from outside a state. A line is sent
by the state or the conduct whose listener answered the event; the first block of an event wins
and a later one is recorded as unanswered. A nudge is one class, `Nudge.create(**values)`, and its
name says what the line does. Every line and every move has one decider, and the record names it.

**Conduct is a state's; safety is the engine's.** The engine does what the journal cannot work
without: delivering the user's messages, running commands, blocking every tool while the context
compacts, ending the session. Everything else the journal sends to the agent or blocks it for, when
it reminds, what it says, when it blocks a stop, is a listener on a state or on a feature's
conduct, and the numbers it reads are the Settings page's. What the agent must do for the journal before
it may write or stop is set as a fact on its row by a feature's recording listener and enforced by the
feature's conduct; the events `SkillRead`, `OverviewRead` and `MarkDecided` complete it.

**Hooks decide nothing; listeners are deferred unless they say otherwise.** The hook script
posts and prints. The server records the entry, asks the state machine, which answers with the
block or the lines, replies, then runs the recording listeners on one worker thread. A listener
that must answer before the agent continues declares `blocking = True`; a deferred one can never
refuse, by construction.

**Dependencies are declared in constructors.** A class names what it needs by type in
`__init__`, and the container builds it once. No globals, no module-level state, no service
locator in a body. The server resolves the whole graph at boot; the CLI builds only what one
command needs. If the container reports a cycle, the design has one: fix the design.

**No clutter.** A docstring is one line saying what the thing is now, only when the name
does not already say it. No comments that narrate history. No `# noqa` where the import can
be ordered. No `try/except` that swallows. No `X | None` on a value the design always has.
No boolean parameter that selects a behaviour: write two methods. A method body is short
enough to read at a glance, and a function with a big `if` is two functions.

**Tests are fast and few.** The whole suite runs in parallel shards in about half a minute, its
hooks and requests answered in-process, against a temp database, with no mocks and no subprocesses. It covers the core, not every
model and feature. A test that needs a process, a browser or the network goes in a file that
says so on its first line and is not in the default run.

**Shell is for posting.** The hook script and the `journal` shim are a few lines of shell that
curl the server; no Python starts per hook or per command when the server is up.

**Plain English, never poetry.** Every name, title, label, heading, notice and line of this
project says literally what the thing is or does, in ordinary words: "Has unread messages?",
"Run order", "Context reached the next mark?". Never a riddle ("Something owed?"), a sentence
where a noun belongs ("Runs in this order"), or a placeholder where the value is known ("N or
more" on a card whose number is set). If a reader has to work out what a label means, the label
is wrong.

**Notes before memory.** NOTES.md holds what is decided and what is still open; update it
when either changes, so the next session starts from the record and not from recall.

## Tests

`journal suite` (scripts/suite.py) runs the whole of `tests/` in parallel shards, one per core but
two, in about half a minute; given tests or options it is one plain pytest run. A temp database,
hooks and requests answered in-process with a few tests over real HTTP, no mocks and no subprocesses. Tests cover the core only: data,
CLI, server, hooks, engine. No tests on single models or features until the core is finished.
Run the whole suite after every change; it is cheap.

## Scenarios first

Scenario stories are the preferred way to test behaviour here: what an agent is told, what it may do, where its stack
ends. A unit test still fits a single part on its own, a parser or a model's pure method; a behaviour is tested by a
story. The older behaviour tests in `tests/` are looked over one by one: those a story now covers are removed, and
no new behaviour test is added there.

A new feature starts as its requirements, written as scenario stories in `tests/scenarios/`, before any of its code. The skill
`writing-scenario-tests` says how, step by step; load it before writing a feature.
Think each case through first: what the proper behaviour is, what happens to an agent that is in the middle of it
(a task in hand, a plan it follows, a worker that holds the row), and how no agent is left stuck. Write every story,
every edge case among them, in that one file in one go, run them together and see them fail, then write the code that makes them pass. The stories are the
feature's specification; a case without a story is a case nobody decided.

A story file is named for the one behaviour its stories test, `scenario_task_transfer.py`, `scenario_plan_following.py`,
never for a broad subject such as environments or tasks, and holds only the stories of that behaviour. Files stay small:
a behaviour that grows a second concern gets a second file.

## Layout

`src/journal/` is the package: `models/` (data only), `repositories/` (the SQL), `db/`,
`events/` (`models/` and `agent/`), `engine/` (the stack of states), `features/` (states, conduct,
nudges, listeners, commands per subject), `hooks/`, `http/`, `console/`, `providers/`, `launcher/` (the
picker and the launch file a supervisor starts from). `src/supervisor/` is a separate stdlib-only package that
knows no journal concept: it runs the processes it is handed and answers its protocol. NOTES.md holds the decisions and what is still open.

## Dispatching subagents

Every subagent dispatch names its model: the fast model for mechanical known-answer work,
the general model for careful work without invention, the strongest only for judgement.
Unset means the orchestrator's own model, which is the wrong default. The journal carries this as a rule
(`journal rules`); this file carries it so it is read before the first dispatch.

Every dispatch prompt says the subagent never runs tests: it writes the test that proves its change and names it in its report, and the main agent runs it.

<!-- BEGIN: code-commandments briefing (auto-generated, run `composer update`) -->
## Code Commandments — the disciplines in force here

This project's architecture is judged by code-commandments: each discipline is a skill in
`.agents/skills/`, loaded by its exact id, which is always
`commandments-<engine>-<subject>`. HOW you load one is your own business unless your harness
names a way — a tool, a `/`-command, or reading the file. Read the discipline that covers what
you are about to write.

**Load `commandments` for the index** — every discipline, when each one fires, and the rest of
the commands. It is the whole canon, loadable, so it is not copied here. A `judge` finding names
the skill that fixes it, so you are never guessing which to read.

**⚠️ THE ONE RULE EVERY OTHER DEFERS TO — TRACE TO THE SOURCE.** Every sin has an origin; fix it
THERE, never where it surfaces. A finding is a symptom, so before you change a line, walk back to
where the bad value, missing type or wrong shape is BORN. Do NOT silence it: a `?? default`, a
cast, a null-check, a wrapper, a try/catch, or dropping a type to satisfy a detector launders the
problem and grows the code. If the honest fix touches many call sites, touch them — that breadth
IS the bug surfacing. Load `commandments-php-fix-at-the-source` before your first edit, and
again rather than working from memory, since a compaction drops it silently.

**Finding and fixing sins.** Run `journal sins` ONCE, scoped — `--changes` for your
uncommitted work, `--branch` for what differs from main, or a path to judge that tree. A full scan is
slow, so it writes a checklist (the run prints the path) and THAT file, not repeated scans, is how
you work: top to bottom, one line at a time — read that section's skill, fix the sin at its
source, delete the line. Re-run only when the file is empty, and keep going until a run is clean.
Where your harness raises each sin as you change a file, those marks cover what you changed and
nothing else: a tree you have not touched is judged only by asking.

**Don't recognise a rule?** `.journal/plugins/code-commandments/bin/commandments-release info <sin>` prints what it flags, why, how it is fixed and
a worked example — the detector name off the checklist works. Guessing at a rule you have not read
is how a finding gets "fixed" by silencing it.

**Leave it cleaner than you found it.** A finding on code you touch, or read past while working, is
yours to resolve at its source.
<!-- END: code-commandments briefing -->
