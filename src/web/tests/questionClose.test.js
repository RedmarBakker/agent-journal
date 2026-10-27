import {createApp, h} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

const {api} = await import("../src/api/client.js");
const {default: OptionsPicker} = await import("../src/resource/OptionsPicker.vue");

let app = null;

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

async function drawn(question) {
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(OptionsPicker, {question})});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    return host;
}

test("an open question has a Close button, in the chat's card and the overlay alike, which closes it with no reason asked", async () => {
    const act = vi.spyOn(api, "act").mockResolvedValue({});
    const host = await drawn({table: "questions", id: 7, text: "Which colour?", options: ["a", "b"], answer: null});
    const close = [...host.querySelectorAll("button")].find((b) => b.textContent.trim() === "Close");
    close.click();
    await flush();
    expect(act).toHaveBeenCalledWith("questions", 7, "close");
    expect(host.querySelector("input").value).toBe("");
});

test("a question the user closed says so, and is not shown as an answer in their own words", async () => {
    const host = await drawn({table: "questions", id: 7, text: "Which colour?", options: ["a", "b"], answer: "The user closed it without an answer.", closed: true});
    expect(host.querySelector(".closed").textContent).toBe("You closed it without an answer.");
    expect(host.querySelector(".own-words")).toBeNull();
    expect([...host.querySelectorAll("button")].some((b) => b.textContent.trim() === "Close")).toBe(false);
});
