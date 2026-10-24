---
name: ImportsAtTheTop
description: Load it before writing an import, or when an import inside a function is flagged, so every module is loaded at boot and no cycle is hidden in a body.
summary: Every import sits at the top of its module; a cycle is broken by moving what both sides need into a module of its own, never by importing inside a function.
tier: mandatory
languages: [python]
---

# Imports at the top

The server builds its whole graph at boot, so the first hook, command or page after a boot pays nothing extra. An
import inside a function breaks that: its module is loaded on the first call, in the middle of a request. And it
is almost always there to hide a cycle: a feature's file imports its listeners and commands, and one of them imports
the feature back for its options.

## The rule

- Every import sits at the top of its module, never in a function or method.
- A cycle is a design fault, so fix the design: move what both modules need (a feature's options, a constant, a
  small value class) into a module of its own that both import; or hand the value in through the constructor.
- Never break a cycle by moving the import into a body, under `if TYPE_CHECKING`, or behind a string type.

## Example

Bad, in `worker_runner.py`:

```python
def minutes(self) -> float:
    from journal.features.workers.feature import Workers
    return self.settings.decimal(Workers.TIMEOUT)
```

Good: the option lives in `features/workers/worker_options.py`, which both `feature.py` and `worker_runner.py`
import at the top.

```python
from journal.features.workers.worker_options import WorkerOptions

def minutes(self) -> float:
    return self.settings.decimal(WorkerOptions.TIMEOUT)
```
