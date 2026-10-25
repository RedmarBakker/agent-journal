class ShardDeal:
    """Deals tests to shards by the seconds each took last time, longest first to the shard with the least so far, so every shard ends near the same moment; a test with no recorded time counts as the average, and with no times at all the tests go round the shards in turn."""

    def __init__(self, seconds: dict[str, float]) -> None:
        self.seconds = seconds

    def shards(self, names: list[str], count: int) -> list[list[str]]:
        if not self.seconds:
            return [names[index::count] for index in range(count)]
        average = sum(self.seconds.values()) / len(self.seconds)
        loads, dealt = [0.0] * count, [[] for _ in range(count)]
        for name in sorted(names, key=lambda name: (-self.seconds.get(name, average), name)):
            lightest = loads.index(min(loads))
            dealt[lightest].append(name)
            loads[lightest] += self.seconds.get(name, average)
        return dealt
