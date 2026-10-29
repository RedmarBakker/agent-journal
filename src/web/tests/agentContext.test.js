import {createApp, h} from "vue";
import {afterEach, expect, test} from "vitest";
import AgentFacts from "../src/chat/AgentFacts.vue";

let app;
afterEach(() => {
    app?.unmount();
    document.body.innerHTML = "";
});

const shown = (context) => {
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(AgentFacts, {data: {id: 1, provider: "codex", model: "", capabilities: ["context status"], context, usage: []}})});
    app.directive("tip", {});
    app.mount(host);
    return host.querySelector(".agent-context");
};

test("a context the session has not reported is not drawn, so a session that took over shows none of the one before", () => {
    expect(shown(null)).toBeNull();
});

test("a context reported as empty is drawn as nought percent", () => {
    expect(shown(0).textContent).toContain("0%");
});
