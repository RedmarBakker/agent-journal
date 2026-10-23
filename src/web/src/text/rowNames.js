import {register} from "./index.js";
import {WORD_PATTERN, tableOfWord} from "../domain/tables.js";

const SKIPPED = /(<code>.*?<\/code>|<a\s.*?<\/a>|\[[^\]\n]*\]\([^)\s]*\))/gs;
// a row by its word and number, with a place in it after a colon: a line, a span of lines, or "section N"; or its number in parentheses, as in "the joining task (1463)"
const NAMED = new RegExp(`\\b(${WORD_PATTERN}) (?:#?(\\d+)(?::(\\d+(?:-\\d+)?|section \\d+))?\\b|\\((\\d+)\\))`, "gi");

const chips = (text) =>
    text.replace(
        NAMED,
        (whole, word, bare, at = "", enclosed) => {
            const id = bare || enclosed;
            return `<a class="row-pill" href="#" data-peek="${tableOfWord(word)}:${id}"${at ? ` data-sub="${at}"` : ""}>${word} <span class="row-pill-num">${id}${at ? `:${at}` : ""}</span></a>`;
        }
    );

register((text, context) =>
    context.rowNames === false
        ? text
        : text
              .split(SKIPPED)
              .map((part, i) => (i % 2 ? part : chips(part)))
              .join("")
);
