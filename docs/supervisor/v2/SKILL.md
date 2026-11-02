# Supervisor version 2

Use the version 2 grant for the current environment and its watched plans. Read the command tier from `src/journal/features/supervisor/capability_catalogue.py`; do not invent or copy a second tier list.

- Read commands are always allowed.
- Tier 1 and tier 2 commands follow the saved grant decision and scope.
- Tier 3 commands default to On and Propose. The owner's Control decision for that verb may refuse it, leave it Propose only, or permit it to Act.
- A `never` command, including changing the supervisor's own grant, is always refused.
- Apply narrowing rules at the command check. They may refuse or require a proposal, never widen a grant.
- Send actions through the journal command funnel and wait for readback and a receipt. Never report an action complete from a tool acknowledgement alone.
- Keep proposals pending for the owner's decision. Owner feedback is context for later wakes, not authorization.
- An owner may undo an applied tier 1 action only while the rows still match the receipt's after values; the undo itself uses the command funnel and owner actor.

Journal-side behavior is implemented and covered by stories. Live deployment, operator migration and a live smoke run remain open.
