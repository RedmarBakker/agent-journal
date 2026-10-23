import {expect, test} from "vitest";
import {readFileSync, readdirSync} from "node:fs";
import {resolve} from "node:path";
import {ChatMark} from "../src/domain/chatMark.js";
import {withSystemCards} from "../src/domain/figureState.js";

test("a chat mark answers from the guesses the server made, and no figure code matches a title itself", () => {
    const message = (text, data) => ({table: "messages", id: 1, author: "system", session: "s", created_at: new Date(2000).toISOString(), text, data: {card_type: "process", ...data}});
    const agent = withSystemCards({session: "s", data: {cards: []}}, [message("Build the viewer", {guess_is_build: true})]);
    const mark = new ChatMark(agent.data.cards[0]);
    expect([mark.guessIsTest(), mark.guessIsBuild(), mark.guessIsUpload()]).toEqual([false, true, false]);
    expect(new ChatMark({label: "Running tests"}).guessIsTest(), "a title alone guesses nothing here").toBe(false);
    const sources = [resolve(__dirname, "../src/domain/figureState.js"), ...readdirSync(resolve(__dirname, "../src/figure")).map((name) => resolve(__dirname, "../src/figure", name))];
    for (const path of sources) expect(readFileSync(path, "utf8"), path).not.toMatch(/\/(test|build|upload)\/i/);
});
