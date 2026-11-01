// @vitest-environment node
import {expect, test} from "vitest";
import {catalog, groupRows, settingChanges} from "../src/domain/settingsCatalog.js";

const option = (name, title, abstract, option_type, def, extra = {}) => ({key: name, name: name.split(".")[1], title, abstract, option_type, default: def, unit: "", choices: [], provider: "", main_switch: "", ...extra});
const spec = {
    features: [
        {name: "workers", title: "Workers", help: "", default: true, fixed: false, options: [
            option("workers.organization_folder", "Agentic organization folder", "The folder holding the domains", "text", ""),
            option("workers.default_plan_mode", "Default plan mode", "How a new plan runs", "choice", "organization", {choices: ["organization", "solo"]}),
            option("workers.openrig_version", "OpenRig version", "The OpenRig version", "text", ""),
            option("workers.seat_cap", "Most seats at once", "The most seats", "number", 0, {unit: "seats"}),
            option("workers.cost_cap_dollars", "Most a plan may cost", "The dollars one plan may spend", "number", 0, {unit: "$"}),
            option("workers.timeout_minutes", "Time limit of a worker run", "Minutes", "number", 60),
        ]},
        {name: "plans", title: "Plans", help: "", default: true, fixed: false, options: [option("plans.plan_agents", "Plan agents", "On: plan agents", "switch", false)]},
    ],
    groups: [
        {key: "workers", title: "Workers", line: "", section: "Agent", tab: "agent", lead: "workers"},
        {key: "plans", title: "Plans", line: "", section: "Agent", tab: "agent", lead: "plans"},
        {key: "organization", title: "Organization", line: "", section: "Organization", tab: "agent", lead: ""},
    ],
};
const rowsOf = (sections, key) => groupRows(sections.flatMap((s) => s.groups).find((g) => g.key === key)).filter((r) => r.kind !== "switch" || r.target?.path[0] !== "features");

test("the Organization section holds the five organization settings, each with its words, and the other groups do not repeat them", () => {
    const sections = catalog(spec, {workers: {seat_cap: 4}, plans: {plan_agents: true}});
    const organization = rowsOf(sections, "organization");
    expect(organization.map((r) => r.label)).toEqual(["Agentic organization folder", "Default plan mode", "OpenRig version", "Most seats at once", "Most a plan may cost"]);
    expect(organization.every((r) => r.hint.length > 1)).toBe(true);
    expect(organization[3].value).toBe(4);
    expect(organization[1].options.map((o) => o.key)).toEqual(["organization", "solo"]);
    expect(rowsOf(sections, "workers").map((r) => r.label)).toEqual(["Time limit of a worker run"]);
    expect(rowsOf(sections, "plans").map((r) => r.label)).toEqual(["Plan agents"]);
});

test("a row of the Organization section writes its setting under its own feature", () => {
    const row = rowsOf(catalog(spec, {plans: {plan_agents: true}}), "organization")[1];
    expect(settingChanges(row.target, "solo", {})).toEqual({workers: {default_plan_mode: "solo"}});
});
