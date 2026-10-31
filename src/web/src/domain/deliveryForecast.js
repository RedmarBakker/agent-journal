const day = (value) => value?.slice(0, 10) || "";

export function formatForecastDay(value) {
    if (!value) return "";
    const date = value instanceof Date ? value : new Date(`${day(value)}T12:00:00`);
    return new Intl.DateTimeFormat("en-GB", {day: "numeric", month: "short"}).format(date);
}

export function sprintRange(sprint) {
    if (!sprint?.starts_on || !sprint?.ends_on) return "Dates not set";
    const end = new Date(`${sprint.ends_on}T12:00:00`);
    end.setDate(end.getDate() - 1);
    return `${formatForecastDay(sprint.starts_on)} to ${formatForecastDay(end)}`;
}

export function sprintEnd(sprint) {
    if (!sprint?.ends_on) return "Dates not set";
    const end = new Date(`${sprint.ends_on}T12:00:00`);
    end.setDate(end.getDate() - 1);
    return formatForecastDay(end);
}

export function forecastTone(probability) {
    if (!Number.isFinite(probability)) return "unknown";
    if (probability >= 70) return "good";
    if (probability >= 40) return "caution";
    return "risk";
}

export function forecastForPlan(planId, sprintForecasts) {
    const period = planPeriod(planId, sprintForecasts);
    if (!period) return null;
    const forecast = period.forecast || {};
    const plan = forecast.plan_forecasts?.find((row) => row.plan_id === planId);
    return {...forecast, ...(plan || {}), sprint: period.sprint};
}

export function sprintGroups(plans, sprintForecasts) {
    const asOf = sprintForecasts.map((row) => row.forecast?.as_of).filter(Boolean).sort().at(-1) || new Date().toISOString().slice(0, 10);
    const memberships = plans.map((plan) => ({plan, period: planPeriod(plan.id, sprintForecasts)}));
    const groups = sprintForecasts.map((entry) => {
        const rows = memberships.filter(({period}) => period?.sprint.id === entry.sprint.id);
        const shown = rows.map(({plan}) => ({plan, forecast: forecastForEntry(entry, plan.id)}));
        const status = sprintState(entry.sprint, asOf);
        const unfinished = shown.some(({plan, forecast}) => plan.state !== "cancelled" && forecast?.delivery_complete !== true);
        return {key: String(entry.sprint.id), sprint: entry.sprint, forecast: entry.forecast,
            plans: shown, status, unfinished, order: orderOf(status, unfinished), asOf};
    }).filter((group) => group.plans.length);
    groups.sort((first, second) => first.order - second.order || compareGroups(first, second));
    const unscheduled = memberships.filter(({period}) => !period).map(({plan}) => ({plan, forecast: null}));
    if (unscheduled.length) groups.push({key: "none", sprint: null, forecast: null, plans: unscheduled, status: "unscheduled", unfinished: true, order: 4, asOf});
    return groups;
}

export function sprintStatusLabel(group) {
    if (group.status === "unscheduled") return "No sprint";
    const today = group.asOf;
    if (group.status === "ended") return `Ended ${difference(today, lastDay(group.sprint.ends_on))} days ago`;
    if (group.status === "current") return `Current sprint, ends in ${difference(lastDay(group.sprint.ends_on), today)} days`;
    return `Next sprint, starts in ${difference(group.sprint.starts_on, today)} days`;
}

function planPeriod(planId, entries) {
    return entries
        .filter((entry) => entry.sprint.plan_ids.includes(planId))
        .sort((first, second) => Number(first.sprint.state === "closed") - Number(second.sprint.state === "closed") || second.sprint.starts_on.localeCompare(first.sprint.starts_on))[0] || null;
}

function forecastForEntry(entry, planId) {
    const plan = entry.forecast?.plan_forecasts?.find((row) => row.plan_id === planId);
    return {...(entry.forecast || {}), ...(plan || {}), sprint: entry.sprint};
}

function sprintState(sprint, asOf) {
    if (sprint.state === "closed" || (sprint.ends_on && sprint.ends_on <= asOf)) return "ended";
    if (sprint.starts_on <= asOf) return "current";
    return "future";
}

function orderOf(status, unfinished) {
    if (status === "ended" && unfinished) return 0;
    if (status === "current") return 1;
    if (status === "future") return 2;
    return 3;
}

function compareGroups(first, second) {
    return first.status === "future" ? first.sprint.starts_on.localeCompare(second.sprint.starts_on) : second.sprint.ends_on.localeCompare(first.sprint.ends_on);
}

function lastDay(value) {
    const date = new Date(`${value}T00:00:00Z`);
    date.setUTCDate(date.getUTCDate() - 1);
    return date.toISOString().slice(0, 10);
}

function difference(later, earlier) {
    return Math.max(0, Math.round((Date.parse(`${later}T00:00:00Z`) - Date.parse(`${earlier}T00:00:00Z`)) / 86400000));
}
