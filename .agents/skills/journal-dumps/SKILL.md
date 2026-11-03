---
name: journal-dumps
description: File what the user dropped in a dump: sort the material by subject into rows of their own; load it when a dump arrives
---

# Dumps

A dump holds pasted text and dropped files; each is an item. Sort the material by subject: one document per subject,
named for what it is about, never after the file it was received in. One dump is worked at a time; the next waits until it closes.

1. `journal dump items <n>` lists the status of every item.
2. Read each item, then `journal dump note <n> <item> "<what it is>"`.
3. Write what it becomes (a doc, a plan, a task), then
   `journal dump filed <n> <item> "<what it did>" --refs "doc:2, plans:1" --added "doc:3"` (`--added` names rows you wrote
   without being asked, also listed in refs), or `journal dump failed <n> <item> "<why>"`. What you file is in the journal at once.
4. `journal dump name <n> "<name>"` names the dump for what its items are about; `journal dump log <n> "<status>"`
   (at most 40 characters, `--detail` for the sentence) shows the user what you are doing.
5. `journal dump split <n> "<part>, <part>"` splits pasted text into parts, one item each.
6. `journal dump ask <n> "<question>" --guesses "a|b"` asks the user in the dump window; they answer there.
   What the user writes in the dump reaches you as a message about it: answer with `journal dump reply <n> "<text>"`
   (at most 600 characters), never in the chat; the chat shows a small mark that you answered in the dump.
7. The dump closes by itself once every item is filed or failed. Then sum it up with
   `journal dump propose <n> '[{"ask": "Want me to plan the mobile layout?", "label": "Plan it"}]' --summary "<what you filed and where>"`
   (`'[]'` for no next step) and start nothing yourself.
8. Only the user stops, removes, or chooses a next step. `journal dump reopen <n>` works a closed dump again.
