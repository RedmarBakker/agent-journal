import {createApp, h} from "vue";
import {afterEach, expect, test} from "vitest";
import CloseButton from "../src/kit/CloseButton.vue";

let app = null;
afterEach(() => {
    app?.unmount();
    document.body.innerHTML = "";
});

test("a close button names itself to screen readers and shows no tooltip", () => {
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp({render: () => h(CloseButton, {title: "Close the plan"})});
    app.mount(host);
    const button = host.querySelector("button");
    expect(button.getAttribute("aria-label")).toBe("Close the plan");
    expect(button.hasAttribute("title")).toBe(false);
    expect(button.hasAttribute("data-tip")).toBe(false);
});
