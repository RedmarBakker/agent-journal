import {expect, test} from "vitest";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
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
    expect(bar).toMatch(/<template #jobs>\s*<AgentJobs :jobs="data\.jobs \|\| \[\]" \/>/);
    const list = readFileSync(resolve(__dirname, "../src/chat/AgentJobs.vue"), "utf8");
    expect(list).toMatch(/\{\{ scheduleWords\(job\.cron\) \}\}/);
});
