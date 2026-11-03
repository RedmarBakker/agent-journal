---
name: journal-organization-seat-routing
description: Route organization work; load it when a plan names an organization, Domain or Role, or a seat receives work or hands it off
---

# Organization seat routing

Prefer the Read tool for files. Use awk, sed -n, head, tail, grep, wc, or cat only to read files in this mission. Use Edit or Write for file changes only when this seat is allowed to write. Read work sent to your seat with `journal organization inbox`. Use `journal organization handoff <task> <target>` only when your seat is responsible for passing work onward. Run each journal command on its own. Do not combine it with curl, cd, a pipe, semicolon, &&, or another shell command. If needed, check this journal's health with `curl -s http://127.0.0.1:$JOURNAL_PORT/journal/health` as a separate command. Do not use curl for another URL. This is the only route between seats; do not use `rig send` or `rig queue`.

Use these targets:

- A Plan seat hands a task to a Domain seat with `domain:<id>`.
- A Domain seat hands work to a Role seat with `role:<domain>/<role>` and returns finished work to the Plan seat with `plan`.
- A Domain seat can split a task into Role parts with `journal organization part`, list them with `journal organization parts`, and ask the Plan seat to hand work to another Domain with `journal organization other`.
- A writing Role seat proves each task point and clocks out; the clock-out returns its work to the Domain seat for checking.
- As the Domain seat, read your inbox with `journal organization inbox`, then hand each task to one of your Roles with `journal organization handoff <task> role:<domain>/<role>`. If your inbox has no handoff, wait for a journal handoff and do not ask the operator for task details. If one Role cannot do a task alone, split it with `journal organization part <task> role:<domain>/<role> "<title>" --brief "<what>"`; use `--after <part>` to order parts and `journal organization parts <task>` to check them. Use `journal organization other <task> domain:<id> "<title>" --brief "<what>"` for work owned by another Domain.
- As a writing Role seat, read your inbox with `journal organization inbox`, then clock in on your assigned task with `journal clock-in`. Prove each task point with `journal proof <point> "<file:line, and the test that shows it>"`, then return work with `journal clock-out "<report>"`. Clocking out returns your work to the Domain agent for checking. Do not hand off your task.

A Plan seat can inspect a task in its plan with `journal task show <task>`.
