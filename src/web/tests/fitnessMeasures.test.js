import {createApp, h, nextTick} from "vue";
import {expect, test, vi} from "vitest";
import {store} from "../src/state/store.js";

vi.mock("../src/actions/settings.js", () => ({saveSettings: vi.fn(async () => ({}))}));

test("the fitness dropdown lists each measure with its value, range and state, and the band", async () => {
    const {default: FitnessTimeline} = await import("../src/layout/FitnessTimeline.vue");
    store.settings = {workers: {}};
    const measures = [
        {key: "high_queue_minutes", label: "Minutes the worker queue stood high", value: 16, is_measured: true, is_failing: true, changed_at: 1700000000, last_line_at: 1700000300, fail_level: 15, pass_level: 15},
        {key: "clearing_wait", label: "Minutes the oldest worker waited", value: 2.5, is_measured: true, is_failing: false, changed_at: 0, last_line_at: 0, fail_level: 6, pass_level: 6},
        {key: "delegation", label: "Your own share of the landed code", value: 0, is_measured: false, is_failing: false, changed_at: 0, last_line_at: 0, fail_level: 0.3, pass_level: 0.2},
    ];
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(FitnessTimeline, {score: 70, hours: 6, low: 75, measures, band: "high", bandChangedAt: 1700000000})});
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    const rows = [...host.querySelectorAll(".fitness-timeline-measure")];
    expect(rows.map((row) => row.querySelector(".fitness-timeline-measure-label").textContent)).toEqual(measures.map((measure) => measure.label));
    expect(rows[0].classList.contains("failing")).toBe(true);
    expect(rows[0].textContent).toContain("fails over 15");
    expect(rows[0].querySelector(".fitness-timeline-measure-state").textContent).toMatch(/^failing since .*, told at /);
    expect(rows[1].querySelector(".fitness-timeline-measure-state").textContent).toBe("passing");
    expect(rows[2].classList.contains("unmeasured")).toBe(true);
    expect(rows[2].querySelector(".fitness-timeline-measure-value").textContent).toBe("–");
    expect(host.querySelector(".fitness-timeline-band").textContent).toMatch(/^Worker queue high since /);
    app.unmount();
    host.remove();
});
