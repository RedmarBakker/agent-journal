import {createApp, h, nextTick} from "vue";
import {expect, test} from "vitest";

const {default: CommandLog} = await import("../src/chat/CommandLog.vue");

test("a command the journal refused shows as refused, dimmed with the reason on hover, and its retry as the one run", async () => {
    const reason = "You cannot mix journal commands with other commands.";
    const line = (time, command, refused = "") => ({agent_id: 1, time, tool: "Journal", command, output: "", seconds: 0, status: 0, stepped: false, level: "everything", refused});
    const lines = [line(1, "journal task list", reason), {...line(1.001, "ls", reason), tool: "Bash"}, {...line(2, "journal task list"), output: "no task"}];
    const host = document.body.appendChild(document.createElement("div"));
    const app = createApp({render: () => h(CommandLog, {lines})});
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    const drawn = [...host.querySelectorAll(".log-line")];
    expect(drawn.map((el) => el.classList.contains("refused"))).toEqual([true, true, false]);
    expect(drawn[0].title).toBe(`The journal refused this before it ran: ${reason}`);
    expect(drawn[0].querySelector(".log-state").textContent).toBe("refused");
    expect(drawn[2].querySelector(".log-state")).toBeNull();
    expect(drawn[2].title).toBe("");
    expect(host.querySelectorAll(".log-output")).toHaveLength(1);
    app.unmount();
    host.remove();
});
