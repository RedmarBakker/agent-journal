---
name: journal-reports
description: Put what was just checked or researched in a report linked to what it is about; load it when the user asks for a critique, a review, an update or a write-up
---

# Reports

A report holds what was just checked or researched; lasting knowledge goes in a doc, ordered work in a plan.

- `journal report create "<title>" --abstract "<what it found, in one short line>" --file <path> --about plans:1` writes one
  from a markdown file, its `##` headings as sections, linked to the rows it is about; `--body "<text>"` for a short one:
  `journal report create "Footer audit" --abstract "Three pages miss the shop name in their footer" --file /tmp/footer-audit.md --about tasks:12`.
  The abstract is required, at most 200 characters, and is the line its card and the reports list show;
  `journal report update <n> --abstract "<line>"` writes it anew, with `--file` its whole text too. A report still being written takes `--part`, so its card says
  being written until `journal report ready <n>`.
- `journal report show <n>` reads a report in parts as `journal doc show` reads a document (the docs skill): its outline
  first, then one section. `journal report list` names them.
- In the chat say in one or two plain lines what it concludes, then its reference on a line of its own, like report 3.
- An update for the user: `journal report changes` lists what it covers since the last update the user read, by section;
  `journal report recap "<one or two sentences>"` writes it, your summary over the rows the journal gathered, docked at the
  bottom of the chat. `journal report item <section> <row> "<title>"`, `note <n> "<text>"` and `drop <n>` change the latest.
