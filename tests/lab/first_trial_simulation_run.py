# Runs the four paired null batches through process workers, so it is not in the default run: journal tests turn tests/lab/first_trial_simulation_run.py::test_first_trial_null_batches_write_inconclusive_records

import json
from pathlib import Path

from tests.lab.__main__ import main
from tests.lab.network_reading import NETWORK_METRICS
from tests.lab.run_reading import RUN_METRICS


SOURCE_COMMIT = "9066fc238e9cf5249e38610a089eea0802b5ecf1"
LAB_HOME = Path("/tmp/journal-lab-task204-simulator")


def test_first_trial_null_batches_write_inconclusive_records(capsys):
    result = main([
        "simulate-first-trials",
        "--source-commit",
        SOURCE_COMMIT,
        "--lab-home",
        str(LAB_HOME),
    ])

    assert result == 0
    paths = tuple(Path(line) for line in capsys.readouterr().out.splitlines())
    assert len(paths) == 4
    for summary_path in paths:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        records = tuple(json.loads(line) for line in Path(summary["run_records"]).read_text(encoding="utf-8").splitlines())
        assert summary["mode"] == "simulated_only"
        assert "does not execute agent work" in summary["model_scope"]
        assert summary["decision"] == "inconclusive"
        assert summary["run_count"] == len(records) == 18
        assert summary["paired_units"] == 9
        assert len(summary["per_business_type"]) == 3
        assert all(item["paired_units"] == item["primary_pairs_replayed_equal"] == 3 for item in summary["per_business_type"])
        assert all(record["simulated"] is True and record["provider"] == "VoidProvider" for record in records)
        assert all(record["reading"]["measurements"][RUN_METRICS.index("cost_dollars")]["measurement"]["value"] == 0.0 for record in records)
        assert all(len(record["network"]["measurements"]) == len(NETWORK_METRICS) for record in records)
