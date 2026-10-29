import {readFileSync} from "node:fs";
import {expect, test} from "vitest";

test("the plan card approves through a split button whose menu approves with a comment, sent before the approval names it", () => {
    const card = readFileSync("src/chat/PlanCard.vue", "utf8");
    const thread = readFileSync("src/chat/Thread.vue", "utf8");
    expect(card).toContain("<SplitButton");
    expect(card).toContain("Approve with a comment</MenuItem>");
    expect(card).toContain('approves: props.plan.id});');
    expect(thread).toContain("if (replying.approves) sent.delivered.then((delivered) => delivered && approveWithMessage(replying.approves, sent.id));");
});
