const DAY = 86400000;

const milliseconds = (value) => (typeof value === "number" ? value * 1000 : value ? new Date(value).getTime() : NaN);

export function finishEstimate(plan, tasks, now = Date.now()) {
    const completed = tasks
        .map((task) => milliseconds(task.completed_at || ((task.state === "completed" || task.state === "merged") ? task.updated_at : null)))
        .filter(Number.isFinite);
    if (!completed.length) return null;
    const total = (plan.tasks || []).length;
    const remaining = Math.max(0, total - Math.max(Number(plan.done) || 0, completed.length));
    const days = Math.max(1, (now - Math.min(...completed)) / DAY);
    const perDay = completed.length / days;
    const date = new Date(now + Math.ceil(remaining / perDay) * DAY);
    return {
        date: date.toISOString().slice(0, 10),
        label: new Intl.DateTimeFormat(undefined, {weekday: "short", day: "numeric", month: "short", timeZone: "UTC"}).format(date),
    };
}

export const estimatedCost = (plans) => plans.reduce((sum, plan) => sum + (Number.isFinite(Number(plan.estimated_api_cost_usd)) ? Number(plan.estimated_api_cost_usd) : 0), 0);

export const nearPlanCap = (plan) => Number(plan.cost_cap_usd) > 0 && Number(plan.estimated_api_cost_usd) >= Number(plan.cost_cap_usd) * 0.8;
