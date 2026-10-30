import {createApp} from "vue";
import {expect, test, vi} from "vitest";
import {flush} from "./flush.js";

vi.mock("../src/api/client.js", async (original) => ({...(await original()), api: {...(await original()).api, answer: vi.fn().mockResolvedValue({})}}));

const {default: OptionsPicker} = await import("../src/resource/OptionsPicker.vue");

const question = {table: "questions", id: 7, text: "which footer?", options: ["The agent writes the long one", "The agent writes the short one"], recommended: "The agent writes the long one", answer: null};

test("the choice the agent recommends is marked as its recommendation, and the others are not", async () => {
    const into = document.createElement("div");
    document.body.append(into);
    const app = createApp(OptionsPicker, {question});
    app.directive("tip", {});
    app.mount(into);
    await flush();
    const text = into.textContent;
    expect(text).toContain("The agent recommends this");
    expect(text.indexOf("The agent writes the long one")).toBeLessThan(text.indexOf("The agent recommends this"));
    expect(text.split("The agent recommends this").length - 1, "one choice is marked").toBe(1);
    app.unmount();
    into.remove();
});
