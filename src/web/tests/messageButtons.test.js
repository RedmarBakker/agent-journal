import {createApp} from "vue";
import {afterEach, expect, test} from "vitest";
import {flush} from "./flush.js";
import MessageButtons from "../src/chat/MessageButtons.vue";

let app = null;
let host = null;

afterEach(() => {
    app?.unmount();
    host?.remove();
});

test("a link button opens its address in a new tab and a form button posts its hidden fields to its address", async () => {
    const message = {
        table: "messages",
        id: 7,
        text: "Create the app.",
        data: {
            buttons: [
                {label: "Open the setup page", action: "http://localhost:8765/", note: "opens the page in a new tab", method: "GET", fields: {}},
                {label: "Create the app", action: "https://github.com/organizations/acme/settings/apps/new", note: "sends the app manifest to GitHub", method: "POST", fields: {manifest: '{"name": "acme deploys"}', state: "one"}},
            ],
        },
    };
    host = document.createElement("div");
    document.body.append(host);
    app = createApp(MessageButtons, {message});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    const link = host.querySelector("a.message-button");
    expect([link.textContent.trim(), link.getAttribute("href"), link.getAttribute("target")]).toEqual(["Open the setup page", "http://localhost:8765/", "_blank"]);
    const form = host.querySelector("form");
    expect([form.getAttribute("method"), form.getAttribute("action"), form.getAttribute("target")]).toEqual(["post", "https://github.com/organizations/acme/settings/apps/new", "_blank"]);
    expect(Object.fromEntries([...form.querySelectorAll("input[type=hidden]")].map((i) => [i.name, i.value]))).toEqual({manifest: '{"name": "acme deploys"}', state: "one"});
    expect(form.querySelector("button[type=submit]").textContent.trim()).toBe("Create the app");
});
