import {createApp, h, nextTick, ref} from "vue";
import {afterEach, expect, test} from "vitest";

const {default: GrowIn} = await import("../src/kit/GrowIn.vue");

let app = null;
afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
});

const mounted = (shown) => {
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(GrowIn, {shown: shown.value}, () => h("p", {class: "linked"}, "Linked: task 3"))});
    app.mount(host);
    return host;
};

test("a line added to a message after it is shown grows in from no height while it fades in, instead of popping in", async () => {
    const shown = ref(false);
    const host = mounted(shown);
    expect(host.querySelector(".linked")).toBeNull();
    shown.value = true;
    await nextTick();
    const grow = host.querySelector(".grow-in");
    expect(grow.querySelector(".linked").textContent).toBe("Linked: task 3");
    expect(grow.classList.contains("grow-in-enter-active")).toBe(true);
});

test("a line there when its message is first shown is simply there, with no growing in", async () => {
    const host = mounted(ref(true));
    await nextTick();
    const grow = host.querySelector(".grow-in");
    expect(grow.classList.contains("grow-in-enter-active")).toBe(false);
    expect(grow.querySelector(".linked")).not.toBeNull();
});
