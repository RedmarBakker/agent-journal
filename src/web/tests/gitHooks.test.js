import {createApp, h} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

const {api} = await import("../src/api/client.js");
const {default: GitHooks} = await import("../src/resource/GitHooks.vue");

let app = null;
afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

test("the Checks page lists each git hook by its name, whether it runs, and what it runs, read only", async () => {
    vi.spyOn(api, "gitHooks").mockResolvedValue([
        {name: "pre-push", is_active: true, folder: "/p/.git/hooks", purpose: "the push gate", commands: ["python3 scripts/suite.py"]},
        {name: "commit-msg", is_active: false, folder: "/p/.git/hooks", purpose: "a commit names its task", commands: ["grep -q Task"]},
    ]);
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(GitHooks)});
    app.mount(host);
    await flush();
    const rows = [...host.querySelectorAll(".git-hook")].map((row) => [row.dataset.hook, row.querySelector(".chip")?.textContent.trim(), row.querySelector(".git-hook-commands").textContent]);
    expect(rows).toEqual([
        ["pre-push", "active", "python3 scripts/suite.py"],
        ["commit-msg", "not running", "grep -q Task"],
    ]);
    expect(host.querySelector("button, input")).toBeNull();
});
