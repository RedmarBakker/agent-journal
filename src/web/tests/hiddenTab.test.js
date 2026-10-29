import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {expect, test} from "vitest";

const source = (path) => readFileSync(resolve(__dirname, path), "utf8");

test("a hidden tab holds no stream and asks for no entries, and a shown one opens the stream after the newest entry it holds", () => {
    const stream = source("../src/sync/stream.js");
    expect(stream).toMatch(/export function listen\(\) \{\s*if \(document\.hidden\) return hush\(\);/);
    expect(stream).toMatch(/function hush\(\) \{[^}]*clearInterval\(watching\);[^}]*clearInterval\(asking\);[^}]*source\.close\(\);/);
    expect(stream).toMatch(/document\.addEventListener\("visibilitychange", \(\) => listen\(\)\);/);
});

test("a returning tab follows the latest messages only when the reader was already at the bottom", () => {
    const thread = source("../src/chat/Thread.vue");
    expect(thread).toContain("(reading) => reading || away.value || toFoot()");
    expect(thread).toMatch(/function toFoot\(\) \{[^}]*glideTo\(false\);/);
});
