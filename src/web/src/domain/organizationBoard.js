const PHASES = [
    ["planned", "Planned"],
    ["in_progress", "In progress"],
    ["in_review", "In review"],
    ["done", "Done"],
];

function matches(plan, words) {
    const query = words.trim().toLowerCase();
    if (!query) return true;
    return [plan.id, plan.title, plan.mode, plan.waits_on].some((value) => String(value || "").toLowerCase().includes(query));
}

// Each domain's four phases, named by its contract, with one card per plan in the phase it reached for that domain.
export function organizationLanes(domain, {words = "", hideDone = false} = {}) {
    return PHASES.map(([key, fallback]) => ({
        key,
        title: domain.board?.[key] || fallback,
        plans: hideDone && key === "done" ? [] : (domain.plans || []).filter((plan) => plan.phase === key && matches(plan, words)),
    }));
}
