import {expect, test, vi} from "vitest";
import {createApp, h, nextTick} from "vue";
import {api} from "../src/api/client.js";
import {actsOf} from "../src/domain/acts.js";
import {checkState, VERDICTS} from "../src/domain/checks.js";
import CheckCard from "../src/resource/CheckCard.vue";
import CheckResult from "../src/resource/CheckResult.vue";

const running = {table: "checks", id: 4, title: "Suite", command: "sleep 30", progress: {time: Date.now() / 1000 - 5, output: "", process: 4242}};
const stopped = {table: "checks", id: 4, title: "Suite", command: "sleep 30", progress: null, last_passed: null, last_stopped: true, last_run_at: new Date().toISOString(), last_duration: 5};

test("a running check shows a Stop button in its card and its page, which posts the check's stop", async () => {
    const act = vi.spyOn(api, "act").mockResolvedValue({});
    for (const component of [CheckCard, CheckResult]) {
        const root = document.createElement("div");
        createApp({render: () => h(component, {resource: running})}).mount(root);
        expect(root.querySelector("button.check-run")).toBeNull();
        const button = root.querySelector("button.check-stop");
        expect(button.textContent.trim()).toBe("Stop");
        button.click();
        await nextTick();
        expect(act).toHaveBeenLastCalledWith("checks", 4, "stop");
    }
    act.mockRestore();
});

test("a check not running offers Run, and a stopped run reads as stopped, neither passed nor failed", () => {
    const root = document.createElement("div");
    createApp({render: () => h(CheckCard, {resource: stopped})}).mount(root);
    expect(root.querySelector("button.check-stop")).toBeNull();
    expect(root.querySelector("button.check-run")).not.toBeNull();
    expect(root.textContent).toContain("Stopped");
    expect(checkState(stopped, Date.now() / 1000).verdict).toBe("stopped");
    expect(VERDICTS.stopped).toBe("Stopped");
    expect(actsOf(running).map((a) => a.name)).toEqual(["stop"]);
    expect(actsOf(stopped).map((a) => a.name)).toEqual(["run"]);
});
