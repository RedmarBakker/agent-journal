"""Splits the lines of the command corpus with the journal's own Chain and lists the lines it may split wrongly, by the check that caught them, leaving out the lines already decided as split right; a full run writes the failing lines' IDs, and a run with --failing checks only those, so the list is drained before the next full run. Builds nothing else. Run from the repository: PYTHONPATH=src python3 -m scripts.splitter_check <corpus> --decided <file> --report <file> [--failing <file>] [--only-failing]."""

import argparse
import multiprocessing
import time
from collections import Counter, defaultdict
from pathlib import Path

from journal.support.chain import Chain
from scripts.corpus_forms import LINE_ID, splitter_faults, staged

WORKERS = 4
CHUNK_LINES = 500
SAMPLE_LINES = 20


def corpus_lines(corpus: Path, only: set[str] | None):
    with corpus.open(errors="replace") as lines:
        for raw in lines:
            raw = raw.rstrip("\n")
            found = LINE_ID.match(raw)
            line_id = found.group(1) if found else ""
            if raw and (only is None or line_id in only):
                yield line_id, raw[found.end():] if found else raw


def line_faults(entry: tuple[str, str]) -> tuple[str, str, list[str]]:
    line_id, line = entry
    text = line.replace("\\n", "\n")
    chained = Chain.chained(text)
    return line_id, line, splitter_faults(text, chained, staged(chained))


def decided_lines(path: Path | None) -> set[str]:
    return {row.split("\t")[0] for row in path.read_text().splitlines() if row.strip()} if path and path.is_file() else set()


def report(faults: dict[str, list[tuple[str, str]]], checked: int, seconds: float) -> str:
    counts = Counter({check: len(found) for check, found in faults.items()})
    head = [f"{checked} lines checked in {seconds:.0f} s; {sum(counts.values())} suspect by check:", *(f"  {check}: {count}" for check, count in counts.most_common()), ""]
    body = [f"== {check} ({len(found)}) ==\n" + "\n".join(f"{line_id}\t{reason}\t{line[:300]}" for line_id, reason, line in found[:SAMPLE_LINES]) for check, found in sorted(faults.items(), key=lambda item: -len(item[1]))]
    return "\n".join(head + body) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--decided", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--failing", type=Path, default=None, help="the file of failing line IDs: written by a full run, read with --only-failing")
    parser.add_argument("--only-failing", action="store_true", help="check only the lines the last full run found failing")
    args = parser.parse_args()
    only = decided_lines(args.failing) if args.only_failing else None
    decided, began, checked = decided_lines(args.decided), time.monotonic(), 0
    faults: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    with multiprocessing.Pool(WORKERS) as pool:
        for line_id, line, found in pool.imap(line_faults, corpus_lines(args.corpus, only), chunksize=CHUNK_LINES):
            checked += 1
            if line_id in decided:
                continue
            for reason in found:
                faults[reason.split(":")[0]].append((line_id, reason, line))
    text = report(faults, checked, time.monotonic() - began)
    if args.failing:
        failing_ids = sorted({line_id for found in faults.values() for line_id, _, _ in found})
        args.failing.write_text("".join(f"{line_id}\n" for line_id in failing_ids))
    if args.report:
        args.report.write_text(text)
    print(text.split("\n\n")[0])


if __name__ == "__main__":
    main()
