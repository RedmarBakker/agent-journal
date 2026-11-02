import {createApp, h} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

const {api} = await import("../src/api/client.js");
const {default: Control} = await import("../src/pages/Control.vue");

afterEach(() => {
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

test("Control shows every tier-three decision on request and saves a choice while keeping its own grant at Never", async () => {
    const decisions = [
        {area: "Plans and tasks", noun: "plan", verb: "approve", command: "plan approve", decision: "propose_only"},
        ...Array.from({length: 6}, (_, index) => ({
            area: "Plans and tasks",
            noun: "plan",
            verb: `decision ${index + 2}`,
            command: `plan decision ${index + 2}`,
            decision: "propose_only",
        })),
    ];
    vi.spyOn(api, "supervisorControl").mockResolvedValue({
        grant_id: "grant-1", grant_version: 4, tier_three_decisions: decisions,
        never_allowed: [{area: "Its own grant", noun: "grant", verb: "change", command: "grant change", decision: "never"}],
    });
    const save = vi.spyOn(api, "saveSupervisorDecision").mockResolvedValue({});
    const host = document.body.appendChild(document.createElement("div"));
    const app = createApp({render: () => h(Control)});
    app.mount(host);
    await flush();

    expect(host.textContent).toContain("Needs your decision");
    expect(host.querySelectorAll(".decision-row")).toHaveLength(5);
    const defaultChoice = host.querySelector('[data-command="plan approve"] input[value="propose_only"]');
    expect(defaultChoice.checked).toBe(true);
    expect(host.textContent).toContain("Changing its own grant");
    const grantChange = host.querySelector('[data-command="grant change"]');
    expect(grantChange.textContent).toContain("Never");
    expect(grantChange.querySelector("input")).toBeNull();

    [...host.querySelectorAll("button")].find((button) => button.textContent.trim() === "Show all").click();
    await flush();
    expect(host.querySelectorAll(".decision-row")).toHaveLength(decisions.length);
    expect(host.textContent).toContain("plan decision 7");

    const mayAct = host.querySelector('[data-command="plan approve"] input[value="may_act"]');
    mayAct.checked = true;
    mayAct.dispatchEvent(new Event("change", {bubbles: true}));
    await flush();
    expect(save).toHaveBeenCalledWith("grant-1", 4, "plan approve", "may_act");
    app.unmount();
});
