import {expect, test} from "vitest";
import {buttonSpot} from "../src/domain/commentButton.js";
import {fileComment} from "../src/format/quote.js";

const field = {left: 100, right: 700, top: 50};
const window = {width: 1200};

test("the Comment button is centered over a selection that lies inside the field", () => {
    expect(buttonSpot({left: 200, right: 300, top: 120}, field, window)).toEqual({x: 150, y: 70});
});

test("a selection running past the edge of the field puts the button in the middle of what is visible", () => {
    expect(buttonSpot({left: 150, right: 5000, top: 120}, field, window)).toEqual({x: 325, y: 70});
    expect(buttonSpot({left: -400, right: 5000, top: 120}, field, window)).toEqual({x: 300, y: 70});
});

test("a field wider than the window is centered on the window's part of it, and a selection above the window sits at its top", () => {
    expect(buttonSpot({left: 0, right: 5000, top: -300}, {left: 100, right: 3000, top: -500}, window)).toEqual({x: 550, y: 500});
});

test("a comment on a file's lines is sent as the message's text, so it reaches the chat", () => {
    const sent = fileComment({path: "src/app.py", text: "a\nb\nc"}, {first: 2, last: 3, text: "b\nc"}, " why this? ");
    expect(Object.keys(sent)).toEqual(["text"]);
    expect(sent.text).toBe("About src/app.py, lines 2-3:\n\n> b\n> c\n\nwhy this?");
});
