import {describe, expect, test} from "vitest";
import ResourceCard from "../src/resource/ResourceCard.vue";
import {store} from "../src/state/store.js";
import {shown} from "./shown.js";

const task = (id, state) => ({table: "tasks", id, state: state === "done" ? "completed" : state, completed_at: state === "done" ? "2026-10-19T10:00:00+00:00" : null});

describe("a plan's card", () => {
    test("counts its tasks as the plan's page does, with the phase it is in beside it", async () => {
        store.rows = {...store.rows, tasks: [task(1, "done"), task(2, "done"), task(3, "open")]};
        const plan = {table: "plans", id: 15, title: "GPS integration", state: "approved", held: false, task_ids: [1, 2, 3], current_phase: 1, phases: [{title: "One", task_ids: [1, 2]}, {title: "Two", task_ids: [3]}], created_at: "2026-10-19T09:00:00+00:00"};
        const card = await shown(ResourceCard, {resource: plan});
        expect(card.querySelector(".plan-steps").textContent).toBe("2 of 3 tasks done · phase 1 of 2 · approved");
    });
});

test("a plan the user closed on the card leaves the card to the next plan waiting, one at a time", async () => {
    const {cardPlan, cardChoices} = await import("../src/domain/plans.js");
    const waiting = (id, extra = {}) => ({table: "plans", id, title: `Plan ${id}`, state: "ready", ...extra});
    const plans = [waiting(1, {is_dismissed: true}), waiting(2), waiting(3)];
    expect(cardPlan(plans)?.id).toBe(2);
    expect(cardChoices(plans, cardPlan(plans)).map((plan) => plan.id)).toEqual([3]);
});
