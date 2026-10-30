import {expect, test} from "vitest";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {actorName, isMe, personName} from "../src/domain/people.js";

const people = (me) => ({me, device: "", people: [{id: 3, name: "Jesse Gall"}, {id: 7, name: "Anna de Vries"}]});

test("a message by user 7 is Anna de Vries to user 3 and you to user 7, and an agent is the agent", () => {
    expect(actorName("user:7", people(3))).toBe("Anna de Vries");
    expect(actorName("user:7", people(7))).toBe("you");
    expect(actorName("agent:abc", people(3))).toBe("the agent");
    expect(personName(3, people(3))).toBe("Jesse Gall");
    expect(isMe("user:7", people(7)) && !isMe("user:7", people(3))).toBe(true);
});

test("the viewer keeps a chat's messages in the order they were written, whichever journal numbered them", () => {
    const rows = readFileSync(resolve(__dirname, "../src/sync/rows.js"), "utf8");
    expect(rows).toMatch(/const ORDERS = \{messages: byWriting\}/);
    expect(rows).not.toMatch(/\.sort\(byId\)/);
});
