---
name: journal-sequences
description: Follow a sequence of steps one at a time; load it when a sequence is run or written
---

# Sequences

Steps followed in order, one at a time. A running sequence stays with you through tasks, waits and new sessions
until its last step is done.

- `journal sequence run <n>` starts one and tells you step 1. Creating a plan starts Building a plan on its own.
- `journal sequence follow` takes the step in hand up: until you do, a write and a command that runs anything but a read
  wait, while reads, journal commands and a subagent's dispatch go through. A command the step names, in backticks, also takes it up when you run it.
- `journal sequence next` when the step is done: you are given the next one, or that the sequence ended and what
  you were doing before it. A step never taken up cannot be moved on.
- `journal sequence pause --why "<why>"` sets the run aside, its holds quiet; `journal sequence follow` resumes it. A run about
  a row you write yourself, such as Building a plan, is not paused: write it, or hand its writing to subagents with
  `journal sequence delegate --why "<who writes it>"`, which lets your edits through while they write it.
- A sequence about a row ends only when the row is where it promises: Building a plan's last step waits for a ready
  plan. A row cancelled or deleted, or the sequence deleted, ends the run and you are informed.
- `journal sequence abandon --why "<why>"` names the steps it would leave undone; again with `--sure` it gives the run
  up and tells the user. Take the step up first.
- Sequences stack: one started while another runs is the top, and only the top is held to and followed, moved on
  or abandoned; when it ends, the one beneath is announced again, its step taken up as it was, and carries on. Only the user's own
  words start a sequence by its trigger.
- A stop with a step open is shown the step once; a wait, an open question or a pending duty to the journal keeps it silent.
- `journal sequence create "<title>" --steps "first | second | third"` writes one. A step with a title and guards is
  `--step "<title> | <instructions>"`, followed by `--hold-edits` when file edits wait while it is in hand and
  `--allow-commands '<pattern>'` for each shell line it lets through; reads and journal commands always go through.
- `--trigger` starts it on its own, one each: `row:plan.created` when a row you create is made, `phrase:'<words>'` when
  the user's message is those words, `command:'<pattern>'` when a shell line matches, `file:'<glob>'` when a file is
  edited, `file-text:'<glob>':'<text>'` when an edit's new text holds the text, `tool:<name>:'<pattern>'` when a tool's
  input matches. Only the main agent's own actions start one; a worker's or a subagent's never do.
- `journal sequence edit <n>` writes the steps or the triggers anew the same way, and `journal sequence show <n>` lists
  its triggers and its steps with their guards.
