import {api} from "../api/client.js";
import {patched, rows} from "../sync/rows.js";

const act = (plan, method) => api.act("plans", plan.id, method);
const becomes = (state) => (plan) => (plan.state = state);

export const approvePlan = (plan) => patched(plan, becomes("approved"), () => act(plan, "approve"));

export const pausePlan = (plan) => patched(plan, becomes("paused"), () => act(plan, "pause"));

export function startPlan(plan) {
    const takeOver = (row) => {
        rows("plans")
            .filter((p) => p !== row && p.state === "started")
            .forEach(becomes("paused"));
        becomes("started")(row);
    };
    return patched(plan, takeOver, () => act(plan, "start"));
}
