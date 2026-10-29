import {describe, expect, test} from "vitest";
import {ORGANIZATION_STATES} from "../src/domain/organizationStates.js";
import OrganizationState from "../src/kit/OrganizationState.vue";
import {shown} from "./shown.js";

describe("the organization screens' states", () => {
    test.each([
        ["no-folder", "No organization folder set"],
        ["contracts", "Some contracts have problems"],
        ["openrig", "OpenRig is not available"],
        ["agents-off", "Plan agents are off"],
        ["no-plans", "This domain has no plans yet"],
        ["never-ran", "This Role has not run yet"],
        ["failed", "Could not load"],
    ])("%s says %s in plain words and what to do", async (state, title) => {
        const host = await shown(OrganizationState, {state});
        expect(host.textContent).toContain(title);
        expect(host.textContent).toContain(ORGANIZATION_STATES[state].text);
    });

    test("a problem state adds the detail it is given", async () => {
        const host = await shown(OrganizationState, {state: "contracts", detail: "sales/account.md: no job."});
        expect(host.textContent).toContain("sales/account.md: no job.");
    });

    test("loading shows a skeleton and none of the words", async () => {
        const host = await shown(OrganizationState, {state: "loading"});
        expect(host.querySelector("[aria-busy='true']")).not.toBeNull();
    });
});
