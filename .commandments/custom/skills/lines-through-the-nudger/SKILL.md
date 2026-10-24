---
name: lines-through-the-nudger
description: Every line the journal says to an agent goes through the Nudger; load it when line-outside-nudger fires
---

# Lines go through the Nudger

The Nudger is the one funnel for what the journal says to an agent. It drops a line whose feature is switched off
or that was said within its repeat span, records it in the entries, and announces that it was said. A line built
with `nudge.rendered()` and typed through the supervisor, put in a hook answer or returned as a note skips all of
that: nobody can find it in the record and its switch does not silence it.

## What to do

- Hand the Nudge to the Nudger and send the words it returns:
  `line = self.nudger.deliver(agent, nudge)`, then `self.supervisor.type(environment_id, line)` when `line` is set.
- A refusal: `nudger.refuse_with(agent, nudge)`. An answer to a command the agent ran, which must show however
  recently it was said: `nudger.answer(agent, nudge)`.
- The agent comes from the event or the caller: `SessionAgents.agent(session, environment_id)`.
- A line with no nudge yet gets one in its feature's `*_nudges.py`, registered in the feature's `nudges` tuple;
  the engine's own lines are `EngineNudges`.
