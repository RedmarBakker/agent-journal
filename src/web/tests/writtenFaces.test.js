import {expect, test} from "vitest";
import {VOICE_FACES, EVERY_VOICE_FACES, choicesFor} from "../src/figure/pile.js";
import {writtenFacesAfter} from "../src/domain/figureState.js";

const at = (seconds) => new Date(seconds * 1000).toISOString();
const message = (id, author, text, data = {}, session = "s") => ({table: "messages", id, author, text, data, session, created_at: at(10 + id)});
const agent = {session: "s", data: {}};

test("a face the agent writes in its own message plays the act a reaction with that face plays, for every face of every voice", () => {
    for (const [voice, faces] of Object.entries({...VOICE_FACES, every: EVERY_VOICE_FACES})) {
        for (const [face, clip] of Object.entries(faces)) {
            const [fire] = writtenFacesAfter(agent, [message(1, "agent", `Very good, Sir Jesse. ${face}`)], 0);
            expect(fire, `${voice} ${face}`).toEqual({beat: `agent_reacted:${face}`, time: 11, card: "messages:1"});
            const played = choicesFor({moment: fire.beat, voice: voice === "every" ? "butler" : voice}).map((each) => each.name);
            expect(played, `${voice} ${face}`).toContain(clip);
        }
    }
});

test("only the agent's own words count, once, the first face in a message, never the user's or a message seen before", () => {
    const messages = [
        message(1, "user", "thanks 🎩"),
        message(2, "agent", "Two faces 🥂 and then 🎩"),
        message(3, "agent", "a thought 🎩", {kind: "thought"}),
        message(4, "agent", "another session's 🎩", {}, "other"),
        message(5, "agent", "no face at all"),
    ];
    expect(writtenFacesAfter(agent, messages, 0).map((fire) => [fire.beat, fire.card])).toEqual([["agent_reacted:🥂", "messages:2"]]);
    expect(writtenFacesAfter(agent, messages, 12)).toEqual([]);
});
