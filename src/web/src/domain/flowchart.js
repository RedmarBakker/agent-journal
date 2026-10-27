// The sizes a flowchart is laid out with, in the drawing's own units: a card's padding, its widest line in characters and the width of
// one character, the gaps between cards side by side and between rows, and the margin round the whole drawing
const CARD = {padX: 14, padY: 10, line: 17, lineChars: 24, charWidth: 7.4, minWidth: 120};
const LABEL = {lineChars: 28, charWidth: 6.4, line: 14, pad: 4};
const GAP = {across: 48, down: 110, margin: 32, loop: 36};
const ORDER_SWEEPS = 6;

// a text broken into lines of at most `most` characters, at spaces, a word longer than that on a line of its own
export function wrapped(text, most) {
    const lines = [];
    for (const word of String(text).split(/\s+/).filter(Boolean)) {
        const last = lines.at(-1);
        if (last !== undefined && last.length + 1 + word.length <= most) lines[lines.length - 1] = `${last} ${word}`;
        else lines.push(word);
    }
    return lines.length ? lines : [""];
}

const cardOf = (name) => {
    const lines = wrapped(name, CARD.lineChars);
    const width = Math.max(CARD.minWidth, Math.max(...lines.map((line) => line.length)) * CARD.charWidth + CARD.padX * 2);
    return {name, lines, line: CARD.line, padY: CARD.padY, width, height: lines.length * CARD.line + CARD.padY * 2};
};

// the arrows that close a ring, found by a walk from each top: an arrow back to a name still on the walk's path
function backArrows(names, edges, tops) {
    const back = new Set();
    const state = new Map();
    const visit = (name) => {
        state.set(name, "open");
        edges.forEach((edge, index) => {
            if (edge[0] !== name) return;
            const seen = state.get(edge[1]);
            if (seen === "open") back.add(index);
            else if (!seen) visit(edge[1]);
        });
        state.set(name, "done");
    };
    [...tops, ...names].forEach((name) => state.has(name) || visit(name));
    return back;
}

// each name's row: the longest way down to it from a top, the arrows that close a ring left out
function rowsOf(names, forward) {
    const row = new Map(names.map((name) => [name, 0]));
    for (let pass = 0; pass < names.length; pass++) {
        let moved = false;
        forward.forEach(([from, to]) => {
            if (row.get(to) < row.get(from) + 1) {
                row.set(to, row.get(from) + 1);
                moved = true;
            }
        });
        if (!moved) break;
    }
    return row;
}

// the names of each row in an order that crosses few arrows: each sweep sorts a row by where its neighbours in the row before, then after,
// stand on average
function orderedRows(names, forward, row) {
    const rows = [];
    names.forEach((name) => (rows[row.get(name)] ||= []).push(name));
    const place = () => new Map(rows.flatMap((names) => names.map((name, index) => [name, index])));
    const sorted = (names, neighbours) => {
        const at = place();
        const centre = (name) => {
            const near = neighbours(name).map((other) => at.get(other));
            return near.length ? near.reduce((a, b) => a + b, 0) / near.length : at.get(name);
        };
        return [...names].sort((a, b) => centre(a) - centre(b));
    };
    for (let sweep = 0; sweep < ORDER_SWEEPS; sweep++) {
        const down = sweep % 2 === 0;
        const indexes = rows.map((_, index) => index);
        (down ? indexes.slice(1) : indexes.slice(0, -1).reverse()).forEach((index) => {
            const neighbours = (name) => forward.filter((edge) => edge[down ? 1 : 0] === name).map((edge) => edge[down ? 0 : 1]);
            rows[index] = sorted(rows[index], neighbours);
        });
    }
    return rows;
}

// where an arrow leaves or enters a card: arrows on one side of a card are spread along it in the order of the cards at their other ends
function ports(arrows, placed, end) {
    const side = new Map();
    arrows.forEach((arrow) => {
        const key = `${arrow[end]}:${arrow.back ? "side" : end === "from" ? "bottom" : "top"}`;
        (side.get(key) || side.set(key, []).get(key)).push(arrow);
    });
    const other = end === "from" ? "to" : "from";
    for (const list of side.values()) {
        list.sort((a, b) => placed.get(a[other]).x - placed.get(b[other]).x);
        list.forEach((arrow, index) => (arrow[`${end}Share`] = (index + 1) / (list.length + 1)));
    }
}

// The drawing of a flowchart from its arrows, each [from, to, label]: a card for every name, sized to hold its words wrapped, in rows from the
// tops down, ordered to cross few arrows; an arrow down from a card's bottom to the next card's top, spread along both edges so no two meet,
// and an arrow that closes a ring drawn round the right of the cards it passes; each arrow's words wrapped beside its middle
export function layoutOf(edges) {
    const names = [...new Set(edges.flatMap(([from, to]) => [from, to]))];
    const led = new Set(edges.map(([, to]) => to));
    const tops = names.filter((name) => !led.has(name));
    const back = backArrows(names, edges, tops.length ? tops : names.slice(0, 1));
    const forward = edges.filter((_, index) => !back.has(index));
    const row = rowsOf(names, forward);
    const rows = orderedRows(names, forward, row);
    const cards = new Map(names.map((name) => [name, cardOf(name)]));
    const rowWidths = rows.map((names) => names.reduce((sum, name) => sum + cards.get(name).width, 0) + GAP.across * (names.length - 1));
    const width = Math.max(...rowWidths) + GAP.margin * 2 + GAP.loop * 2;
    const placed = new Map();
    let y = GAP.margin;
    rows.forEach((names, index) => {
        let x = (width - rowWidths[index]) / 2;
        const tallest = Math.max(...names.map((name) => cards.get(name).height));
        names.forEach((name) => {
            const card = cards.get(name);
            placed.set(name, {...card, x, y: y + (tallest - card.height) / 2});
            x += card.width + GAP.across;
        });
        y += tallest + GAP.down;
    });
    const arrows = edges.map(([from, to, label], index) => ({from, to, label: label || "", back: back.has(index) || row.get(to) <= row.get(from)}));
    ports(arrows, placed, "from");
    ports(arrows, placed, "to");
    const right = width - GAP.margin;
    const drawn = arrows.map((arrow, index) => drawnArrow(arrow, placed.get(arrow.from), placed.get(arrow.to), right - (index % 3) * 10));
    const nodes = [...placed.values()];
    const spread = spreadLabels(drawn, nodes);
    const lowest = Math.max(y - GAP.down, ...spread.filter((arrow) => arrow.label).map((arrow) => arrow.label.y + arrow.label.height));
    const widest = Math.max(width - GAP.margin, ...spread.filter((arrow) => arrow.label).map((arrow) => arrow.label.x + arrow.label.width));
    return {width: widest + GAP.margin, height: lowest + GAP.margin, nodes, arrows: spread};
}

function drawnArrow(arrow, start, end, right) {
    const lines = arrow.label ? wrapped(arrow.label, LABEL.lineChars) : [];
    const labelWidth = lines.length ? Math.max(...lines.map((line) => line.length)) * LABEL.charWidth + LABEL.pad * 2 : 0;
    const labelHeight = lines.length * LABEL.line + (lines.length ? LABEL.pad * 2 : 0);
    if (arrow.back) {
        const x1 = start.x + start.width;
        const y1 = start.y + start.height * arrow.fromShare;
        const x2 = end.x + end.width;
        const y2 = end.y + end.height * arrow.toShare;
        const reach = Math.max(right, x1 + GAP.loop, x2 + GAP.loop);
        return {...arrow, lines, labelWidth, labelHeight, path: `M${x1} ${y1} C${reach} ${y1} ${reach} ${y2} ${x2} ${y2}`, mid: {x: reach - labelWidth / 2, y: (y1 + y2) / 2}};
    }
    const x1 = start.x + start.width * arrow.fromShare;
    const y1 = start.y + start.height;
    const x2 = end.x + end.width * arrow.toShare;
    const y2 = end.y;
    const bend = (y2 - y1) / 2;
    return {...arrow, lines, labelWidth, labelHeight, path: `M${x1} ${y1} C${x1} ${y1 + bend} ${x2} ${y2 - bend} ${x2} ${y2}`, mid: {x: (x1 + x2) / 2, y: (y1 + y2) / 2}};
}

// each arrow's words in a box at its middle, moved down past any card or box already placed that it would overlap
function spreadLabels(arrows, nodes) {
    const boxes = nodes.map(({x, y, width, height}) => ({x, y, width, height}));
    return arrows.map((arrow) => {
        if (!arrow.lines.length) return {...arrow, label: null};
        const box = {x: arrow.mid.x - arrow.labelWidth / 2, y: arrow.mid.y - arrow.labelHeight / 2, width: arrow.labelWidth, height: arrow.labelHeight};
        while (boxes.some((other) => overlaps(box, other))) box.y += LABEL.line;
        boxes.push(box);
        return {...arrow, label: {...box, lines: arrow.lines, line: LABEL.line, pad: LABEL.pad}};
    });
}

export const overlaps = (a, b) => a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height;
