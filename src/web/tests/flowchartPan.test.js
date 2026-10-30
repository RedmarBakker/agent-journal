import {createApp} from "vue";
import {afterEach, expect, test} from "vitest";
import {flush} from "./flush.js";
import FlowchartDialog from "../src/chat/FlowchartDialog.vue";

let app = null;
let host = null;

afterEach(() => {
    app?.unmount();
    host?.remove();
});

test("pressing to pan the flowchart clears any text selection and keeps the browser from starting one", async () => {
    host = document.createElement("div");
    document.body.append(host);
    app = createApp(FlowchartDialog, {title: "How a run is read", edges: [["Run", "Reader", ""]]});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    const frame = document.body.querySelector(".flowchart-frame");
    const label = document.body.querySelector(".flowchart tspan");
    window.getSelection().selectAllChildren(label || frame);
    const press = new MouseEvent("pointerdown", {bubbles: true, cancelable: true, clientX: 10, clientY: 10});
    frame.dispatchEvent(press);
    expect(press.defaultPrevented, "the browser starts no selection").toBe(true);
    expect(window.getSelection().toString(), "a selection made before is cleared").toBe("");
});
