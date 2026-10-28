---
name: writing-scenario-tests
description: How a new feature or a change in behaviour starts in this project - its requirements written first as scenario stories, every case and edge case in one file, run red together, then the code. Load it before writing any feature, command or state change.
---

# Writing scenario tests

A feature starts as its requirements, written as stories in `tests/scenarios/`, before any of its code. The stories
are the specification: a case without a story is a case nobody decided.

Stories are the preferred way to test behaviour. A unit test still fits a single part on its own, a parser or a
model's pure method; the older behaviour tests in `tests/` are looked
over one by one, those a story now covers are removed, and no new behaviour test is added there.

## 1. Think every case through first

Before a line of a story, write down for yourself what the feature does in each situation it can meet:

- **The plain case**: what it does when nothing is in the way.
- **Every state a row can be in**: open, started, paused, in testing, blocked, closed. A feature that moves or changes a
  row keeps its state exactly unless the feature is about changing it.
- **Every agent that holds the row**: the agent working on it now, a plan that will start it next, a worker or a queue
  that owns it, a wait on it, an agent in another environment that receives it. Say what each one is told and where its
  stack ends.
- **How nobody gets stuck**: after the feature runs, every agent can still stop, go on with its next work, or is told
  what to do. A refusal names the way out (a flag, a command to run first).
- **What is refused, and what a flag such as `--force` allows**, and what it never allows.

## 2. Write every story in one file, in one go

- One file per behaviour, named for it: `scenario_task_transfer.py`, never `scenario_environments.py`. It holds every
  case of that behaviour and nothing else; another concern gets its own small file.
- One story per case, its name the sentence of what happens:
  `test_a_paused_task_arrives_paused_and_is_no_longer_offered_here`.
- Start each story from the fixture whose rows it uses (`@scenario(TaskInHand, end=[IDLE])`); `end` is the stack the
  story leaves, bottom first.
- Play the agent through `scenario.agent_runs(...)` and hooks, the user through the viewer's routes, never the CLI.
- A setting the story needs is set with `@settings(TasksOptions.WAKE_MINUTES, 10)` above the story, one per setting:
  the user sets it through the viewer's route after the start fixture and before the first step, and the story fails
  when the journal never reads it. A story that tries several values uses `@values_of(option)` (a switch off and on,
  a number none, one, a middle and its default) or `@values(...)` with `scenario.user_sets(option, value)` inside.
- Numbers come from the code, never copied: `@values(MemoryThresholds.CONTEXT)`, `scenario.setting(option) + 1`,
  `scenario.agent_consumes(option)` for as many tool uses as a setting allows.
- Check what reaches the agent (`expect_agent_told`, `expect_refused`), the rows (`expect_task`, `task_numbers_in`) and
  the stack.
- A step the builder lacks is added to the builder in `tests/scenarios/builder/`, once, for every story to use.

## 3. Run them together, see them fail

Run the file once: `journal suite tests/scenarios/scenario_<behaviour>.py -q`. Every new case should fail for the
reason you expect. A story that passes before the code exists tests nothing new; a story failing for another reason is
fixed first.

## 4. Then write the code

Write the code until the whole file passes. Then run every story once (`journal suite tests/scenarios -q`): the path
overlay fails a story that walks nothing of its own, so two stories that check the same path become one.
