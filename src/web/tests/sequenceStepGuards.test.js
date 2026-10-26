import {createApp, h, nextTick} from "vue";
import {expect, test, vi} from "vitest";
import {api} from "../src/api/client.js";

test("a step's file edits are switched to wait in the steps editor and saved with its title and instructions", async () => {
    const saved = vi.spyOn(api, "setSteps").mockResolvedValue({});
    const {default: SequenceSteps} = await import("../src/resource/SequenceSteps.vue");
    const resource = {table: "sequences", id: 3, locked: false, triggers: [], steps: [{title: "Review", instructions: "read the diff", file_edits_allowed: true, allowed_commands: []}]};
    const host = document.createElement("div");
    document.body.append(host);
    createApp({render: () => h(SequenceSteps, {resource})}).mount(host);
    await nextTick();
    expect([...host.querySelectorAll(".stop-title")].map((title) => title.textContent).join(" ")).toContain("Review");
    expect(host.querySelector(".guard").textContent).toBe("File edits allowed");
    [...host.querySelectorAll("button")].find((button) => button.textContent.includes("Edit steps")).click();
    await nextTick();
    host.querySelector(".edits-switch").click();
    await nextTick();
    expect(host.querySelector(".edits-switch").textContent.trim()).toBe("File edits wait");
    [...host.querySelectorAll("button")].find((button) => button.textContent.includes("Save steps")).click();
    await nextTick();
    expect(saved).toHaveBeenCalledWith(3, [{title: "Review", instructions: "read the diff", file_edits_allowed: false, allowed_commands: []}]);
});

test("a new sequence is made on the page with two steps, a step whose file edits wait and a file-text trigger", async () => {
    const created = vi.spyOn(api, "create").mockResolvedValue({id: 9});
    const {default: NewSequence} = await import("../src/resource/NewSequence.vue");
    const host = document.createElement("div");
    document.body.append(host);
    createApp({render: () => h(NewSequence)}).mount(host);
    await nextTick();
    const typed = (input, text) => {
        input.value = text;
        input.dispatchEvent(new Event("input"));
    };
    const button = (words) => [...document.querySelectorAll("button")].find((b) => b.textContent.includes(words));
    typed(document.querySelector(".title-input"), "Clear the todo");
    button("Add a step").click();
    await nextTick();
    const instructions = document.querySelectorAll(".step-card textarea");
    typed(instructions[0], "find what the todo asks");
    typed(instructions[1], "do what it asks");
    document.querySelector(".edits-switch").click();
    button("Add a trigger").click();
    await nextTick();
    button("An edit adds a text").click();
    await nextTick();
    const [glob, text] = document.querySelectorAll(".trigger-field input");
    typed(glob, "src/*.py");
    typed(text, "TODO");
    await nextTick();
    button("Create sequence").click();
    await nextTick();
    expect(created).toHaveBeenCalledWith("sequences", {
        title: "Clear the todo",
        steps: [
            {title: "", instructions: "find what the todo asks", file_edits_allowed: false, allowed_commands: []},
            {title: "", instructions: "do what it asks", file_edits_allowed: true, allowed_commands: []},
        ],
        triggers: [{kind: "file-text", pattern: "src/*.py", text: "TODO"}],
    });
});
