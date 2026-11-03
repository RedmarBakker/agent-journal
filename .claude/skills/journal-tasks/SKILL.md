---
name: journal-tasks
description: Declare, log and finish the current work; load it when you start or are asked to
---

# Tasks

A task is one unit of work with a lifecycle: open, started, done. Only one is current at a time. A quick edit
needs no task; file one for work that is an item of its own, that waits, or that the user should see tracked.

- `journal task create "<title>" --brief "<what and where to start>"` files one; `--start` starts it at once.
- Add `--from <message n>` when it comes from one of the user's messages, so the chat shows the task above it:
  `journal task create "Footer names the shop" --brief "Done when every page's footer shows the shop name" --from 412 --start`.
- Add `--priority low|high|critical` when the task is not normal.
- Five tasks of yours left at the default priority are asked about once; at ten your next write waits until each has
  one from `journal task edit <n> --priority <level>`, or `journal task priorities confirm` says normal is right.
- `journal task edit <n> --title "<title>" --brief "<what and done when>"` writes either or both anew: the title when
  the first was wrong, the brief when the user corrects a task or a plan's review changes it.
- Read the brief with `journal task show <n>` before you edit it: `--brief` replaces it whole.
- Never write a revision as a log line. Add `--from <message n>` to an edit when a message of the user's changes the task.
- `journal task start <n>` takes a task in hand; `journal task list` shows every task here.
- `journal task show <n>` reads one whole, title, state, plan and phase, brief and every log line, so you pick it up
  where it stood.
- Log with `journal task log <n> "<where it stands>"` after each step that matters, and always before a compaction.
- Only the task in hand takes a log line; change a task not running with `journal task edit`.
- Finish with `journal task complete <n> --how "<outcome>"`:
  `journal task complete 12 --how "Every footer shows the shop name; test_footer passes"`.
- One task is in hand at a time: starting another blocks the one in hand until the new one closes, and the output
  says so; it opens again then and auto mode takes it up.
- A task is never paused: a task that waits is blocked, and `journal task start <n>` on a blocked task takes it up again.
- A wait is a block the journal can see, never words in a log line.
- Block a task that waits on another with `journal task block <n> --on task:<m>`, or on an answer with
  `--on question:12`: it opens by itself once that row is answered or closed.
- Block one that waits on anything else with `--until '<command>'`, run every two minutes, such as a check that a pull
  request is merged; it opens once the command passes. Single quotes keep a `$(...)` in it to run each time.
- Block one that waits on a decision with no row to watch with `journal task block <n> "<what it waits on>"`, and open
  it with `journal task unblock <n>` when that has arrived.
- A blocked task is never offered; one with nothing to end it is named every five completed tasks or thirty minutes,
  whichever comes first, idle or not (settings tasks.loose_block_tasks and tasks.loose_block_minutes): unblock it if
  it can go on, else make it wait on a task or a check.
- A task whose test run failed is blocked with what failed.
- Unblocking a task or a plan, by hand or by its wait, releases its waits and retires the check its block made.
- Wait for something outside your control with `journal await "<what you wait for>" --output <n>` for a command in the
  background, or `--until "<script>"`, run every 30 seconds, for anything else; then end your turn.
- Add `--reader <name>` to a wait on a command to watch it as it runs while you wait.
- A wait ends by itself once its thing is done, and you are told the result; working again ends it too.
- A wait that names neither, or a wait on the user, is refused: ask with `journal question ask`, or end your turn.
- Log as you go, counted in edits: after twenty-five with nothing logged you are asked to, every twenty-five the current
  work is named again, and at fifty the next write waits for the log line (settings tasks.first_nudge_after,
  tasks.name_every and tasks.log_after). A log line starts a new version.
- A stop with current work names it again, three times a version; then the stop passes.
- A commit whose message includes `Journal: tasks done <n>` on a line of its own completes task n.
- Auto mode (the setting tasks.auto, on by default) works the list: at a stop, or when your task closes with none in
  hand, the journal starts the next for you, and only the user stops you.
- Auto mode's next is the next task of your plan or of an approved plan, then the first open task by priority; a
  blocked task is among them as soon as its block ends.
- With auto mode off the journal starts no task for you.
- File work you put off in words as a task: work put off in words is lost.
- Stopping with a task in hand is informed to continue.
- When you are stuck, say so with `journal stuck "<why>"`: the journal sends nothing until your next tool use.
