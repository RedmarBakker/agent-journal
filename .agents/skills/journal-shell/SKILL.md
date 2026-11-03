---
name: journal-shell
description: Run shell commands through the journal: in parts, timed, and in the background past the limit; load it when a command moves to the background, or before reading an output or writing a reader or an alias
---

# Shell commands

Every shell command you run goes through the journal's runner.

- A line chained with `&&` or `;` is run part by part; each part is recorded with what it printed and how long it took,
  and a failing part stops the chain where the shell would have.
- A command that runs past fifteen seconds, or ten while a message of the user's is waiting, is moved to the background with
  the rest of its chain: the tool call returns with its output number, and you are informed when output N ends. Until you
  read it, by `journal output read N` or `status N`, it is named again every five tool uses, or after thirty idle seconds.
- A command whose whole output is under 400 characters, with no pipe in its line, prints as it is and is stored as no
  output. Any other command's output is stored as a numbered output, the newest 250 of them. `journal output read N` needs a flag
  naming the part: `--tail 20`, `--head 20`, `--grep "<words>"`, `--lines 100-160`, `--reader <name>`, `--summary` for
  how it ended with its first and last lines, or `--all` for every line when you need it in full. `journal output
  list` names the newest. `journal output status N` says in one line whether it is running, finished or failed with code C;
  without a number it names each of your background outputs with its status. Read an output this way, never by running the command again nor by reading its files raw.
- A reader reads outputs of one shape, such as a test run's failures: `journal reader add <name> --pattern <regex>
  --about "<what it picks>"`, or `--script <file>` for a shell script that receives the output on its input. Use it with
  `journal output read N --reader <name>`; `journal reader list` names the project's readers. The second time you
  read the same shape of output by hand, add a reader for it and say so in the chat.
- `journal output watch N [--reader <name>] [--title "<words>"]` attaches a running output to you: after every tool use you are
  shown the lines its reader picks, or its last ten lines with no reader, and a card in the chat shows the same, updated in
  place. The card is for the user: its title says what the run is doing in plain words, `--title "Running tests"`, else
  the reader's label, else what the command does; the command line shows only when the user opens the card. The
  watch ends by itself when the command ends, and you are informed once how it ended; `journal output unwatch` ends it
  sooner. One output is watched at a time. A reader written for a watch picks few lines that read well in the card, and
  may show how far the command has progressed: `--progress <regex>` takes the last match, its groups a percentage such as
  `\[(\d+)%\]` or a count of a total such as `(\d+)/(\d+)`, shown as a bar in the card, and `--label "<words>"` says what the run is doing, such as Running tests or Building the
  application, never a bare name such as Tests nor a half sentence that stops on of or the: a short, whole phrase in plain words in the user's own language that says what the run is doing, such as Running tests or Building the application; `--topic '<pattern>'`, read over the command line, adds what a run is about
  after the title, such as the test files or the -k a line names, for a command run with different arguments.
  A run over several suites, packages or shards shows its progress too: count what has finished against the total and print it as N/M on each line that finishes one, such as each test against the number the run will run, as a suite run in shards counts every shard's finished tests; give the reader --progress '(\d+)/(\d+)' and a --label that is a short, whole phrase in plain words in the user's own language that says what the run is doing, such as Running tests or Building the application. A bar that counts suites or packages says little when each runs many tests: count the tests.
  `--finished '<pattern>'` and `--failed '<pattern>'` pick other lines once the command finished or failed, such as its summary
  `--summary '<pattern>'` is the summary reader: the last match in the output, its groups joined, is the summary the card shows when opened, such as '(\d+ failed), (\d+ passed)'
  or its failures; a script reader finds which in JOURNAL_OUTPUT_STAGE: running, finished or failed.
- A reader names the commands whose output it reads, `--commands "pytest"`, and a command moved to the background that
  runs one is instructed to watch it with that reader, so one reader serves every later run. When a run moved to the
  background ends and no reader reads it, a test run, a build, an install or a long process, or a command whose output you
  read by hand twice, the line naming its end says once `no reader reads <part> yet` with a `journal reader add` filled
  from that run's output: the starting reader of its kind and the lines it saw. The add tries it on the stored runs and
  refuses it naming what it missed, such as the counts of a passing or a failing run, or a --progress that matches no line;
  fix what it names and add it again. A reader the journal made on its own reads the run at once and the user sees a card
  for it: keep it, or write your own over it. The journal ships readers for pytest, dotnet test and phpunit
  or pest in .journal/readers as examples. A wait on a command given `--reader <name>`
  (the tasks skill) watches it too, so the user sees it progress while you wait.
- A test run, a build or any other command's output is shown in full up to 400 characters; past that you see only a
  line naming the output to read by its number, with its lines, its characters and the part of the line it belongs to. A command that reads (cat, grep, sed, git diff) is shown up to 8,000
  characters, past that by its two ends. A line of journal commands is shown in full and stored as no output.
- A command that only reads or edits the project's own code, a file, a folder or a glob under the project and outside .journal, runs as written, pipes and all,
  in the shell itself: nothing of it is captured, recorded or stored, and `grep -n x src/app.py | tail -5` answers at once. Any other command's trailing output shapers, `| tail`, `| head`, `| grep`, `| cut`, `| sort`, `| uniq`, `| wc`, `| sed -n`, `| awk`, `| jq` and the like, are removed from the line: the command runs in full, the
  whole output is stored under its number, and your cut is applied to it and shown before the one line naming the
  number, so the lines you asked for come back and the rest stays readable.
- An alias names a command line of the project: `journal alias add <name> "<line>" [--reader <name>] [--about "<what
  it does>"] [--env KEY=VALUE]`, then `journal <name> [args]` runs the line with the args at its end, recorded as your
  own command. A run that moves to the background is watched at once through the alias's reader, so the user sees it
  progress. `journal alias list` names them, `journal alias edit <name> [--line] [--reader] [--about]` changes one and
  `journal alias remove <name>` removes it; a name that is a journal command or an alias already is refused. The
  user types the same `journal <name>` in a terminal, and a plugin may ship aliases with their readers. An alias chains
  with other commands like any command. A line an alias runs, typed by hand, refuses the whole tool use with the alias,
  and so does an alias run whose line a more specific alias runs; a reader of the project never reads a plugin's alias,
  and one that would is deleted when the alias runs. A line you run three times or more with no alias for it is asked
  once to become one, with the reader that reads it.
- A test suite is a long runner: run it on its own and chain the commit after its result in a second call.
- A journal command runs on its own, or chained only with other journal commands; chained with anything else it is
  refused, since it would move to the background with the rest and its answer would be lost. A journal command stays in
  the foreground, but for the few that name themselves background commands, such as `journal worker merge`, which go to
  the background at once with their card and their own reader, streaming their lines as they print them.
- While the journal waits to restart until the commands running now end, a command that would go to the background at
  once (a merge, a test run, a build) is refused, since the restart would cut it off: run it again once the journal is back.
