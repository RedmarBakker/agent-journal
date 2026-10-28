---
name: writing-story-tests
description: How a new feature or a change in behaviour starts in this project - its requirements written first as stories, every case and edge case in one file, run red together, then the code. Load it before writing any feature, command or state change.
---

# Writing story tests

**Behaviour that drives the agent is written as a story before it is built.** Anything that changes what the journal
tells the agent, what it lets the agent do or refuses, or where the agent's stack goes, is a behaviour that drives the
agent. Its stories come first: every case it can meet, written and run red, then the code that makes them pass. This is
how every such feature, fix and change is made here, in a plan or outside one. The parts beneath it, the engine, a
repository, a parser, a model's pure method, are not stories: they get unit tests of their own, or none.

A feature starts as its requirements, written as stories in `tests/stories/`, before any of its code. The stories
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

- One folder per subject under `tests/stories/` (`messages/`, `tasks/`, `plans/`, `workers/`, `agent/`, `shell/`,
  `sequences/`, `developer/`), one file per behaviour, named for it: `tasks/task_transfer.py`, never `environments.py`. It holds every
  case of that behaviour and nothing else; another concern gets its own small file.
- One story per case, its name the sentence of what happens:
  `test_a_paused_task_arrives_paused_and_is_no_longer_offered_here`.
- Start each story from the fixture whose rows it uses (`@story(TaskInHand, end=[IDLE])`); `end` is the stack the
  story leaves, bottom first.
- Play the agent through `story.agent_runs(...)` and hooks, the user through the viewer's routes, never the CLI.
- A setting the story needs is set with `@setting(TasksOptions.WAKE_MINUTES, 10)` above the story, one per setting, repeated for more:
  the user sets it through the viewer's route after the start fixture and before the first step, and the story fails
  when the journal never reads it. No `@values`: each case is a story of its own, from a fixture.
- A story runs once, on a VoidProvider that sends and expects nothing of Claude or Codex; `@provider("codex")` marks the
  few stories where the provider is what is tested.
- A story holds no assert: every check is an expect method of the builder, which holds the assert. The
  StoryAssertDetector flags an assert in `tests/stories/`.
- Numbers come from the code, never copied: `MemoryThresholds.CONTEXT[0]`, `story.setting(option) + 1`,
  `story.agent_consumes(option)` for as many tool uses as a setting allows.
- Check what reaches the agent (`expect_agent_told`, `expect_refused`), the rows (`expect_task`, `task_numbers_in`) and
  the stack.
- A step the builder lacks is added to the builder in `tests/stories/builder/`, once, for every story to use.

## 3. Run them together, see them fail

Run the file once: `journal suite tests/stories/<subject>/<behaviour>.py -q`. Every new case should fail for the
reason you expect. A story that passes before the code exists tests nothing new; a story failing for another reason is
fixed first.

## 4. Then write the code

Write the code until the whole file passes. Then run every story once (`journal suite tests/stories -q`): the path
overlay fails a story that walks nothing of its own, so two stories that check the same path become one.
