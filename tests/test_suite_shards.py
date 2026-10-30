import importlib.util
import sys
from pathlib import Path

from tests.service_memory import ServiceMemory
from tests.shard_deal import ShardDeal


def suite_script(name: str = "suite"):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / "scripts" / f"{name}.py")
    suite = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(suite)
    return suite


def test_shards_are_dealt_longest_first_so_they_end_together_and_go_round_without_times():
    seconds = {"long": 30.0, "mid": 20.0, "a": 10.0, "b": 10.0, "c": 5.0, "d": 5.0}
    shards = ShardDeal(seconds).shards(["a", "b", "c", "d", "long", "mid", "new"], 2)
    loads = [sum(seconds.get(name, 13.3) for name in shard) for shard in shards]
    assert sorted(name for shard in shards for name in shard) == ["a", "b", "c", "d", "long", "mid", "new"], "every test is in one shard"
    assert abs(loads[0] - loads[1]) <= 13.3, "no shard ends a whole long test after the other"
    assert "long" in shards[0] and "mid" in shards[1], "the longest test starts a shard of its own"
    assert ShardDeal({}).shards(["a", "b", "c"], 2) == [["a", "c"], ["b"]], "with no times the tests go round"


def test_a_shards_count_never_drops_when_a_printed_line_lands_in_its_line_of_dots(tmp_path):
    suite = suite_script()
    output = tmp_path / "shard.out"
    output.write_text("collected 9 items\n....")
    assert suite.shard_progress(output) == (4, 9)
    output.write_text("collected 9 items\n....no supervisor hosts this journal, so these services are off: sync\n..F  [ 77%]\n")
    assert suite.shard_progress(output) == (7, 9), "the dots before a printed line still count"
    output.write_text("collected 9 items\n.........  [100%]\nE       assert False\nF\n")
    assert suite.shard_progress(output) == (9, 9), "an assertion line of a failure's report is no result"


def test_the_suite_takes_fewer_shards_when_little_memory_is_free_and_reads_free_memory_on_macos_and_linux():
    suite = suite_script()
    shard = suite.SHARD_BYTES
    assert suite.shard_count(100 * shard) == suite.core_shards(), "with memory to spare the cores decide"
    assert suite.shard_count(3 * shard) == min(3, suite.core_shards()) and suite.shard_count(shard // 2) == 1, "with little free, as many shards as fit, never none"
    vm_stat = "Mach Virtual Memory Statistics: (page size of 16384 bytes)\nPages free:      10.\nPages active:   99.\nPages inactive:  20.\nPages speculative: 2.\n"
    assert suite.vm_stat_available(vm_stat) == 16384 * 32, "macOS: the free, inactive and speculative pages"
    assert suite.meminfo_available("MemTotal:  1000 kB\nMemAvailable:   512 kB\n") == 512 * 1024, "Linux: MemAvailable"
    assert "only 600 MB of memory is free" in suite.memory_line(2, 600 * 2**20), "the run says why it took fewer"


class Turn:
    def __init__(self) -> None:
        self.count = 0


class Tracker:
    def __init__(self) -> None:
        self.turns = {"main": Turn()}
        self.lines = {"main": ["read"]}
        self.agents = (Turn(),)


def test_a_service_put_back_forgets_what_a_test_changed_inside_the_objects_and_lists_it_holds():
    tracker = Tracker()
    turn = tracker.turns["main"]
    memory = ServiceMemory([tracker])
    tracker.turns["main"].count = 3
    tracker.lines["main"].append("wrote")
    tracker.agents[0].count = 2
    tracker.turns["worker"] = Turn()
    memory.put_back()
    assert tracker.turns == {"main": turn} and turn.count == 0, "an object held in a dict is put back as it stood"
    assert tracker.lines == {"main": ["read"]}, "a list inside a dict is put back as it stood"
    assert tracker.agents[0].count == 0, "an object held in a tuple is put back as it stood"
    tracker.lines["main"].append("wrote again")
    memory.put_back()
    assert tracker.lines == {"main": ["read"]}, "a second put back still has what was taken, never what the last test changed"
