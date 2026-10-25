import {createApp, h} from "vue";
import {afterEach, expect, test} from "vitest";
import HiddenEnvironmentsCard from "../src/layout/HiddenEnvironmentsCard.vue";

let app = null;

afterEach(() => {
    app?.unmount();
    document.body.innerHTML = "";
    localStorage.clear();
});

function mounted() {
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp({render: () => h(HiddenEnvironmentsCard)});
    app.mount(host);
    return host;
}

test("the card saying colleagues' environments are hidden unless their chat is shared shows once, and not on the next load", () => {
    localStorage.clear();
    expect(mounted().textContent).toContain("Colleagues' environments are no longer shown unless their chat is shared.");
    app.unmount();
    expect(mounted().textContent).not.toContain("Colleagues' environments");
});
