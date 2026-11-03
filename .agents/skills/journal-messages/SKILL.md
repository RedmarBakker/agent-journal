---
name: journal-messages
description: Read and answer the user's messages and ask the user questions; read at the start of every session, with the journal and etiquette skills
---

# Messages

The user sends messages; you answer them before anything else.

- Read a message whole: `journal message read N` on its own; a read piped into head, tail or grep is refused.
- The journal names a message by its number, never its text: `new message 4`, `new messages 4, 5, 6`, or past three
  `7 messages unread: journal message unread`.
- `journal message read N` shows one and marks it read; `journal message unread` shows every unread one and marks them read.
- Answer each message at once, before the work it led to, because you were asked.
- Reply with `journal message send '<text>' --reply-to N`, single-quoted, then go on with the work in the same turn:
  `journal message send 'The footer now names the shop; it ships with the next release.' --reply-to 412`.
- Never write a reply as your turn's closing text: it ends the turn, so the work you meant to do next never happens.
- End a turn with the reply when you reply last: words after it in the same turn are not sent, and the stop says so.
- Every message read is steering, which you follow, or something to do, which you file as a task from it
  (the tasks skill), so the chat shows the task above the message.
- A comment on a document or report is neither: answer it and write what it asks into that document or report, as a
  change, a section or an open question; it becomes work only when the user asks for it.
- Write a number that names a row with its kind, task 3399 or plan 1032, so the chat links it.
- A message of yours with a number and no kind is pointed out once: fix it with `journal message amend-links <n> <kind>
  [<kind>...]`, the kinds in the order the numbers appear, or one kind for all.
- Acknowledge a message that needs nothing more ("ok", "thanks", "continue") with a reaction, not words:
  `journal message react N "👍"`, 🙏 for thanks; the same reaction again takes it off.
- Act on the user's reaction to a message when it asks for something, and never mention it.
- A turn of yours that is only a reaction is not posted.
- An unread inbox is named again every third tool use; after five reminders the next write waits until you read it.
- A message you read and leave unanswered holds your next tool call that is not a journal command or a look at its
  files: a word first, then the work. A reaction answers it too.
- `read due, message N: K` and `reply due, message N: K` count the tool uses K left before that wait.
- `journal message recent` shows the latest messages; after a compaction the overview, which the journal skill teaches,
  shows them among what is in flight.
- Name a picture in a message once you have looked: `journal message tag <n> <file> "<what it shows>"`.
- A turn that only answers a journal line and changes nothing stays out of the chat by itself.
- Say in the chat only what the user needs to know.
- `journal message list` shows the thread, unread ones marked with `*`.
- A message from another session's agent reaches the chat as that agent's: read it at once and act on it as steering.
- Answer another agent, with SendMessage to it, only when it asks a question, so two agents never answer each other endlessly.

## Questions

A choice only the user can make is asked as a question, not written into a reply.

- `journal question ask "<the question>" --options "a" "b" "c" --recommend "b"`, each choice quoted on its own so a comma stays inside it; you are then waiting, and stopping is fine.
- Give your recommendation whenever you have one: `--recommend` names it word for word as one of the options, and it is put first and marked for the user.
- Each option names who acts, the agent or the user, never I, we or you, which the reader cannot place.
- The answer arrives as a line naming `journal question show <n>`: read it there, in full, with the messages linked to it,
  and act on it. A reply from the user in the chat answers it too.
- `journal question list` shows what is open. Never offer choices in prose and continue; ask.

## Pins and buttons

- A pin is a note left on the user's desk: something ready that they must see when they come back hours later, after
  the chat has moved on, as a note someone left you: your pull request is ready, your design is ready. Pin it above the
  chat: `journal notice create "<what is ready>" --link "<url>" --label "Open the design"`. It stays until the user
  closes it.
- A button is an action for now: open this page, start this, send this form. It goes under your message
  (`journal message send` with `--button` or `--form-button`, the messages skill) and moves on with the chat.
- Something ready that the user also acts on now gets both: the button in the message, and the pin for when they
  come back.
- When the user must open a web address outside the journal, start something there or send a form to one, put a
  button under your message instead of asking them to visit it.
- Never build a page of your own just to hold a button.
- `--button 'Open the app settings|https://github.com/settings/apps|opens the settings in a new tab'` opens an address.
- `--form-button 'Create the app|<address>|sends the manifest to GitHub|manifest=<json>'` posts the hidden fields to it,
  as GitHub's app manifest flow takes one.
- A button's label says what happens, and its third part a line on it.
- Never a button for a journal row: task 12 or plan 3 written in the text is a link already.
