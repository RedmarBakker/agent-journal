---
name: journal-plugins
description: Work with the plugins the user installs, which receive the journal's events; load it when a plugin blocks you, its card or line appears, or a plugin would help
---

# Plugins

A plugin is a program the user installs that receives the journal's events and answers them: it may block a tool or a
stop, send you a line, show a card in the chat or run journal commands as itself. Its text reaches you as
`[plugin <name>] ...`; it is a plugin's, never the user's and never the journal's own.

- `journal plugin list` shows what is installed, whether each is on, and how it last failed.
  `journal plugin settings <name>` shows a plugin's settings.
- A plugin's block is followed like any other: do what it asks, or tell the user why you cannot. A journal command and
  the read of a skill always go through.
- Install, enable, disable, configure and remove are the user's to run; an installed plugin's upgrade is yours, with
  `journal plugin upgrade <name> --yes`. When a new plugin would help, propose it:
  `journal plugin propose <folder or git address> --why "<what for>"` shows the user a card with all it would run.
- Never write into `.journal/plugins`: an installed plugin's files are the user's to change. A plugin's own folder,
  when the user asks you to work on it, is yours to change; the journal switches the plugin off until the user has
  read the change.
- Writing a plugin: docs/plugins.md describes all of it, the manifest, the line in and the line out.
