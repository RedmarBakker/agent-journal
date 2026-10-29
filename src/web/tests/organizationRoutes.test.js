import {beforeEach, describe, expect, test} from "vitest";
import {href, knowPages, PAGES, route} from "../src/route.js";
import {choose} from "../src/state/environment.js";
import {catalog} from "../src/domain/settingsCatalog.js";
import {planAgents, planAgentsOn} from "../src/domain/planAgents.js";
import {store} from "../src/state/store.js";

knowPages((name) => PAGES.includes(name));
choose("main");

const at = async (hash) => {
    location.hash = hash;
    await new Promise((done) => setTimeout(done));
};

describe("the organization pages' addresses", () => {
    beforeEach(() => (store.settings = {plans: {plan_agents: true}}));

    test.each([
        [href.organization(), {page: "organization", domain: "", role: "", shared: false}],
        [href.domain("Sales & Ops"), {page: "organization", domain: "Sales & Ops", role: ""}],
        [href.role("Sales", "Account manager"), {page: "organization", domain: "Sales", role: "Account manager"}],
        [href.rolePage("Sales", "Account manager", "worker:plan-2:9"), {page: "role", domain: "Sales", role: "Account manager", instance: "worker:plan-2:9"}],
        [href.sharedRoles(), {page: "organization", shared: true, domain: ""}],
    ])("%s opens from a link and is read back, and stays after a reload", async (hash, wanted) => {
        await at(hash);
        expect(route.value).toMatchObject(wanted);
        expect(location.hash).toBe(hash);
    });

    test("back returns to the page before", async () => {
        await at(href.organization());
        await at(href.domain("Sales"));
        history.back();
        await new Promise((done) => setTimeout(done, 20));
        expect(route.value.domain).toBe("");
    });
});

describe("the organization addresses with the plan agents setting off", () => {
    test.each([href.organization(), href.domain("Sales"), href.role("Sales", "Account manager"), href.rolePage("Sales", "Account manager"), href.sharedRoles()])("%s leads to the old Home, and to the page once the setting is on", async (hash) => {
        store.settings = {plans: {plan_agents: false}};
        await at(hash);
        expect(planAgents.value).toBe(false);
        expect(route.value.page).toBe("");
        store.settings = {plans: {plan_agents: true}};
        expect(route.value.page).toBe("organization");
    });

    test("another page is the same with the setting off", async () => {
        store.settings = {};
        await at("#/settings?sub=agent");
        expect(route.value.page).toBe("settings");
    });
});

describe("the plan agents setting", () => {
    const spec = {
        features: [{name: "workers", title: "Workers", help: "", default: true, fixed: false, options: [{key: "workers.seat_cap", name: "seat_cap", title: "Most seats at once", abstract: "x", option_type: "number", default: 0, unit: "", choices: [], provider: "", main_switch: ""}]}],
        groups: [{key: "organization", title: "Organization", line: "", section: "Organization", tab: "agent", lead: ""}, {key: "workers", title: "Workers", line: "", section: "Agent", tab: "agent", lead: "workers"}],
    };
    const groupKeys = (settings) => catalog(spec, settings).flatMap((s) => s.groups.map((g) => g.key));

    test("it is off unless set", () => {
        expect(planAgentsOn({})).toBe(false);
        expect(planAgentsOn(null)).toBe(false);
        expect(planAgentsOn({plans: {plan_agents: true}})).toBe(true);
    });

    test("the Settings Organization section shows only while it is on, and the rest of Settings is the same", () => {
        expect(groupKeys({})).toEqual(["workers"]);
        expect(groupKeys({plans: {plan_agents: true}}).sort()).toEqual(["organization", "workers"]);
    });
});
