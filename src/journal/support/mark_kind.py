from dataclasses import dataclass


@dataclass(frozen=True)
class MarkKind:
    """One kind of chat mark as Show in chat offers it, the unit shown or hidden: its label, the family it belongs to, whether it is one of the family's main marks or a detail of them, whether the chat shows it until the user hides it, the viewer's turn kinds and message kinds it covers, and the other kinds hiding it hides too."""

    key: str
    label: str
    family: str
    main: bool = True
    shown: bool = True
    turns: tuple[str, ...] = ()
    messages: tuple[str, ...] = ()
    covers: tuple[str, ...] = ()
