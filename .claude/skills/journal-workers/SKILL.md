---
name: journal-workers
description: Send a worker to write a bounded job and wait for its report; load it before dispatching one
---

# Workers

A subagent only reads. A worker writes one bounded job and reports it, with a worktree of its own when it changes code.

For plans, read journal-plans. The main agent starts and oversees them. With Plan agents enabled, each started plan has its own Plan agent. In organization plan mode, it coordinates Domain agents and Roles; in solo plan mode, it takes Roles one at a time. A Role contract supplies the work's instructions and access.

- Queue related tasks to one worker so it reports once, at the end of its queue.
- A worker reports, and its tests run, only once no task of its queue is left, so a queue interrupts you once.
- Dispatch or send it the first task, then queue it the rest with `journal worker queue <n> <task> [<task>...]`.
- A queued task is delegated to that worker at once, never offered to you or blocked; releasing the worker opens it again.
- When a worker's work is merged you are given the next task in its queue with the line that sends it.
- A dispatch or a send of a single task while other tasks of its plan wait is told once to queue them.
- Prefer one worker for a whole approved plan, or one phase of it: `--plan <n>` or `--plan <n> --phase <k>` in place of `--task`
  queues its open tasks in order, delegates the plan, and the worker tests as the plan's testing template says
  and reports once, at the plan's or phase's end or where it cannot go on.
- Dispatch with `journal worker dispatch "<Name>" --task <n> --changes "<what it changes>" --profile journal-senior|journal-medior
  ["<more to tell it>"] [--provider claude|codex] [--worktree --libraries <a,b> | --copies <a,b> | --no-libraries]`:
  `journal worker dispatch "Lady Lovelace" --task 12 --changes "src/footer.py, tests/test_footer.py" --profile journal-medior --worktree --libraries .venv`.
- Name a worker after a distinguished figure with a twist on their trade.
- In organization dispatch, use `--role <domain/role>` so the Role contract supplies the job's guidance, tools and model. When no organization Role is being used, `--profile journal-medior` is for a defined implementation job and `--profile journal-senior` is for broad design judgement.
- A worker writes, and `--changes` names what; a job that only reads, searches, researches or reviews is a subagent's.
- A worker is started only on a task, an open one with a brief or the one you own, and the task is its own until merged or released.
- The profile sets its model and instructions; `--model` overrides it.
- How a worker tests is the setting How workers test. With The journal runs them, the default, it names its tests at
  clock-out with `--tests "<arguments>"` and the journal runs them in its worktree, a card in your chat showing the run;
  only a passing run lets the clock-out stand, and a failing one goes straight back to the worker.
- No worker is sent until the test command is set: `journal tests command "<command>" --proof "<the arguments of one passing test>"`.
- With Hand the tests over it runs none and its proofs name them for you; with Run the tests it wrote, `--tests` names the
  test template (`journal template list`), Scoped tests when not named and Full suite seldom: the full suite is yours.
- In a project with repositories of its own, a worktree holds one for each repository the brief names, all when it names none; each merges into its own.
- A worktree has no installed libraries: `--libraries node_modules,.venv` links the main checkout's, `--copies vendor` copies them, `--no-libraries` gives none.
- Always copy composer's vendor: through a link its autoloader would run the main checkout's code.
- The settings workers.preparation_commands, workers.completion_commands and workers.worktree_step hold the project's commands around a worktree's creation.
- A worker clocks in, keeps its own `journal todo` list, proves each point of the brief with `journal proof <point>
  "<file:line, and the test>"` (or `--not-done` and why) and clocks out with one report.
- At clock-out the journal commits a worker's work, asks the plugins, rebases it and runs its tests; a hold or a failing test goes back to the worker.
- You are told when a worker clocks in and once when its work is ready to check; your stops name what waits.
- A worker, a reviewer, a verifier and a subagent each run only the journal verbs their helper file in src/journal/helpers/
  names, and hear only what it allows; any other verb is refused, naming the file.
- `journal worker wait <n> [<n>...]` waits until they have clocked out; stopping is fine while you wait.
- Check each proof: read them with `journal task show <task>`, then `journal worker check <n> <point>`.
- Send a short proof back with `journal worker check <n> <point> --short "<what is missing>"`, to the same worker on the same task.
- Take the work in with `journal worker merge <n>` once every point is checked; nothing else adds a worker's work.
- A merge runs in the background with its card, step 1/5 to 5/5, while the plugins judge it; wait on its output as on any command.
- A worker whose run ends without clocking out still owns its task: send it again with `journal worker send <n>`.
- `journal worker release <n>` releases its task, refused while tasks it completed wait for the merge unless `--drop`.
- A worker that runs past 60 minutes is stopped and its report says so (setting workers.timeout_minutes, 0 for no limit).
- Send related work to the worker that knows it: `journal worker send <n> "<next job>"` keeps its session, memory and worktree.
- Never dispatch a new worker for work one already out has done part of.
- `--model <model>` or `--profile <profile>` on a send moves it to another model: stronger after three send-backs, cheaper for a settled shape.
- `journal worker list` shows every worker and the subagents you started: state, task, model, spend and send-backs.
- A worker with a task still queued clocks out of each task, which waits for the merge, and goes straight on to the
  next in its queue in the same session, with no test run and telling you nothing.
- Proving the last point of a task hands a queued worker the next.
- A queued worker reports, and its tests run, once no task is left; a blocked task next in its queue or a point proved
  not done ends the queue there.
- Check a finished task's points with `journal worker check <n> <point> --task <task>`; one merge takes every completed task in,
  refused while any point is unchecked.
- A worker still running takes a word with `journal worker notify <n> "<text>"`.
- Only a running Claude worker has a session inbox; notify to any other is refused with what to use instead.
- A dispatch whose brief names files an idle worker touched is refused, naming its send line; `--fresh` only when the job needs a new worker.
- Once a profile has workers.idle_kept workers out or idle (8, 0 for no limit), its dispatch is refused while one is idle.
- A reviewer always starts new.
- `journal worker complete <n>` or `journal worker stop <n>` of an idle worker first asks whether it could be reused; `--why "<reason>"` retires it.
- A worker out silent for 20 minutes is named to you once.
- A worker lists its dispatcher's other workers with `journal worker peers` and reaches one with notify or send; never
  itself, a retired one or another agent's workers.
- A subagent job on files an idle subagent of the same kind read is refused, naming its SendMessage line.
- `journal subagent retire <n>` releases a subagent from the count of those running at once (workers.most_subagents).
