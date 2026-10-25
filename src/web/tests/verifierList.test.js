import {expect, test, vi} from "vitest";
import {createApp, h, nextTick} from "vue";
import {api} from "../src/api/client.js";

const judged = {table: "verifiers", id: 4, name: "Diogenes, lamp-bearer of the honest reason", state: "judged", session: "1b2c3d4e-aaaa", model: "claude-sonnet-5-5", brief: "Judge the dismissal", judged: ["reader_reports:65", "reader_reports:66"], created_at: new Date().toISOString(), updated_at: new Date().toISOString()};

test("a verifier's inspector shows its state, session, the reports it judged and its transcript", async () => {
    vi.spyOn(api, "verifierTranscript").mockResolvedValue({turns: [], total: 0});
    window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
    const {default: VerifierPage} = await import("../src/resource/VerifierPage.vue");
    const root = document.createElement("div");
    createApp({render: () => h(VerifierPage, {resource: judged})}).mount(root);
    await nextTick();
    expect(root.textContent).toContain("Verifier 4");
    expect(root.textContent).toContain("Session 1b2c3d4e-aaaa");
    expect(root.textContent).toContain("Reader report 66");
    expect(root.textContent).toContain("Transcript");
});
