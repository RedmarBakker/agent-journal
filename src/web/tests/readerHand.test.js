import {expect, test} from "vitest";
import {isScrollbarPress, wheelsInside} from "../src/domain/readerHand.js";

const sized = (element, {scrollHeight, clientHeight, scrollTop = 0, clientWidth = 300, overflowY = "auto"}) => {
    Object.defineProperties(element, {
        scrollHeight: {value: scrollHeight, configurable: true},
        clientHeight: {value: clientHeight, configurable: true},
        clientWidth: {value: clientWidth, configurable: true},
        scrollTop: {value: scrollTop, writable: true, configurable: true},
    });
    element.style.overflowY = overflowY;
    return element;
};

test("only a press on the chat's own scrollbar counts as the reader's hand on the chat, never a click inside it", () => {
    const pane = sized(document.createElement("div"), {scrollHeight: 2000, clientHeight: 500});
    const bubble = document.createElement("p");
    pane.append(bubble);
    expect(isScrollbarPress({target: pane, offsetX: 305}, pane), "the scrollbar, past the content's width").toBe(true);
    expect(isScrollbarPress({target: pane, offsetX: 120}, pane), "the pane's own padding").toBe(false);
    expect(isScrollbarPress({target: bubble, offsetX: 305}, pane), "a click on a bubble").toBe(false);
});

test("a wheel up over a code block that can still scroll up moves the block, not the chat", () => {
    const pane = sized(document.createElement("div"), {scrollHeight: 2000, clientHeight: 500});
    const block = sized(document.createElement("pre"), {scrollHeight: 400, clientHeight: 100, scrollTop: 50});
    const line = document.createElement("code");
    block.append(line);
    pane.append(block);
    document.body.append(pane);
    expect(wheelsInside({target: line, deltaY: -40}, pane)).toBe(true);
    block.scrollTop = 0;
    expect(wheelsInside({target: line, deltaY: -40}, pane), "a block already at its top passes the wheel to the chat").toBe(false);
    const plain = document.createElement("span");
    pane.append(plain);
    expect(wheelsInside({target: plain, deltaY: -40}, pane), "a wheel over plain text moves the chat").toBe(false);
    pane.remove();
});
