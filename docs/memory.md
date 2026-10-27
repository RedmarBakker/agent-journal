# Memory

What the agent keeps in mind beyond one context window, and how long it keeps it.

## Memories

A memory is a row of its environment: what to keep in mind, in one or two plain sentences, and a weight from 1 to 10.
Every compaction of the environment's agent lowers every weight by one. At nought the memory is no longer shown; it
stays on its row. The agent, or the user in the viewer, may raise or lower a weight at any time, so a memory that
still matters climbs back.

- `journal memory add "<what to keep in mind>" --weight 7` adds one.
- `journal memory weigh 3,7,9 5,8,2` gives each its own weight, in order; `journal memory weigh 3,7,9 5` gives them all one.
- `journal memory list` names every memory still shown, heaviest first, with its number and weight.
- `journal memory remove 3,7` takes out the ones no longer true; they stay on their rows, never shown again.
- `journal memory skip "<why>"` says nothing needs keeping at a mark.

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
