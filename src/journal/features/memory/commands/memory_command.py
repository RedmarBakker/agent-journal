from argparse import Namespace
from datetime import datetime, timezone

from journal.console.command import Command
from journal.engine.clock import Clock
from journal.features.memory.support.threshold_decisions import ThresholdDecisions
from journal.models.memory import HEAVIEST, LOWEST_WEIGHT, Memory
from journal.repositories.memories import Memories
from journal.support.caller import Caller
from journal.support.rejection import Rejection


class MemoryCommand(Command):
    """journal memory add, weigh, list, remove and skip: the agent's memories, each with a weight every compaction lowers by one, and the word that nothing needs keeping at a mark."""

    noun = "memory"

    def __init__(self, memories: Memories, decisions: ThresholdDecisions, clock: Clock) -> None:
        self.memories, self.decisions, self.clock = memories, decisions, clock

    def arguments(self, verbs) -> None:
        adding = self.verb(verbs, "add", "add something to keep in mind, in one or two plain sentences")
        adding.add_argument("text")
        adding.add_argument("--weight", type=int, default=5, help="how much it matters, 1 to 10; every compaction lowers it by one")
        adding.add_argument("--keywords", default="", help="words that bring it back when you write one, comma-separated")
        weighing = self.verb(verbs, "weigh", "give memories new weights: weigh 3,7,9 5,8,2 gives each its own, weigh 3,7,9 5 gives all one")
        weighing.add_argument("numbers")
        weighing.add_argument("weights")
        self.verb(verbs, "list", "every memory still shown, with its number and weight, heaviest first")
        self.verb(verbs, "remove", "take out memories that are no longer true: remove 3,7").add_argument("numbers")
        self.verb(verbs, "skip", "say why nothing needs keeping at this mark").add_argument("why")

    def add(self, args: Namespace, caller: Caller) -> int:
        keywords = tuple(word.strip().lower() for word in args.keywords.split(",") if word.strip())
        memory = self.memories.save(Memory(text=args.text, keywords=keywords).weighed(self.weight(str(args.weight))), caller.actor)
        self.decisions.decided(caller)
        print(f"memory {memory.id} added, weight {memory.weight}: {memory.text}")
        return 0

    def weigh(self, args: Namespace, caller: Caller) -> int:
        memories = self.found(args.numbers)
        weights = [self.weight(text) for text in args.weights.split(",")]
        if len(weights) not in (1, len(memories)):
            raise Rejection(f"{len(memories)} memories and {len(weights)} weights: give one weight for all, or one for each")
        weighed = [self.memories.save(memory.reweighed(weight), caller.actor) for memory, weight in zip(memories, weights * len(memories) if len(weights) == 1 else weights)]
        self.decisions.decided(caller)
        print(", ".join(f"memory {memory.id} weighs {memory.weight}" for memory in weighed))
        return 0

    def list(self, args: Namespace, caller: Caller) -> int:
        for memory in self.memories.shown():
            print(f"{memory.id:>4}  weight {memory.weight:>2}  {memory.text}")
        return 0

    def remove(self, args: Namespace, caller: Caller) -> int:
        removal_time = datetime.fromtimestamp(self.clock.time(), timezone.utc)
        removed = [self.memories.save(memory.removed(removal_time), caller.actor) for memory in self.found(args.numbers)]
        self.decisions.decided(caller)
        print(f"removed: memory {', '.join(str(memory.id) for memory in removed)}")
        return 0

    def skip(self, args: Namespace, caller: Caller) -> int:
        self.decisions.decided(caller)
        print("noted; carry on")
        return 0

    def found(self, text: str) -> list[Memory]:
        numbers = [self.number(word) for word in text.split(",")]
        if len(set(numbers)) != len(numbers):
            raise Rejection(f"{text} has a memory twice: write each number once")
        memories = self.memories.numbered(numbers)
        unknown = sorted(set(numbers) - {memory.id for memory in memories})
        if unknown:
            raise Rejection(f"no memory {', '.join(map(str, unknown))} here: `journal memory list` lists them")
        return memories

    @staticmethod
    def number(word: str) -> int:
        if not word.strip().isdigit():
            raise Rejection(f"{word.strip() or 'an empty place'} is not a memory's number: name them as 3,7,9")
        return int(word)

    @staticmethod
    def weight(word: str) -> int:
        if not word.strip().isdigit() or not LOWEST_WEIGHT <= int(word) <= HEAVIEST:
            raise Rejection(f"a weight is a whole number from {LOWEST_WEIGHT} to {HEAVIEST}, not {word.strip()}")
        return int(word)
