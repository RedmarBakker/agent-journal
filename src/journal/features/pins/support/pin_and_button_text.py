class PinAndButtonText:
    """What a pin is and what a button is, said in the same words by the pinned-links skill and the messages skill."""

    BULLETS = """- A pin is a note left on the user's desk: something ready that they must see when they come back hours later, after
  the chat has moved on, as a note someone left you: your pull request is ready, your design is ready. Pin it above the
  chat: `journal notice create "<what is ready>" --link "<url>" --label "Open the design"`. It stays until the user
  closes it.
- A button is an action for now: open this page, start this, send this form. It goes under your message
  (`journal message send` with `--button` or `--form-button`, the messages skill) and moves on with the chat.
- Something ready that the user also acts on now gets both: the button in the message, and the pin for when they
  come back.
"""
