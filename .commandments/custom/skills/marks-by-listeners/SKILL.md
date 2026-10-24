---
name: MarksByListeners
description: Load it before writing a chat mark, or when a call to a card writer outside a listener is flagged, so every mark is written where its event happens.
summary: A chat mark is written only by a listener on the event the change raises, never by a command handler, a controller, a job, a support class or the engine.
tier: mandatory
languages: [python]
---

# Marks by listeners

Every bubble the chat shows is a message, written where its event happens. A card writer (`MomentCards.show`,
`ProcessCards.show`, `show_fields`, `show_recent`) called from a command handler, a controller, a job or a support
class writes a mark that the event never announced: a second path to the same mark appears the day another command
raises the same change.

## The rule

- A call to a card writer sits only in a listener under `features/<feature>/listeners`.
- A command or support class changes the row, and the row names its event with `with_event`; the repository
  dispatches it on save.
- The listener hears that event and writes the mark. When no event exists for the change, add one in `events/`.

## Example

Bad, in a command handler:

```python
self.cards.show(self.scope.id, caller.agent_session, "Agent stuck", "warn", "bad", args.why, shows=CardKind.IMPASSE)
```

Good: the command saves the row, `ImpasseReported` rides on it, and `ImpasseCards` in
`features/tasks/listeners/` writes the mark.

```python
class ImpasseCards(Listener[ImpasseReported]):
    def handle(self, event: ImpasseReported) -> None:
        self.cards.show(event.environment_id, event.session, "Agent stuck", "warn", "bad", event.why, shows=CardKind.IMPASSE)
```
