import {describe, expect, test} from "vitest";
import {orchestraOf, splitTask} from "../src/domain/orchestra.js";
import {store} from "../src/state/store.js";

describe("the name an agent's cell is titled with", () => {
    test("a subagent dispatched as 'Name: job' is titled with the name and keeps the job below", () => {
        expect(splitTask("Dr. Einstein: profile the slow hooks")).toEqual({name: "Dr. Einstein", job: "profile the slow hooks"});
        expect(splitTask("profile the slow hooks")).toEqual({name: "Subagent", job: "profile the slow hooks"});
    });

    test("a subagent is titled with its name and its Kind line says only subagent", () => {
        store.rows = {
            subagents: [
                {
                    table: "subagents",
                    id: 1,
                    dispatcher: "s7",
                    task: "Coco Rams: draw the plan card",
                    agent_type: "designer",
                    session: "s1",
                    state: "running",
                    started_at: 1,
                    ended_at: 0,
                    resumed_at: 0,
                },
            ],
        };
        const [cell] = orchestraOf({environments: []}, [], {id: 7, session: "s7"}, "main");
        expect(cell).toMatchObject({name: "Coco Rams", title: "draw the plan card", label: "Subagent", sub: true});
    });
});

describe("the title of a worker's cell", () => {
    test("it carries the worker's number as the chat words it, then its name", () => {
        store.rows = {};
        const workers = [
            {id: 1127, name: "Mrs. Harrison", brief: "write the parser", state: "clocked in", created_at: 1, updated_at: 2},
            {id: 1128, name: "", brief: "write the docs", state: "clocked in", created_at: 1, updated_at: 2},
        ];
        const cells = orchestraOf({environments: []}, workers, {id: 7, session: "s7"}, "main");
        expect(cells.map((entry) => entry.heading)).toEqual(["Worker 1127, Mrs. Harrison", "Worker 1128"]);
    });
});

describe("the four facts of a worker's cell", () => {
    test("it shows its queue, finished count, pace an hour and context left from the worker's own fields", () => {
        store.rows = {};
        const worker = {id: 5, name: "", brief: "b", state: "clocked in", created_at: 0, updated_at: 7200, agent: 9, context: 35, queue: [{id: 1, title: "a"}, {id: 2, title: "b"}], finished: [3, 4, 6, 7]};
        const [cell] = orchestraOf({environments: []}, [worker], {id: 7, session: "s7"}, "main", 7200);
        expect(cell.facts).toEqual({queued: 2, done: 4, pace: 2, contextLeft: 65});
    });

    test("a worker on its first task shows its queue and nothing finished, with no pace and no context it did not report", () => {
        const worker = {id: 5, name: "", brief: "b", state: "clocked in", created_at: 0, updated_at: 1, agent: 0, context: null, queue: [{id: 1, title: "a"}], finished: []};
        const [cell] = orchestraOf({environments: []}, [worker], {id: 7, session: "s7"}, "main", 3600);
        expect(cell.facts).toEqual({queued: 1, done: 0, pace: null, contextLeft: null});
    });

    test("a worker not yet read by id shows no queue and no finished count", () => {
        const worker = {id: 5, name: "", brief: "b", state: "clocked in", created_at: 0, updated_at: 1};
        const [cell] = orchestraOf({environments: []}, [worker], {id: 7, session: "s7"}, "main", 3600);
        expect(cell.facts).toEqual({queued: null, done: null, pace: null, contextLeft: null});
    });
});
