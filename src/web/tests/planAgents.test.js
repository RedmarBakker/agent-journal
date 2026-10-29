import {describe, expect, test} from "vitest";
import {chatPlan, chatPlanLine, modeOf, planAgentChats, planAgentChatsMatching, planAgentOf, planChatHeader} from "../src/domain/plans.js";
import {trailOf} from "../src/domain/agentState.js";

const plans = [
    {table: "plans", id: 3, title: "Floors", mode: "solo", chat: "plan-3"},
    {table: "plans", id: 4, title: "Roof", mode: "organization", chat: ""},
];

describe("plans and their Plan agents in the viewer", () => {
    test("a plan names its mode and where its agent runs, and nothing while it has no agent", () => {
        expect(plans.map(modeOf)).toEqual(["Solo mode", "Organization mode"]);
        expect(plans.map(planAgentOf)).toEqual(["Plan agent in plan-3", ""]);
    });

    test("the chat list names a Plan agent's chat by its plan and mode, and no other chat", () => {
        expect(chatPlan(plans, "plan-3").id).toBe(3);
        expect(chatPlanLine(plans, "plan-3")).toBe("Plan 3 · Floors · Solo mode");
        expect(chatPlanLine(plans, "main")).toBe("");
    });

    test("the chat switcher lists the main agent and open Plan agents, searches by title, and marks unread chats", () => {
        const all = [
            {id: 3, title: "Floors", mode: "solo", phase: "in_progress", state: "started", chat: "plan-3"},
            {id: 4, title: "Finished roof", mode: "organization", state: "done", chat: "plan-4"},
            {id: 5, title: "Waiting roof", state: "ready", chat: "plan-5"},
        ];
        const environments = [
            {environment: {name: "main"}, messages: 1},
            {environment: {name: "plan-3"}, messages: 0},
            {environment: {name: "plan-5"}, messages: 2},
        ];
        const chats = planAgentChats(all, environments, "main");

        expect(chats.map((chat) => chat.title)).toEqual(["Main agent", "Floors", "Waiting roof"]);
        expect(chats.map((chat) => chat.unread)).toEqual([true, false, true]);
        expect(planAgentChatsMatching(chats, "roof").map((chat) => chat.title)).toEqual(["Waiting roof"]);
        expect(planChatHeader(all, "plan-3")).toBe("Plan 3 · Floors · Solo mode · Phase: In progress");
    });

    test("the trail names a pushed Role state with the Role it works as", () => {
        const agent = {trail: [{before: ["leading_plan (plan 3)", "following_plan (plan 3, task 7)"], after: ["leading_plan (plan 3)", "following_plan (plan 3, task 7)", "role_work (Role builder)"], cause: "task started", refused: "", line: ""}]};
        expect(trailOf(agent)).toEqual(["leading_plan (plan 3), following_plan (plan 3, task 7) > leading_plan (plan 3), following_plan (plan 3, task 7), role_work (Role builder), by task started"]);
    });
});
