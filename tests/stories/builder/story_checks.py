from tests.stories.builder.step_checks import HOOK_DURATION
from journal.features.shell.support.output_view import OutputView
import json
import re
import time
from enum import Enum

from journal.engine.nudge import Nudge
from journal.support.typed_lines import JOURNAL_PREFIX
from journal.events.moments.plugin_update_available import PluginUpdateAvailable
from journal.repositories.entries import Entries
from journal.repositories.links import Links
from journal.repositories.messages import Messages
from journal.repositories.organization_handoffs import OrganizationHandoffs
from journal.repositories.reports import Reports
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers as WorkerRows
from journal.repositories.plans import Plans
from journal.repositories.rigs import Rigs
from journal.repositories.domain_rows import DomainRows
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.rig_seats import DOMAIN_AGENT, PLAN_AGENT, PLAN_POD
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.providers.providers import Providers
from journal.support.caller import ACTOR_TOKEN, ORGANIZATION_RIG, ORGANIZATION_SEAT
from journal.models.support.ref import Ref
from journal.support.time_source import TimeSource
from tests.full_project import MAIN
from tests.in_process import get_answer
from tests.stories.builder.story_agent import StoryAgent
from journal.features.workers.feature import Workers
from tests.stories.builder.mode_floor import ModeFloor


# the duration a hook's answer shows the user, such as "PreToolUse: 12 ms"


class StoryChecks:
    """The checks a story makes on what its last step brought: what the agent was told, by registry key and values, whether the hook let it through, whether the command passed, the stack and the rows, read through the API; a failing check says what was lines instead and the stack."""

    def told_number(self, nudge: Nudge, name: str) -> int:
        return int(next(line.values[name] for line in reversed(self.said) if line.key == nudge.key))

    def expect_one_entry_of_firing(self, firing: str) -> None:
        with self.app.container.get(Scope).environment(1):
            entries = self.app.container.get(Entries)
            count = entries.counted(entries.query().filter(idempotency=f"hook:{self.scoped_session()}:PreToolUse:{firing}"))
        assert count == 1, f"firing {firing} has {count} entries, not one"

    def expect_newest_message_text(self, text: str) -> None:
        newest = self.api_row("messages", self.newest("messages"))
        assert newest["text"] == text, f"the newest message reads {newest['text']!r}, not {text!r}"

    def expect_recent_message_text(self, text: str, within: int = 5) -> None:
        newest = self.newest("messages")
        reads = [self.api_row("messages", n)["text"] for n in range(newest, max(newest - within, 0), -1)]
        assert text in reads, f"none of the newest {within} messages reads {text!r}: {reads}"

    def expect_no_new_output(self) -> None:
        assert not self.shell_outputs, f"the command kept output {self.newest_output()}"

    def expect_new_output(self) -> None:
        assert self.shell_outputs, "the command kept no output"

    def expect_output_count(self, count: int) -> None:
        assert self.output_count() == count, f"{self.output_count()} outputs are kept, not {count}"

    def expect_chat_marks(self, shows: str, *texts: str) -> None:
        rows = [row for row in get_answer(self.app, "/journal/messages", MAIN)[1]["rows"] if (row.get("data") or {}).get("shows") == shows]
        marks = sorted(row["text"] for row in rows)
        assert marks == sorted(texts), f"the chat's {shows} marks are {marks}, not {sorted(texts)}: {rows}"

    @staticmethod
    def is_shown_docked(data: dict, now: float) -> bool:
        return bool(data.get("docked")) and not (data.get("undock_at") and not data.get("held_at") and now >= data["undock_at"])

    def expect_docked_cards(self, *texts: str) -> None:
        now = self.app.container.get(TimeSource).seconds()
        docked = sorted(row["text"] for row in get_answer(self.app, "/journal/messages?docked=1", MAIN)[1]["rows"] if self.is_shown_docked(row.get("data") or {}, now))
        assert docked == sorted(texts), f"the cards docked above the chat are {docked}, not {sorted(texts)}"

    def expect_plan_titles_in(self, environment: str, *titles: str) -> None:
        shown = sorted(row["title"] for row in get_answer(self.app, "/journal/plans", {"X-Journal-Env": environment})[1]["rows"])
        assert shown == sorted(titles), f"the plans of {environment} are {shown}, not {sorted(titles)}"

    def expect_dispatch_card(self, **data) -> None:
        cards = [row.get("data") or {} for row in get_answer(self.app, "/journal/messages", MAIN)[1]["rows"] if (row.get("data") or {}).get("dispatch")]
        fields = {name: cards[-1].get(name) for name in data} if cards else {}
        assert fields == data, f"the subagent's dispatch card holds {fields}, not {data}"

    def expect_card(self, n: int, **data) -> None:
        shown = self.api_row("messages", n).get("data") or {}
        fields = {name: shown.get(name) for name in data}
        assert fields == data, f"card {n} holds {fields}, not {data}"

    def run_cards(self, output: int) -> list[dict]:
        return [row for row in get_answer(self.app, "/journal/messages", MAIN)[1]["rows"] if (row.get("data") or {}).get("key") == OutputView.key(output)]

    def expect_run_card_titled(self, output: int, title: str) -> None:
        titles = [row.get("text") for row in self.run_cards(output)]
        assert titles[-1:] == [title], f"the card of output {output} is titled {titles}, not {title!r}"

    def expect_run_card_saying(self, output: int, line: str) -> None:
        cards = self.run_cards(output)
        data = (cards[-1].get("data") or {}) if cards else {}
        assert line in (data.get("detail"), *data.get("lines", ())), f"the card of output {output} holds {data}, not the line {line!r}"

    def expect_project_file(self, path: str, *parts: str) -> None:
        file = self.app.config.root / path
        text = file.read_text() if file.is_file() else ""
        missing = [part for part in parts if part not in text]
        assert file.is_file() and not missing, f"{path} does not hold {missing}: {text[:400]!r}"

    def expect_runtime_file(self, name: str, text: str) -> None:
        file = self.app.config.home / "runtime" / name
        shown = file.read_text() if file.is_file() else ""
        assert shown == text, f"runtime/{name} holds {shown!r}, not {text!r}"

    def expect_project_file_without(self, path: str, part: str) -> None:
        text = (self.app.config.root / path).read_text()
        assert part not in text, f"{path} still holds {part!r}"

    def expect_no_project_file(self, path: str) -> None:
        assert not (self.app.config.root / path).exists(), f"{path} is still in the project"

    def expect_project_file_holds(self, path: str, data: bytes) -> None:
        assert (self.app.config.root / path).read_bytes() == data, f"{path} does not hold the bytes it was published with"

    def expect_project_file_is(self, path: str, text: str) -> None:
        assert (self.app.config.root / path).read_text() == text, f"{path} changed"

    def expect_typed(self, *nudges: Nudge) -> None:
        typed = self.typed[self.typed_from:]
        lines = [f"{JOURNAL_PREFIX} {nudge.rendered()}" for nudge in nudges]
        assert typed == lines, f"the terminal was to be typed {lines} since the story or its fixture began, and only that; typed {typed}"

    def expect_agent_told(self, agent: StoryAgent, nudge: Nudge, **values) -> None:
        session = self.session_of(agent)
        lines = self.log.environment_lines(self.session_environments.get(session, "main"))
        assert any(line.session == session and line.matches(nudge.key, values) for line in lines), f"{session} was not told {nudge.key} {values}: {lines}"

    def expect_typed_nudge(self, nudge: Nudge, count: int = 1, **values) -> None:
        self.expect_typed_text(nudge.cut(nudge.create(**values).rendered()) if values else nudge.title.partition("{{")[0], count)

    def expect_typed_text(self, part: str, count: int = 1) -> None:
        typed = " ".join(line.removeprefix(f"{JOURNAL_PREFIX} ") for line in self.typed[self.typed_from:])
        assert typed.count(part) == count, f"the terminal was to be typed {part!r} {count} times since the story or its fixture began; typed {typed!r}"

    def expect_typed_last(self, line: str) -> None:
        last = self.typed[-1] if self.typed else ""
        assert last == line, f"the last line typed into the agent's terminal is {last!r}, not {line!r}"

    def expect_stack(self, agent: StoryAgent, *states: type) -> None:
        stack = self.session_stack(self.session_of(agent))
        assert stack == [self.floor().name if state is ModeFloor else state.name for state in states], f"the stack of the {agent.role} is {stack}; told {[line.key for line in self.said]}"
        self.stack_checked_at = len(self.path)

    def expect_agent_session_in_environment(self, agent: StoryAgent, environment: str) -> None:
        session = self.session_of(agent)
        headers = {**MAIN, "X-Journal-Env": environment}
        rows = get_answer(self.app, "/journal/agents", headers)[1]["rows"]
        assert any(row.get("session") == session for row in rows), f"{session} has no agent row in {environment}"

    def expect_task_in(self, environment: str, n: int, state: str) -> None:
        states = self.task_states_in(environment)
        assert states.get(n) == state, f"task {n} in {environment} is {states.get(n)}, not {state}"

    def expect_task_not_in(self, environment: str, n: int) -> None:
        assert n not in self.task_numbers_in(environment), f"task {n} is still in {environment}"

    def expect_message(self, n: int, **fields) -> None:
        self.expect_row("messages", n, fields)

    def expect_message_buttons(self, n: int, buttons: list[dict]) -> None:
        shown = self.api_row("messages", n).get("data", {}).get("buttons", [])
        assert shown == buttons, f"message {n} carries the buttons {shown}, not {buttons}"

    def expect_newest_message(self, n: int) -> None:
        assert self.newest("messages") == n, f"the newest message is {self.newest('messages')}, not {n}: another was sent"

    def expect_no_hook_duration(self) -> None:
        assert not HOOK_DURATION.search(self.last_step.user_line()), f"the hook's answer shows a duration though the setting is off: {self.last_step.user_line()}"

    def expect_last_answer_carries(self, nudge: Nudge, **values) -> None:
        line = nudge.cut(nudge.create(**values).rendered())
        assert line in self.last_step.agent_text(), f"the last hook's answer does not carry {nudge.key}: {self.last_step.agent_text()!r}"

    def expect_answer_text(self, part: str) -> None:
        assert part in self.last_step.agent_text(), f"the last hook's answer does not carry {part!r}: {self.last_step.agent_text()!r}"

    def expect_last_answer_lines_in_order(self, *nudges: Nudge) -> None:
        places = [self.last_step.agent_text().find(nudge.cut(nudge.rendered())) for nudge in nudges]
        assert -1 not in places and places == sorted(places), f"the last hook's answer does not carry {[nudge.key for nudge in nudges]} in that order: {self.last_step.agent_text()!r}"

    def expect_last_answer_without(self, nudge: Nudge, **values) -> None:
        line = nudge.cut(nudge.create(**values).rendered())
        assert line not in self.last_step.agent_text(), f"the last hook's answer carries {nudge.key}: {self.last_step.agent_text()!r}"

    def expect_plugin_version(self, n: int, version: str) -> None:
        shown = self.api_row("plugins", n)["manifest"]["version"]
        assert shown == version, f"plugin {n} is at version {shown}, not {version}"

    def expect_plugin_update_offered(self, plugin: str, previous: str, version: str) -> None:
        title = PluginUpdateAvailable(environment_id=0, plugin=plugin, previous=f"v{previous}", tag=f"v{version}").card_parts()[0]
        texts = [row["text"] for row in get_answer(self.app, "/journal/messages", MAIN)[1]["rows"]]
        assert title in texts, f"no card offers the update: {texts[-5:]}"

    def expect_search_result_rows(self, n: int, *rows: str) -> None:
        results = (self.api_row("messages", n).get("data") or {}).get("results", [])
        assert [result["row"] for result in results] == list(rows), f"the search mark {n} opens {results}, not {list(rows)}"

    def expect_card_data(self, n: int, **fields) -> None:
        data = self.api_row("messages", n).get("data") or {}
        card_fields = {name: data.get(name) for name in fields}
        assert card_fields == fields, f"the card of message {n} holds {card_fields}, not {fields}"

    def expect_newest_agent_message(self, text: str) -> None:
        agent_rows = [row for row in get_answer(self.app, "/journal/messages", MAIN)[1]["rows"] if row.get("author") == "agent"]
        newest = max(agent_rows, key=lambda row: row["id"]) if agent_rows else {}
        assert newest.get("text") == text, f"the agent's newest message is {newest.get('text')!r}, not {text!r}"

    def expect_worker_chat_after_its_job(self, worker: StoryAgent, *turns: tuple[str, str]) -> None:
        rows = sorted(get_answer(self.app, f"/journal/chats/{self.session_of(worker)}", MAIN)[1]["rows"], key=lambda row: row["id"])
        chat, expected = [(row["author"], row["text"]) for row in rows], [("user", self.api_row("workers", worker.number)["brief"]), *turns]
        assert chat == expected, f"the worker's chat holds {chat}, not {expected}"

    def expect_plugin_given(self, plugin: str, variable: str, is_given: bool) -> None:
        given = json.loads((self.app.config.home / "plugin-data" / plugin / "environment.json").read_text())
        assert (variable in given) is is_given, f"plugin {plugin}'s program was {'not ' if is_given else ''}given {variable}"

    def expect_chat_holds(self, text: str) -> None:
        texts = [row["text"] for row in get_answer(self.app, "/journal/messages", MAIN)[1]["rows"]]
        assert text in texts, f"the chat holds no message {text!r}: {texts}"

    def expect_agent_messages(self, count: int) -> None:
        agent_messages = [row for row in get_answer(self.app, "/journal/messages", MAIN)[1]["rows"] if row.get("author") == "agent"]
        assert len(agent_messages) == count, f"the chat holds {len(agent_messages)} messages of the agent, not {count}"

    def expect_setting(self, option, value: object) -> None:
        stored = self.setting(option)
        assert stored == value, f"{option.key} is {stored!r}, not {value!r}"

    def expect_task_count(self, count: int) -> None:
        self.expect_row_count("tasks", count)

    def expect_plan_count(self, count: int) -> None:
        self.expect_row_count("plans", count)

    def expect_question_count(self, count: int) -> None:
        self.expect_row_count("questions", count)

    def expect_change_told_to_the_viewer(self, table: str, n: int) -> None:
        changes = get_answer(self.app, "/journal/entries?since=0", MAIN)[1]
        assert (table, n) in [(change["data"].get("table"), change["data"].get("id")) for change in changes], f"no change of {table} {n} told to the viewer"

    def expect_row_count(self, table: str, count: int) -> None:
        rows = get_answer(self.app, f"/journal/{table}", MAIN)[1]["rows"]
        assert len(rows) == count, f"{len(rows)} {table} through the API, not {count}"

    def expect_task(self, n: int, **fields) -> None:
        self.expect_row("tasks", n, fields)

    def expect_task_unheld(self, n: int) -> None:
        tasks = self.app.container.get(Tasks)
        task = tasks.global_matching(id=n)[0]
        with self.app.container.get(Scope).environment(task.environment_id):
            holder = tasks.holder(task)
        assert holder is None, f"task {n} is held by {holder}, not open plan work"

    def expect_task_tied_to_domain(self, task: int, domain: str) -> None:
        with self.app.container.get(Scope).environment(1):
            names = self.app.container.get(DomainRows).domain_names(self.app.container.get(Tasks).find(task))
        assert names == [domain], f"task {task} is tied to {names}, expected {domain}"

    def expect_organization_handoff_pending(self, plan_id: int, task_id: int, target: str) -> None:
        plan = self.app.container.get(Plans).global_matching(id=plan_id)[0]
        with self.app.container.get(Scope).environment(plan.environment_id):
            handoffs = self.app.container.get(OrganizationHandoffs).pending(target)
        assert any(row_plan.id == plan_id and row_task.id == task_id for _, row_plan, row_task in handoffs), \
            f"plan {plan_id} task {task_id} is not unread in {target}'s inbox: {handoffs}"

    def expect_plan_rig(self, plan_id: int, name: str) -> None:
        with self.app.container.get(Scope).environment(1):
            plans = self.app.container.get(Plans)
            rig = self.app.container.get(Rigs).find(plans.rig_id(plans.find(plan_id)))
        assert rig.name == name, f"plan {plan_id} uses rig {rig.name}, not {name}"

    def expect_plan_rig_seat_settings(self, rig: str) -> None:
        runtime = self.app.container.get(SeatRuntime)
        spec = runtime.read_spec(rig)
        for pod in spec["pods"]:
            for member in pod["members"]:
                agent = member["agent_ref"].removeprefix("local:agents/")
                agent_path = runtime.spec_folder(rig) / "agents" / agent / "agent.yaml"
                description = json.loads(agent_path.read_text())["description"]
                prefix = "The journal's "
                assert description.startswith(prefix), f"{agent} has no generated organization identity: {description!r}"
                identity = description.removeprefix(prefix)
                environment = member["env"]
                assert environment.get(ORGANIZATION_SEAT) == identity, f"{pod['id']}.{member['id']} has organization identity {environment.get(ORGANIZATION_SEAT)!r}, not {identity!r}"
                assert environment.get(ORGANIZATION_RIG) == rig, f"{pod['id']}.{member['id']} has organization rig {environment.get(ORGANIZATION_RIG)!r}, not {rig!r}"

    def expect_plan_seat_journal_reads_allowed(self, rig: str) -> None:
        runtime = self.app.container.get(SeatRuntime)
        spec = runtime.read_spec(rig)
        pod = next(value for value in spec["pods"] if value["id"] == PLAN_POD)
        member = next(value for value in pod["members"] if value["id"] == PLAN_AGENT)
        provider = self.app.container.get(Providers).lookup(self.provider)
        permissions = member[provider.openrig_permissions_field]
        if provider.openrig_permissions_field == "claude_permissions":
            assert "Bash(journal *)" in permissions["allow"], "the Plan seat's journal commands need approval"
        else:
            assert permissions["approval"] == "never", "the Plan seat's journal commands need approval"

    def expect_openrig_seat_received(self, agent: StoryAgent, rig: str, seat: str, text: str) -> None:
        member = self.app.container.get(SeatRuntime).organization_member(rig, seat, self.provider)
        messages = [message for target, message in self.simulated_seats().messages if target == member.target]
        assert text in messages, f"OpenRig seat {member.logical_id} for {agent.session} received {messages}, not {text!r}"

    def expect_openrig_seat_environment(self, agent: StoryAgent, seat: str) -> None:
        member = self.organization_seat_member(seat)
        environment = self.openrig_organization_seat_environment(seat)
        session = self.simulated_seats().sessions[member.target]["sessionId"]
        agent_session = self.session_of(agent)
        assert session == agent_session, f"{seat} session {session} does not match {agent_session}"
        assert environment.get(ORGANIZATION_SEAT) == seat, f"{seat} session has organization identity {environment.get(ORGANIZATION_SEAT)!r}"
        assert environment.get(ORGANIZATION_RIG) == member.rig, f"{seat} session has organization rig {environment.get(ORGANIZATION_RIG)!r}"
        assert environment.get(ACTOR_TOKEN) == member.token, f"{seat} session has no actor token from its generated member"
        assert environment.get("JOURNAL_ENV") == member.environment, f"{seat} session has journal environment {environment.get('JOURNAL_ENV')!r}"
        assert environment.get("JOURNAL_ROOT") == str(self.app.config.root), f"{seat} session has journal root {environment.get('JOURNAL_ROOT')!r}"

    def expect_organization_seat_routing_guidance(self, rig: str) -> None:
        agents = self.app.config.home / "runtime" / "rigs" / rig / "agents"
        spec = self.app.container.get(SeatRuntime).read_spec(rig)
        contracts = self.app.container.get(Organization).contracts()
        for pod in spec["pods"]:
            for member in pod["members"]:
                agent = member["agent_ref"].removeprefix("local:agents/")
                folder = agents / agent
                guidance = (folder / "guidance" / "role.md").read_text()
                skill = (folder / "skills" / "journal-organization-seat-routing" / "SKILL.md").read_text()
                agent_spec = json.loads((folder / "agent.yaml").read_text())
                identity = agent_spec["description"].removeprefix("The journal's ")
                skills = agent_spec["profiles"]["default"]["uses"]["skills"]
                assert "journal-organization-seat-routing" in skills, f"{agent} does not load its routing skill"
                instructions = (
                    "journal organization handoff",
                    "journal organization inbox",
                    "only route between seats",
                    "do not use `rig send` or `rig queue`",
                )
                for instruction in instructions:
                    assert instruction in guidance, f"{agent} guidance does not say {instruction!r}"
                    assert instruction in skill, f"{agent} routing skill does not say {instruction!r}"
                if member["id"] == PLAN_AGENT:
                    assert "journal task show" in guidance, "the Plan seat guidance does not name task show for its plan tasks"
                    assert "journal task show" in skill, "the Plan seat routing skill does not name task show for its plan tasks"
                elif member["id"] == DOMAIN_AGENT:
                    assert "`journal organization handoff <task> plan`" in guidance, "the Domain seat guidance does not give the Plan return route"
                    domain_steps = (
                        "As the Domain seat, read your inbox with `journal organization inbox`, then hand each task to one of your Roles",
                        "`journal organization handoff <task> role:<domain>/<role>`",
                        "wait for a journal handoff",
                        "do not ask the operator for task details",
                    )
                    for step in domain_steps:
                        assert step in guidance, f"the Domain seat guidance does not say {step!r}"
                        assert step in skill, f"the Domain seat routing skill does not say {step!r}"
                else:
                    domain_route = f"`journal organization handoff <task> domain:{pod['id']}`"
                    assert domain_route not in guidance, f"{agent} guidance tells a Role to hand off its task"
                    assert domain_route not in skill, f"{agent} routing skill tells a Role to hand off its task"
                    role = contracts.role(identity.split("/", 1)[1])
                    if role and role.writes:
                        role_steps = (
                            "As a writing Role seat, read your inbox with `journal organization inbox`, then clock in on your assigned task",
                            "`journal clock-in`",
                            "`journal proof <point> \"<file:line, and the test that shows it>\"`",
                            "`journal clock-out \"<report>\"`",
                            "Clocking out returns your work to the Domain agent for checking",
                        )
                        for step in role_steps:
                            assert step in guidance, f"{agent} guidance does not say {step!r}"
                            assert step in skill, f"{agent} routing skill does not say {step!r}"
                    else:
                        assert "clock in on your assigned task" not in guidance, f"read-only Role seat {agent} is told to clock in"

    def expect_worker_role_job(self, worker: StoryAgent, task: int, brief: str, stale_brief: str) -> None:
        with self.app.container.get(Scope).environment(1):
            row = self.app.container.get(WorkerRows).find(worker.number)
            task_row = self.app.container.get(Tasks).find(task)
            holder = self.app.container.get(Tasks).holder(task_row)
        assert row.role == "builder" and row.plan_id, f"worker {row.id} is not a plan Builder Role job: {row}"
        assert holder == Ref.build(row), f"task {task} is held by {holder}, not Role worker {row.id}"
        assert brief in row.brief and brief in task_row.brief, f"worker {row.id} has not received task {task}'s brief {task_row.brief!r}: {row.brief!r}"
        assert stale_brief not in row.brief, f"worker {row.id} received an old brief for task {task}: {row.brief!r}"

    def expect_role_job_prompt(self, worker: StoryAgent, brief: str, stale_brief: str, *parts: str) -> None:
        with self.app.container.get(Scope).environment(1):
            row = self.app.container.get(WorkerRows).find(worker.number)
        role = self.app.container.get(Organization).at(row.contract).role(row.role)
        member = self.app.container.get(SeatRuntime).member(f"plan-{row.plan_id}", role.domain, role.id, row.provider)
        seats = self.simulated_seats()
        expected = (brief, *parts)
        deadline = time.monotonic() + 5
        received = [prompt for target, prompt in seats.messages if target == member.target]
        prompts = [prompt for prompt in received if all(part in prompt for part in expected)]
        while not prompts and time.monotonic() < deadline:
            time.sleep(0.01)
            received = [prompt for target, prompt in seats.messages if target == member.target]
            prompts = [prompt for prompt in received if all(part in prompt for part in expected)]
        prompt = prompts[-1] if prompts else ""
        assert prompt, f"Role seat {member.logical_id} never received worker {row.id}'s current job: {received}"
        assert stale_brief not in prompt, f"Role seat {member.logical_id} received an old brief: {prompt!r}"

    def expect_role_guidance_and_skills_omit(self, worker: StoryAgent, *job_text: str) -> None:
        with self.app.container.get(Scope).environment(1):
            row = self.app.container.get(WorkerRows).find(worker.number)
        role = self.app.container.get(Organization).at(row.contract).role(row.role)
        runtime = self.app.container.get(SeatRuntime)
        member = runtime.member(f"plan-{row.plan_id}", role.domain, role.id, row.provider)
        folder = runtime.spec_folder(member.rig) / "agents" / f"{member.pod}-{member.member}"
        guidance = folder / "guidance" / "role.md"
        skills = tuple((folder / "skills").rglob("SKILL.md"))
        assert guidance.is_file(), f"Role seat {member.logical_id} has no standing guidance"
        resources = (guidance, *skills)
        text = "\n".join(path.read_text() for path in resources)
        found = [part for part in job_text if part and part in text]
        assert not found, f"Role seat {member.logical_id} keeps job text in its guidance or skills: {found}"

    def expect_organization_domains(self, *expected: str) -> None:
        contracts = self.app.container.get(Organization).contracts()
        found = tuple(domain.id for domain in contracts.domains)
        assert found == expected, f"organization folder {contracts.folder} has domains {found}, expected {expected}; problems: {contracts.problems}"

    def expect_task_made_by(self, agent: StoryAgent, n: int) -> None:
        self.expect_row("tasks", n, {"creator": f"agent:{self.session_of(agent)}"})

    def expect_report_about_task(self, report: int, task: int) -> None:
        with self.app.container.get(Scope).environment(1):
            report_row = self.app.container.get(Reports).find(report)
            task_ref = Ref.build(self.app.container.get(Tasks).find(task))
            targets = self.app.container.get(Links).targets(report_row, Messages.SUBJECT_LINK)
        assert task_ref in targets, f"report {report} does not link to task {task}: {targets}"

    def expect_task_logged(self, n: int, part: str) -> None:
        shown = self.app.console().run(["task", "show", str(n)], self.agent).text
        assert part in shown, f"task {n} has no log line holding {part!r}: {shown}"

    def expect_worker(self, n: int, **fields) -> None:
        self.expect_row("workers", n, fields)

    def expect_plan(self, n: int, **fields) -> None:
        self.expect_row("plans", n, fields)

    def expect_row_absent(self, table: str, n: int) -> None:
        rows = get_answer(self.app, f"/journal/{table}?ids={n}", MAIN)[1]["rows"]
        assert not rows, f"{table} {n} is still listed through the API: {rows[0]}"

    def expect_row(self, table: str, n: int, fields: dict) -> None:
        row = self.api_row(table, n)
        expected_fields = {name: value.value if isinstance(value, Enum) else value for name, value in fields.items()}
        row_fields = {name: row.get(name) for name in expected_fields}
        assert row_fields == expected_fields, f"{table} {n} has {row_fields}, not {expected_fields}"

    def floor(self) -> type:
        return Workers.modes.states[self.mode]

    def expect_seconds_waited_with_work_open(self, seconds: int) -> None:
        agents = [row["id"] for row in get_answer(self.app, "/journal/agents", MAIN)[1]["rows"] if row.get("session") == self.scoped_session()]
        counted = sum(round(waited) for _, waited in self.api_row("agents", max(agents))["open_work_waits"])
        assert counted == seconds, f"the agent waited {counted} seconds with work open, not {seconds}"

    def stack(self) -> list[str]:
        return self.session_stack(self.scoped_session())

    def session_stack(self, session: str) -> list[str]:
        environment = self.session_environments.get(session, "main")
        headers = {**MAIN, "X-Journal-Env": environment}
        agents = [row for row in get_answer(self.app, "/journal/agents", headers)[1]["rows"] if row.get("session") == session]
        agent = max(agents, key=lambda row: row["id"]) if agents else None
        return [state["name"] for state in reversed(self.api_row("agents", agent["id"], headers)["stack"])] if agent else []

    def newest(self, table: str) -> int:
        return max((row["id"] for row in get_answer(self.app, f"/journal/{table}", MAIN)[1]["rows"]), default=0)

    def api_row(self, table: str, n: int, headers: dict = MAIN) -> dict:
        rows = get_answer(self.app, f"/journal/{table}?ids={n}", headers)[1]["rows"]
        assert rows, f"no {table} row {n} through the API"
        return rows[0]

    def account(self) -> str:
        return f"told {[(lines.session, lines.key, lines.values) for lines in self.said]}; stack {self.stack()}"

