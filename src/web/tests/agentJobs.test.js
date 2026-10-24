import {expect, test} from "vitest";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {createApp, h, nextTick} from "vue";
import {vi} from "vitest";
import {api} from "../src/api/client.js";
import AgentJobs from "../src/chat/AgentJobs.vue";
import {nextRun, scheduleWords} from "../src/domain/cron.js";

test("a cron schedule reads in plain words and knows when it runs next", () => {
    expect(scheduleWords("7,22,37,52 * * * *")).toBe("every hour at :07, :22, :37, :52");
    expect(scheduleWords("*/5 * * * *")).toBe("every 5 minutes");
    expect(scheduleWords("57 8 * * *")).toBe("every day at 08:57");
    const next = nextRun("7,22,37,52 * * * *", new Date(2026, 9, 23, 18, 10));
    expect([next.getHours(), next.getMinutes()]).toEqual([18, 22]);
});

test("the agent bar lists the agent's scheduled jobs in a dropdown of their own", () => {
    const facts = readFileSync(resolve(__dirname, "../src/chat/AgentFacts.vue"), "utf8");
    expect(facts).toMatch(/key: "jobs",\s*icon: "clock",\s*n: \(props\.data\?\.jobs \|\| \[\]\)\.length/);
    const bar = readFileSync(resolve(__dirname, "../src/chat/AgentBar.vue"), "utf8");
    expect(bar).toMatch(/<template #jobs>\s*<AgentJobs :agent="data\.id" :jobs="data\.jobs \|\| \[\]" \/>/);
    const list = readFileSync(resolve(__dirname, "../src/chat/AgentJobs.vue"), "utf8");
    expect(list).toMatch(/\{\{ scheduleWords\(job\.cron\) \}\}/);
});

test("the agent bar lists each scheduled job with its schedule in plain words and a Stop button that stops that job", async () => {
    const stop = vi.spyOn(api, "stopJob").mockResolvedValue({asked: true});
    const root = document.createElement("div");
    const jobs = [{id: "200ed8b1", cron: "*/5 * * * *", prompt: "Journal health check\nrun the script", recurring: true}];
    createApp({render: () => h(AgentJobs, {agent: 7, jobs})}).mount(root);
    expect(root.textContent).toContain("Journal health check");
    expect(root.textContent).toContain("every 5 minutes");
    const button = root.querySelector("button.agent-job-stop");
    expect(button.textContent.trim()).toBe("Stop");
    button.click();
    await nextTick();
    expect(stop).toHaveBeenCalledWith(7, "200ed8b1");
    expect(root.querySelector("button.agent-job-stop").textContent.trim()).toBe("Stopping");
});
