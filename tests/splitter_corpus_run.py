# Runs the splitter check over the whole local command corpus as a process for about five minutes, so it is not in the default run: python3 -m pytest -q tests/splitter_corpus_run.py, after a change to Chain; it is skipped where no corpus was extracted.
"""Chain splits every line of the local command corpus as shfmt counts its statements, with nothing but separators between its parts."""
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / ".journal" / "corpus"
RUN_SECONDS = 900


@pytest.mark.skipif(not (CORPUS / "commands.txt").exists(), reason="no command corpus was extracted here")
def test_no_line_of_the_command_corpus_is_split_wrongly(tmp_path):
    report = tmp_path / "report.txt"
    arguments = [CORPUS / "commands.txt", "--report", report]
    subprocess.run(["python3", "-m", "scripts.splitter_check", *map(str, arguments)], cwd=ROOT, env={**os.environ, "PYTHONPATH": "src"}, check=True, timeout=RUN_SECONDS)
    assert " 0 suspect" in report.read_text(), report.read_text()[:2000]
