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

test("a tab shown again takes the chat to the foot at once, never gliding, when messages came while it was hidden, even from a reader who had scrolled up", () => {
    const thread = source("../src/chat/Thread.vue");
    expect(thread).toMatch(/turnsWhenHidden = turns\.value\.length;/);
    expect(thread).toMatch(/\(reading\) => reading \|\| \(away\.value && turns\.value\.length <= turnsWhenHidden\) \|\| toFoot\(\)/);
    expect(thread).toMatch(/function toFoot\(\) \{[^}]*glideTo\(false\);/);
});
