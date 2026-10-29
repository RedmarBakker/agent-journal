import {expect, test, vi} from "vitest";

test("the phone answers an approval through the phone journal path", async () => {
    document.documentElement.classList.add("phone");
    vi.resetModules();
    const approval = {
        id: 4,
        environment_id: 12,
        role: "Release Manager",
        plan_id: 24,
        task_id: 58,
        decision: "pending",
        expires_at: new Date(Date.now() + 3600000).toISOString(),
    };
    const fetched = vi.fn(async () => new Response(JSON.stringify({...approval, decision: "approved", updater: "phone:1"}), {status: 200, headers: {"Content-Type": "application/json"}}));
    vi.stubGlobal("fetch", fetched);
    const {createApp, h} = await import("vue");
    const {choose} = await import("../src/state/environment.js");
    const {api} = await import("../src/api/client.js");
    const {default:Approvals} = await import("../src/organization/Approvals.vue");
    choose("main");
    const host = document.body.appendChild(document.createElement("div"));
    const app = createApp({render: () => h(Approvals, {approval, question: "Approve production deployment for Role Release Manager, task 58?"})});
    app.provide("scope", {api});
    app.mount(host);

    [...host.querySelectorAll("button")].find((button) => button.textContent.includes("Approve")).click();
    await vi.waitFor(() => expect(host.textContent).toContain("Approved by you, from your phone"));
    expect(fetched.mock.calls[0][0]).toBe("/p/journal/approvals/4/approve");
    expect(fetched.mock.calls[0][1].headers["X-Phone"]).toBe("1");
    expect(fetched.mock.calls[0][1].headers["X-Journal-Viewer"]).toBeUndefined();

    app.unmount();
    host.remove();
    vi.unstubAllGlobals();
    document.documentElement.classList.remove("phone");
});
