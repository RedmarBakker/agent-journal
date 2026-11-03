---
name: journal-pinned-links
description: Pin what the user must see on coming back and put a button under a message for an action now; load it when you point the user at a design, a page or anything else outside the journal
---

# Pinned links

A pin and a button are two different things.

- A pin is a note left on the user's desk: something ready that they must see when they come back hours later, after
  the chat has moved on, as a note someone left you: your pull request is ready, your design is ready. Pin it above the
  chat: `journal notice create "<what is ready>" --link "<url>" --label "Open the design"`. It stays until the user
  closes it.
- A button is an action for now: open this page, start this, send this form. It goes under your message
  (`journal message send` with `--button` or `--form-button`, the messages skill) and moves on with the chat.
- Something ready that the user also acts on now gets both: the button in the message, and the pin for when they
  come back.
A row of the journal you want to keep in view at the bottom of the chat, a plan or a task, is docked there with
`journal plan dock 12`, never pinned; only when the user asks for it pinned above the chat, pin it by its ref with
`--link plans:12 --user-asked`, its button opening the row in place. An outside address opens in a new tab.
A link in your chat text or in a command's output that no pin has, a pull request's address among them, is suggested
as a pin, and the same link again only after a number of your tool uses. The user closes a pin when done.

The same goes for what a subagent makes: when you dispatch one to produce something the user will open, tell it
to end its report with the link, and pin that the moment it reports, before you say anything else about its work.
