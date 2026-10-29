import {createApp, h} from "vue";
import {afterEach, expect, test} from "vitest";

const {default: PlanTimeline} = await import("../src/resource/PlanTimeline.vue");

let app = null;
let host = null;

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
});

test("plan communication moments show their destination and the suggested hub on a refusal", () => {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(PlanTimeline, {items: [
        {time: 1767225600, moment_type: "handoff", task: 0, title: "domain:alpha", text: "Please check the file", address: "domain:alpha", failure: ""},
        {time: 1767225660, moment_type: "refused_send", task: 0, title: "worker 13, Scout", text: "Send this directly", address: "workers:13", failure: "Roles do not send to each other. Send it to your Domain agent, domain:alpha, which passes it on"},
    ]})});
    app.mount(host);

    expect(host.textContent).toContain("Hand-off");
    expect(host.textContent).toContain("Destination address: domain:alpha");
    expect(host.textContent).toContain("Please check the file");
    expect(host.textContent).toContain("Refused send");
    expect(host.textContent).toContain("Destination address: workers:13");
    expect(host.textContent).toContain("hub to use: Roles do not send to each other. Send it to your Domain agent, domain:alpha, which passes it on");
});
