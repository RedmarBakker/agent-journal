import {describe, expect, test} from "vitest";
import {chatPlan, chatPlanLine, modeOf, planAgentOf} from "../src/domain/plans.js";
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

    test("the trail names a pushed Role state with the Role it works as", () => {
        const agent = {trail: [{before: ["leading_plan (plan 3)", "following_plan (plan 3, task 7)"], after: ["leading_plan (plan 3)", "following_plan (plan 3, task 7)", "role_work (Role builder)"], cause: "task started", refused: "", line: ""}]};
        expect(trailOf(agent)).toEqual(["leading_plan (plan 3), following_plan (plan 3, task 7) > leading_plan (plan 3), following_plan (plan 3, task 7), role_work (Role builder), by task started"]);
    });
});
