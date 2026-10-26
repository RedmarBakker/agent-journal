import {createApp, h, nextTick} from "vue";
import {expect, test} from "vitest";
import ChatMark from "../src/kit/ChatMark.vue";

async function drawn(mark) {
    const host = document.body.appendChild(document.createElement("div"));
    const app = createApp({render: () => h(ChatMark, {mark})});
    app.mount(host);
    await nextTick();
    const el = host.querySelector(".mark");
    const shown = {classes: [...el.classList], style: el.getAttribute("style") || ""};
    app.unmount();
    host.remove();
    return shown;
}

test("a mark's shape says how much it matters: an event a quiet line, running work outlined, what needs the user filled", async () => {
    expect((await drawn({label: "Skill journal loaded", group: "agent"})).classes).toContain("w-event");
    expect((await drawn({label: "Running the tests", group: "work", active: true, counting: true})).classes).toContain("w-process");
    expect((await drawn({label: "Check failed", tone: "bad"})).classes).toContain("w-attention");
    expect((await drawn({label: "Agent stuck", tone: "warn"})).classes).toContain("w-attention");
    expect((await drawn({label: "Check passed", tone: "good"})).classes).toContain("w-event");
});

test("a mark's icon takes its group's colour, and its outcome's colour where it reports one", async () => {
    expect((await drawn({label: "Rule recalled", group: "reminders"})).style).toContain("--mark: var(--group-reminders)");
    expect((await drawn({label: "Check passed", group: "work", tone: "good"})).style).toContain("--mark: var(--tone-good)");
});
