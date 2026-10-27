import {describe, expect, it} from "vitest";
import {doesOf, sentence, wordsText} from "../src/domain/triggerWords.js";
import {startWords, triggerBody, triggersProblem} from "../src/domain/sequenceTriggers.js";

const trigger = (more = {}) => ({table: "triggers", id: 3, phrases: ["force push"], action: "deny", text: "Never force-push", ...more});

describe("the words a trigger watches", () => {
    it("are quoted, joined with or, and the rest counted", () => {
        expect(wordsText(["a"])).toBe("“a”");
        expect(wordsText(["a", "b"])).toBe("“a” or “b”");
        expect(wordsText(["a", "b", "c", "d", "e"])).toBe("“a”, “b”, “c” or 2 other phrases");
    });
});

describe("the sentence a trigger reads as", () => {
    it("names the words and what happens", () => {
        expect(sentence(trigger())).toBe("When “force push” comes up, block it and tell the agent “Never force-push”.");
    });

    it("asks for words while it has none", () => {
        expect(sentence(trigger({phrases: []}))).toBe("Add the words to watch for and choose what happens.");
    });

    it("an unknown action reads as a reminder", () => {
        expect(doesOf("nothing").value).toBe("nudge");
    });
});

describe("when a sequence starts", () => {
    it("reads each of its triggers as a sentence, or by hand only", () => {
        const triggers = [
            {trigger_type: "row", moment: "task.created"},
            {trigger_type: "phrase", text: "give me an update"},
            {trigger_type: "command", pattern: "^git push"},
            {trigger_type: "file", pattern: "src/*.py"},
            {trigger_type: "file-text", pattern: "src/*.py", text: "TODO"},
            {trigger_type: "tool", tool: "Edit", pattern: ""},
        ];
        expect(startWords({triggers})).toEqual([
            "When a task is made",
            "When you ask “give me an update”",
            "When a command matching “^git push” runs",
            "When a file matching “src/*.py” is edited",
            "When an edit to “src/*.py” adds “TODO”",
            "When Edit is used",
        ]);
        expect(startWords({triggers: []})).toEqual(["Only when you or the agent start it"]);
    });

    it("sends only the fields a trigger's kind reads and names the first one missing", () => {
        expect(triggerBody({trigger_type: "file-text", pattern: " src/*.py ", text: "TODO", moment: "x", tool: ""})).toEqual({trigger_type: "file-text", pattern: "src/*.py", text: "TODO"});
        expect(triggersProblem([{trigger_type: "file-text", pattern: "src/*.py", text: ""}])).toBe("An edit adds a text: fill in text in the new content.");
        expect(triggersProblem([{trigger_type: "tool", tool: "Bash", pattern: ""}])).toBe("");
    });
});
