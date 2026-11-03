---
name: journal
description: Find your way in the journal: what it is, its basic ideas and which skill to read for what; read at the start of every session, with the etiquette skill
---

# The journal

The journal keeps this project's lasting state beside the code and tells you what to do at the moments you would
otherwise get wrong.

A line that starts with [journal] is the journal speaking, never the user: act on it as an instruction, and never
answer it, quote it or write about it in the chat.

Every command is `journal <noun> <verb>`; `journal <noun> --help` lists the verbs. A row has a kind and a number,
task 12, plan 3, message 7: write both, so the chat links it.

- An environment is one line of work in this project, with its own agents, tasks and chat.
- You are the main agent of your environment, with a stack of states: what you do now sits over what you were doing, and gives way back to it.
- A plan orders tasks and has a solo or organization plan mode. With Plan agents enabled, a started plan has its own Plan agent; in organization plan mode it coordinates Domain agents and Roles, while in solo plan mode it takes on Roles one at a time.
- A Role's organization contract says what work it owns, the tools and model it may use, and the guidance it follows.
- A task is work in hand; a message or a question is what you and the user say to each other.
- A memory keeps what matters past the context window; a worker writes for you on one task, a subagent only reads.
- A sequence is steps followed one at a time; an output is a command's output, kept and read by its number.

When the journal holds you, its line says why and names the way out. After a compaction or a new start, run
`journal environment overview` before anything else. Search before you say you do not know or ask the user again:
`journal search "<words>"`. A pin is a note the user sees on coming back, a button an action for now under your
message: the pinned-links and messages skills say which to use.

| Read | For | The journal asks for it |
|---|---|---|
| etiquette, messages | the chat, messages, questions, pins and buttons | at every start; a message, a question |
| tasks, plans | work in hand, blocks, waits, being stuck; ordered tasks and plan modes | a task or plan command, a plan you follow |
| workers | bounded worker jobs and subagents | a worker command |
| shell, memory | commands, outputs, readers, aliases; memories, rules, reminders | an output or alias; a context mark |
| sequences, docs, reports, templates | steps; lasting knowledge; what was checked; templates | their commands |
| checks, dumps, collections, flowcharts | checks; dropped material; groups of rows; flowcharts | their commands, a check failing, a dump |
| pinned-links, plugins, secrets | links for the user; plugins; keys and logins | their commands and words |
| organization-seat-routing | route work from the Plan agent through Domain agents to Roles | an organization seat receives or hands off work |
