import {expect, test, vi} from "vitest";
import {createApp, h, nextTick} from "vue";
import statusBar from "../src/layout/StatusBar.vue?raw";
import reader from "../src/resource/Reader.vue?raw";
import {api} from "../src/api/client.js";
import * as route from "../src/route.js";

const judged = {table: "verifiers", id: 4, name: "Diogenes, lamp-bearer of the honest reason", state: "judged", session: "1b2c3d4e-aaaa", model: "claude-sonnet-5-5", brief: "Judge the dismissal", judged: ["reader_reports:65", "reader_reports:66"], created_at: new Date().toISOString(), updated_at: new Date().toISOString()};

test("the Verifiers dropdown lists each verifier with its state and session, and a click opens its inspector", async () => {
    const peek = vi.spyOn(route, "peek").mockImplementation(() => {});
    const {default: VerifierList} = await import("../src/chat/VerifierList.vue");
    const root = document.createElement("div");
    createApp({render: () => h(VerifierList, {rows: [judged]})}).mount(root);
    await nextTick();
    expect(root.textContent).toContain("Verifier 4");
    expect(root.textContent).toContain("Idle");
    expect(root.textContent).toContain("Session 1b2c3d4e");
    expect(root.textContent).toContain("Judged 2 dismissals");
    root.querySelector("button.verifier").click();
    expect(peek).toHaveBeenCalledWith("verifiers", 4);
    peek.mockRestore();
    expect(statusBar).toContain("<VerifierList");
    expect(reader).toContain("verifier: VerifierPage");
});

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
