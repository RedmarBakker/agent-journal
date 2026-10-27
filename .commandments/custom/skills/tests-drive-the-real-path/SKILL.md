---
name: TestsDriveTheRealPath
description: Load it before writing a test, or when a test is flagged for writing a command's row or for checking a nudge by its words, so every test runs the path the agent and the user really take.
summary: A test drives the command the agent or the user runs and reads what the agent is sent; it never writes the rows a command would write to stand in for it.
tier: mandatory
languages: [python]
---

# Tests drive the real path

A test proves the behaviour the way it really happens: it runs the command the agent or the user runs, posts the hooks
the agent's own tool uses post, and reads what the agent is actually sent, so the whole path runs: the hook, the state
machine, the conduct, the nudger and the delivery. A test that writes the row a command would have written skips the
command's parsing, its checks and its events, and stays green when the command is broken. Two faults slipped through
that way on 2026-10-26: a setting shipped as a number because its test wrote the row, and a state's line was lost
because no test read what reached the agent.

## The rule

- Set a setting with `journal settings set <key> <value>` through the console, as the caller who may set it (the user
  for a setting that is the user's), never with `SettingRows.set`.
- Never switch a setting off to skip the engine's own timing.
- Assert on what reaches the agent (the hook's answer, the delivered lines), not on a state's method alone, when the claim
  is about what the agent hears.
- Fair setup stays: rows the test is not about, a migration given old shapes, a time backdated that no command can make.

## Example

Bad:

```python
app.container.get(SettingRows).set("workers.mode", "orchestrator", Actor.user(1))
```

Good:

```python
user_set(app, "workers.mode", "orchestrator")
```

where `user_set` (tests/user_settings.py) runs `journal settings set workers.mode orchestrator` as the user.

## A nudge is checked by the registry

A test that checks a nudge reached the agent never compares a string of the nudge's words: the words change, and
another line can contain them. It names the nudge and its values, and `nudge_reached` (tests/nudge_lines.py) finds the
nudger's entry for that nudge with those values and its line in the text the agent was sent.

Bad:

```python
assert "a guard failed and let this through" in body["error"]
```

Good:

```python
assert nudge_reached(app, body["error"], EngineNudges.GUARD_FAILED)
```

Where no nudger ran, a unit test of a state or a conduct, the line is built from the nudge itself:
`has_nudge(line, Nudges.NAME, value=...)` or `Nudges.NAME.create(value=...).rendered()`. An assert's own message is
not judged.

The rule reads the nudges' words from `nudge_words` in .commandments/custom/lists.json, written from the registry by
`PYTHONPATH=src python3 -m scripts.nudge_words`.
