# Memory

What the agent keeps in mind beyond one context window, and how long it keeps it.

## Memories

A memory is a row of its environment: what to keep in mind, in one or two plain sentences, and a weight from 1 to 10.
Every compaction of the agent that owns it lowers its weight by one. At nought the memory is no longer shown; it
stays on its row. The agent, or the user in the viewer, may raise or lower a weight at any time, so a memory that
still matters climbs back.

- `journal memory add "<what to keep in mind>" --weight 7` adds one.
- `journal memory weigh 3,7,9 5,8,2` gives each its own weight, in order; `journal memory weigh 3,7,9 5` gives them all one.
- `journal memory list` names every memory still shown, heaviest first, with its number and weight.
- `journal memory remove 3,7` takes out the ones no longer true; they stay on their rows, never shown again.
- `journal memory skip "<why>"` says nothing needs keeping at a mark.

## Whose memories

Every memory has one owner, and only its owner sees, lists, weighs, removes and fades it. The main agent's memories
link to no row; a worker's link to the worker's row by an owner link. `journal memory weigh` and `remove` refuse a
number another agent owns, and `journal memory list` and the overview show the caller's own alone. The search finds the
main agent's memories only.

- A worker adds, weighs, lists, removes and skips as the main agent does. Its memories are shown to it each time its
  `journal clock-in` has run: on its first job, and on each next job sent to it with `journal worker send`, so reusing a
  worker reuses its memories. Its own compactions fade them, the main agent's never do, and it weighs them at the marks
  of its own context window, where `journal memory skip "<why>"` says it has nothing to keep.
- A reviewer lists its own, which are none, since it adds none.
- A subagent keeps no memories: its journal command names no row of its own, only that it is some subagent of its
  agent, so it runs no memory command, and its compactions fade none.

The viewer lists the memories with their weights, and the user adds, weighs and removes one there. Each change is a
card in the chat, and so is the fading at each compaction.

## The marks

At 50, 80 and 90 percent of the context window the memory conduct pushes the state WeighingMemories over the work. Its
line lists the memories by number and weight. While it is on top, writes and stops wait; reads and journal commands go
through. Adding, weighing or removing a memory, or skipping, pops it. A mark reached while the top state takes no
pushes (a wait, the overview after a compaction) stays owed on the agent's row and is pushed once it can be. A
compaction clears the mark owed, and the first reading of the new window starts the marks again.

## After a compaction

The overview opens with the memories by weight and the line to weigh them: a fixed part, never one of the commands
in the setting briefing.look_commands, so it cannot be switched off. The agent weighs them right after the overview.

## Rules and reminders

A rule is a ruling of the user's that binds the whole project; a reminder is what to keep doing here. A reminder may
be set for a moment with `--at`, or repeat with `--every-minutes` or `--every-tool-uses` while it holds.
