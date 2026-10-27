"""scripts/splitter_check.py and the corpus extractor on made-up lines: a line keeps its ID across runs with no stored map, the gaps between the splitter's parts may hold only space, separators, continuations and comments, and no corpus file is ever written inside the repository but under .journal."""

from pathlib import Path

import pytest

from scripts.corpus_commands import refused_inside_repository
from scripts.splitter_check import content_id, gap_faults

REPOSITORY = Path(__file__).resolve().parents[1]


def test_a_line_keeps_its_readable_id_on_every_run_with_no_stored_map():
    first, again, other = content_id("git status && git diff"), content_id("git status && git diff"), content_id("git status")
    assert first == again != other and len(first) == 19 and first.count("-") == 3, first


def test_only_space_separators_continuations_and_comments_lie_between_parts():
    assert gap_faults("cd x\n# a comment\nawk a; \\\nls && b &") == []
    assert gap_faults("echo a; echo b") == []


def test_no_corpus_file_is_written_inside_the_repository():
    with pytest.raises(SystemExit, match="never enters the repository"):
        refused_inside_repository(REPOSITORY / "tests" / "corpus.txt")
    refused_inside_repository(REPOSITORY / ".journal" / "corpus" / "commands.txt")
