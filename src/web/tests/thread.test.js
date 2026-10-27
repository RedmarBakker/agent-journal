import {describe, expect, test} from "vitest";
import {mainChat, threadTurns} from "../src/domain/thread.js";

const at = (seconds) => new Date(seconds * 1000).toISOString();
const message = (id, seconds, fields = {}) => ({table: "messages", id, created_at: at(seconds), author: "user", text: "", files: [], data: {}, comments_on: [], idempotency: "", ...fields});
const pending = (key, seconds, fields = {}) => ({table: "messages", id: 0, key: `pending:${key}`, pending: true, created_at: at(seconds), author: "user", text: "", files: [], idempotency: key, ...fields});
const card = (id, seconds, data, text = "") => message(id, seconds, {author: "system", text, data});
const turns = (messages, pend = [], older = false) => threadTurns(messages, pend, older).turns;
const keys = (list) => list.map((t) => t.key);

describe("a message just sent", () => {
    test("shows once while only the placeholder exists", () => {
        expect(keys(turns([], [pending("a", 10)]))).toEqual(["pending:a"]);
    });

    test("is replaced by the real message with the same key, never shown twice", () => {
        const got = threadTurns([message(5, 10, {idempotency: "a"})], [pending("a", 10)]);
        expect(keys(got.turns)).toEqual(["messages:5"]);
        expect(got.keys.get("messages:5")).toBe("pending:a");
    });

    test("without a key it is matched by its words, and not when the message is older than the placeholder", () => {
        const words = {text: "hello", idempotency: ""};
        const near = turns([message(5, 7, words)], [pending("a", 10, words)]);
        const far = turns([message(5, 1, words)], [pending("a", 10, words)]);
        expect(near.map((t) => t.id)).toEqual([5]);
        expect(far.map((t) => t.id).sort()).toEqual([0, 5]);
    });

    test("stays a placeholder until its files have arrived", () => {
        const waiting = pending("a", 10, {files: ["a.txt", "b.txt"]});
        expect(turns([message(5, 10, {idempotency: "a", files: ["a.txt"]})], [waiting]).map((t) => t.id)).toEqual([0]);
        expect(turns([message(5, 10, {idempotency: "a", files: ["a.txt", "b.txt"]})], [waiting]).map((t) => t.id)).toEqual([5]);
    });
});

describe("who said it", () => {
    test("the user's and the agent's words are messages, a thought is a thought, and a message under a row is a comment", () => {
        const got = turns([message(1, 1), message(2, 2, {author: "agent"}), message(3, 3, {author: "agent", data: {kind: "thought"}}), message(4, 4, {comments_on: ["tasks:1"]})]);
        expect(got.map((t) => [t.kind, t.who])).toEqual([
            ["message", "user"],
            ["message", "agent"],
            ["thought", "agent"],
            ["comment", "user"],
        ]);
    });
});

describe("the journal's cards", () => {
    test("a card draws its icon, tone and the row it opens, and a visitor's comment is one", () => {
        const visitor = card(4, 6, {kind: "card", icon: "chat", tone: "", detail: "hi", row: "docs:1", visitor: "Ann"}, "Ann commented on docs:1 through a shared link");
        const [got] = turns([visitor]);
        expect([got.kind, got.data.icon, got.data.row, got.data.visitor, got.data.label]).toEqual(["card", "chat", "docs:1", "Ann", "Ann commented on docs:1 through a shared link"]);
    });

    test("a question card carries its options and its answer", () => {
        const [got] = turns([card(2, 2, {kind: "question", row: "questions:7", options: ["a", "b"], answer: "b"}, "Which?")]);
        expect(got.kind).toBe("question");
        expect(got.question).toMatchObject({id: 7, options: ["a", "b"], answer: "b"});
    });

    test("a compaction is its own turn", () => {
        expect(turns([card(1, 5, {kind: "compacted"})])[0].kind).toBe("compacted");
    });
});

describe("folding runs", () => {
    const loads = (n) => Array.from({length: n}, (_, i) => card(i + 1, 10 + i, {kind: "skill", detail: `s${i}`}));

    test("two skill loads stay single, three fold into one group", () => {
        expect(turns(loads(2))).toHaveLength(2);
        const folded = turns(loads(3));
        expect(folded).toHaveLength(1);
        expect(folded[0]).toMatchObject({kind: "group", title: "3 skills loaded"});
        expect(folded[0].turns).toHaveLength(3);
    });

    test("a group of the same card counts the settled ones", () => {
        const sin = (i, settled) => card(i + 1, 10 + i, {kind: "card", icon: "warn", tone: settled ? "good" : "warn"}, "Sin found");
        const cards = [sin(0, "fixed"), sin(1, "fixed"), sin(2), sin(3), sin(4)];
        const folded = turns(cards);
        expect(folded[0]).toMatchObject({kind: "group", title: "5 × Sin found"});
    });

    test("a different turn in the middle ends the run", () => {
        const got = turns([...loads(2), message(9, 11.5, {text: "hm"}), ...loads(4).slice(2).map((m) => ({...m, id: m.id + 20}))]);
        expect(got.map((t) => t.kind)).toEqual(["skill", "skill", "message", "skill", "skill"]);
    });
});

describe("marks of one family", () => {
    const registry = {
        groups: [],
        families: [
            {key: "tasks", title: "Task moves"},
            {key: "memories", title: "Memory changes"},
        ],
        kinds: [
            {key: "task_moves", family: "tasks", group: "work", turns: [], messages: [], covers: [], shown: true},
            {key: "memories", family: "memories", group: "reminders", turns: [], messages: [], covers: [], shown: true},
        ],
    };
    const move = (id, seconds, label = `Task ${id} started`) => card(id, seconds, {kind: "card", shows: "task_moves"}, label);
    const memory = (id, seconds) => card(id, seconds, {kind: "card", shows: "memories"}, `Fact ${id} saved`);
    const said = (id, seconds) => message(id, seconds, {text: "go on"});

    test("three of one family standing together fold into one group mark naming the family and its count of updates, never a count of rows made, and one worker's marks fold by the worker", async () => {
        const {store} = await import("../src/state/store.js");
        store.spec = {marks: registry};
        const [group] = turns([move(1, 1, "Task 1 started"), move(2, 2, "Task 2 completed"), move(3, 3, "Task 3 paused")]);
        expect([group.kind, group.title, group.turns.map((t) => t.id)]).toEqual(["group", "Task moves: 3 updates", [1, 2, 3]]);
        const worker = (id, seconds) => card(id, seconds, {kind: "card", worker: "Mr. Eames", shows: "task_moves"}, `step ${id}`);
        expect(turns([worker(4, 4), worker(5, 5), worker(6, 6)])[0].title).toBe("Mr. Eames: 3 events");
        store.spec = null;
    });

    test("a mark arriving after a bubble stays apart, of the same family or another", async () => {
        const {store} = await import("../src/state/store.js");
        store.spec = {marks: registry};
        const got = turns([move(1, 1), move(2, 2), move(3, 3), said(4, 4), memory(5, 5), move(6, 6)]);
        expect(got.map((t) => (t.kind === "group" ? t.title : t.id))).toEqual(["Task moves: 3 updates", 4, 5, 6]);
        store.spec = null;
    });
});

describe("one subagent's actions", () => {
    const made = (id, seconds, n) => card(id, seconds, {kind: "made", shows: "created", row: `reports:${n}`, run: "subagent:s1:agent-7", step: 0, run_title: "Subagent journal-researcher", run_noun: "actions", run_mark: "subagent"}, `Created report ${n} by subagent journal-researcher`);

    test("fold into one group named for the subagent, counting its actions", () => {
        const got = turns([made(1, 1, 1), made(2, 2, 2), made(3, 3, 3)]);
        expect(got.map((t) => (t.kind === "group" ? t.title : t.id))).toEqual(["Subagent journal-researcher: 3 actions"]);
        expect(got[0].data.markIcon).toBe("subagent");
    });
});

describe("a sequence run's steps", () => {
    const step = (id, seconds, n) => card(id, seconds, {kind: "card", shows: "sequence_steps", row: "sequences:5", run: "5@2026-10-27T10:00:00", step: n, run_title: "Sequence 5, Review"}, `Sequence 5, Review: moved on to step ${n + 1}`);
    const said = (id, seconds) => message(id, seconds, {text: "go on"});

    test("a step arriving late and out of order joins its run's group near the foot in step order, and the group says it has news", () => {
        const got = turns([step(1, 1, 0), step(2, 2, 1), said(3, 3), step(4, 4, 3), said(5, 5), step(6, 6, 2)]);
        expect(got.map((t) => (t.kind === "group" ? t.title : t.id))).toEqual(["Sequence 5, Review: 4 steps", 3, 5]);
        expect(got[0].turns.map((t) => t.data.step)).toEqual([0, 1, 2, 3]);
        expect(got[0].data.news).toBe(2);
    });

    test("a step whose run's marks are past ten bubbles starts a continued group at the foot, naming and opening the earlier one", () => {
        const bubbles = Array.from({length: 10}, (_, i) => said(10 + i, 10 + i));
        const got = turns([step(1, 1, 0), step(2, 2, 1), step(3, 3, 2), ...bubbles, step(30, 30, 3)]);
        const [earlier, last] = [got[0], got.at(-1)];
        expect([earlier.title, earlier.turns.length]).toEqual(["Sequence 5, Review: 3 steps", 3]);
        expect([last.kind, last.title, last.turns.map((t) => t.data.step), last.data.continues]).toEqual(["group", "Sequence 5, Review, continued", [3], earlier.key]);
        expect(got).toHaveLength(12);
    });
});

describe("a group mark", () => {
    test("shows the steps that joined it since it was last opened, and a continued part opens the part it continues", async () => {
        window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
        const {createApp, h, nextTick} = await import("vue");
        const {store} = await import("../src/state/store.js");
        const {default: TurnGroup} = await import("../src/chat/TurnGroup.vue");
        const step = (id, n) => ({key: `messages:${id}`, kind: "card", id, time: id, data: {label: `step ${n}`, step: n}});
        const group = {key: "group:messages:30", kind: "group", time: 9, title: "Sequence 5, Review, continued", icon: "list", data: {news: 2, continues: "group:messages:1", markIcon: "sequence"}, turns: [step(30, 3)]};
        const host = document.body.appendChild(document.createElement("div"));
        const earlier = document.body.appendChild(document.createElement("div"));
        earlier.dataset.ref = "group:messages:1";
        earlier.scrollIntoView = () => {};
        const app = createApp({render: () => h(TurnGroup, {turn: group})});
        app.provide("scope", {env: "", api: {}, rows: () => [], loaded: () => true});
        app.directive("tip", {});
        app.mount(host);
        await nextTick();
        expect(host.querySelector(".mark .news").textContent).toBe("2 new");
        host.querySelector(".mact").click();
        expect(store.focus).toBe("group:messages:1");
        host.querySelector(".mark").click();
        await nextTick();
        expect(host.querySelector(".mark .news")).toBeNull();
        app.unmount();
        host.remove();
        earlier.remove();
    });
});

describe("older turns", () => {
    test("when paging back, no card older than the oldest message loaded is shown", () => {
        const got = turns([message(1, 50), message(2, 60), card(3, 10, {kind: "skill", detail: "old"}), card(4, 55, {kind: "skill", detail: "new"})], [], true);
        expect(got.map((t) => t.id)).toEqual([1, 4, 2]);
    });
});

describe("a message from another session", () => {
    test("is a message bubble naming the session that sent it, with its words", () => {
        const [turn] = turns([card(7, 10, {kind: "peer", peer: "Coco"}, "the report is ready")]);
        expect(turn.kind).toBe("message");
        expect(turn.data.peer).toBe("Coco");
        expect(turn.text).toBe("the report is ready");
    });
});

describe("a reminder whispered to the agent", () => {
    test("is a mark with its words, never an empty one", () => {
        const [turn] = turns([card(9, 10, {kind: "whisper", icon: "rules", row: "reminders:2"}, "Reminded the agent about reminder 2")]);
        expect(turn.kind).toBe("whisper");
        expect(turn.title).toBe("Reminded the agent about reminder 2");
    });
});

describe("a suggestion", () => {
    test("is a turn of its own, with its row, words and the answer it came to", () => {
        const data = {kind: "suggestion", row: "suggestions:3", detail: "As the journal's plugin it runs inside the journal.", accept: "Install it as a plugin", answer: ""};
        const [turn] = turns([card(9, 10, data, "Run it as a journal plugin instead?")]);
        expect(turn.kind).toBe("suggestion");
        expect(turn.suggestion).toEqual({id: 3, title: "Run it as a journal plugin instead?", detail: data.detail, accept: "Install it as a plugin", answer: ""});
    });
});

describe("the Show in chat switches", () => {
    test("hide each card by the kind it names, a reminder's whisper under Reminders and never under Rules", () => {
        const command = card(1, 10, {kind: "card", icon: "terminal", shows: "commands"}, "Moved to the background: testing");
        const fact = card(2, 11, {kind: "whisper", row: "reminders:4", shows: "reminders"}, "Reminded the agent about reminder 4");
        const step = card(3, 12, {kind: "card", icon: "list", shows: "sequence_steps"}, "Sequence 1: moved on to step 2");
        const shown = (hidden) => threadTurns([command, fact, step], [], false, hidden).turns.map((t) => t.id);
        expect(shown([])).toEqual([1, 2, 3]);
        expect(shown(["commands"])).toEqual([2, 3]);
        expect(shown(["rules"])).toEqual([1, 2, 3]);
        expect(shown(["reminders", "sequence_steps"])).toEqual([1]);
    });
});

describe("the two chats", () => {
    test("the main chat leaves out a worker's and a subagent's messages, which its own chat keeps", () => {
        const rows = [message(1, 1, {thread: "main", text: "Fix the footer"}), message(2, 2, {author: "agent", thread: "workers:1", session: "w1", text: "On it"}), message(3, 3, {author: "agent", thread: "subagents:9", session: "s9", text: "Found it"}), message(4, 4, {author: "agent", thread: "main", text: "Done"})];
        expect(keys(turns(mainChat(rows)))).toEqual(["messages:1", "messages:4"]);
        expect(keys(turns(rows.filter((m) => m.session === "w1")))).toEqual(["messages:2"]);
    });
});

describe("a new message", () => {
    test("adds one turn and leaves every other the very turn it was, so nothing else is drawn again", () => {
        const held = [message(1, 1), message(2, 2, {author: "agent"}), card(3, 3, {kind: "card", icon: "chat", tone: "", detail: "x", row: "docs:1"}, "A card")];
        const before = turns(held);
        const after = turns([...held, message(4, 4)]);
        expect(after).toHaveLength(before.length + 1);
        before.forEach((turn, i) => expect(after[i]).toBe(turn));
    });

    test("a message that changed is a new turn, and the rest are still the turns they were", () => {
        const held = [message(1, 1), message(2, 2)];
        const before = turns(held);
        const after = turns([held[0], {...held[1], text: "edited"}]);
        expect(after[0]).toBe(before[0]);
        expect(after[1]).not.toBe(before[1]);
    });
});

describe("what was created from a message", () => {
    test("is one line under the user's message, never a mark of its own nor a copy under the reply", () => {
        const receipt = card(9, 12, {kind: "card", key: "filed:5", shows: "filed", row: "tasks:3721"}, "Created task 3721 from your message");
        const got = turns([message(5, 10, {filed: [3721]}), message(6, 11, {author: "agent", reply_target: 5, filed: [3721]}), receipt]);
        expect(got.map((t) => t.key)).toEqual(["messages:5", "messages:6"]);
        expect(got[0].receipt).toBe("Created task 3721 from your message");
        expect(got[1].receipt).toBeUndefined();
    });
});
