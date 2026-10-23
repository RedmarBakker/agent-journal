// The phone call's speech bubble (chat/ComicBubble.vue), drawn as a comic strip's. Its text is wrapped at `columns` characters a row over at
// most `rows` rows and cut there, set `size` pixels high on rows `line` apart, `glyph` pixels a character, `pad` inside the outline. The
// outline is inked `ink` pixels thick round a box with corners `round` across, with a tail `tail` wide at its base to `gap` short of the
// handset. Its lines boil: the outline is one of `drawings` drawings, the next every `every` of the figure's frames, each of its `points`
// up to `wobble` pixels off its true place.
export const COMIC_BUBBLE = {columns: 28, rows: 5, size: 11, line: 15, glyph: 6.3, pad: 10, ink: 1.6, round: 16, tail: 14, gap: 4, drawings: 3, every: 2, points: 48, wobble: 1.1};

// the call's lines wrapped into the bubble's rows, the first line's rows strong, the last row cut short with an ellipsis when there are more
export function bubbleRows(lines) {
    const all = lines.flatMap((line, index) => wrapped(line).map((text) => ({text, strong: index === 0})));
    if (all.length <= COMIC_BUBBLE.rows) return all;
    const last = all[COMIC_BUBBLE.rows - 1];
    return [...all.slice(0, COMIC_BUBBLE.rows - 1), {...last, text: `${last.text.slice(0, COMIC_BUBBLE.columns - 1).trimEnd()}…`}];
}

function wrapped(line) {
    const rows = [];
    let row = "";
    for (const word of line.split(" ")) {
        const longer = row ? `${row} ${word}` : word;
        if (longer.length <= COMIC_BUBBLE.columns) {
            row = longer;
            continue;
        }
        if (row) rows.push(row);
        row = word;
        while (row.length > COMIC_BUBBLE.columns) {
            rows.push(row.slice(0, COMIC_BUBBLE.columns));
            row = row.slice(COMIC_BUBBLE.columns);
        }
    }
    return row ? [...rows, row] : rows;
}

// the bubble's box in pixels round `rows`
export function bubbleSize(rows) {
    const {glyph, line, pad} = COMIC_BUBBLE;
    return {width: Math.max(...rows.map((row) => row.text.length)) * glyph + 2 * pad, height: rows.length * line + 2 * pad};
}

// which drawing of the boiling outline is shown at the figure's frame `frame`
export const boilAt = (frame) => Math.floor(frame / COMIC_BUBBLE.every) % COMIC_BUBBLE.drawings;

// the outline of a `width` by `height` bubble and of its tail to `tip`, in the bubble's own pixels, as drawing `drawing` of the boil
export function bubbleOutline(width, height, tip, drawing) {
    const points = Array.from({length: COMIC_BUBBLE.points}, (_, index) => {
        const {at, out} = roundedAt(width, height, index / COMIC_BUBBLE.points);
        const off = COMIC_BUBBLE.wobble * wobbleOf(drawing, index);
        return {x: at.x + out.x * off, y: at.y + out.y * off};
    });
    return {body: smoothThrough(points), tail: tailTo(width, height, tip, drawing)};
}

// a number from -1 to 1 for point `index` of drawing `drawing`, the same each time
function wobbleOf(drawing, index) {
    const value = Math.sin((drawing + 1) * 12.9898 + index * 78.233) * 43758.5453;
    return 2 * (value - Math.floor(value)) - 1;
}

// the point `share` of the way round the box's rounded outline, clockwise from its top left, and the way out of the box there
function roundedAt(width, height, share) {
    const round = Math.min(COMIC_BUBBLE.round, width / 2, height / 2);
    const across = width - 2 * round;
    const down = height - 2 * round;
    const arc = (Math.PI * round) / 2;
    const edges = [across, arc, down, arc, across, arc, down, arc];
    let left = share * edges.reduce((sum, each) => sum + each, 0);
    let edge = 0;
    while (left > edges[edge]) left -= edges[edge++];
    const corners = [[width - round, round], [width - round, height - round], [round, height - round], [round, round]];
    if (edge % 2 === 0) {
        const [x, y, out] = [[round + left, 0, {x: 0, y: -1}], [width, round + left, {x: 1, y: 0}], [width - round - left, height, {x: 0, y: 1}], [0, height - round - left, {x: -1, y: 0}]][edge / 2];
        return {at: {x, y}, out};
    }
    const [cx, cy] = corners[(edge - 1) / 2];
    const angle = -Math.PI / 2 + (Math.PI / 2) * ((edge - 1) / 2) + left / round;
    const out = {x: Math.cos(angle), y: Math.sin(angle)};
    return {at: {x: cx + round * out.x, y: cy + round * out.y}, out};
}

// a closed smooth path through `points`, each curve's handles a sixth of the way to its neighbours
function smoothThrough(points) {
    const at = (index) => points[(index + points.length) % points.length];
    const curves = points.map((point, index) => {
        const [before, next, after] = [at(index - 1), at(index + 1), at(index + 2)];
        const first = {x: point.x + (next.x - before.x) / 6, y: point.y + (next.y - before.y) / 6};
        const second = {x: next.x - (after.x - point.x) / 6, y: next.y - (after.y - point.y) / 6};
        return `C${hundredths(first.x)} ${hundredths(first.y)} ${hundredths(second.x)} ${hundredths(second.y)} ${hundredths(next.x)} ${hundredths(next.y)}`;
    });
    return `M${hundredths(points[0].x)} ${hundredths(points[0].y)} ${curves.join(" ")} Z`;
}

// the tail: its base on the bubble's bottom, inside the outline, under the bubble's end nearer `tip`, curving to `gap` short of the tip
function tailTo(width, height, tip, drawing) {
    const {tail, round, gap, wobble} = COMIC_BUBBLE;
    const middle = Math.min(Math.max(tip.x, round + tail), width - round - tail);
    const base = {x: middle, y: height - 2};
    const way = {x: tip.x - base.x, y: tip.y - base.y};
    const length = Math.hypot(way.x, way.y);
    const end = {x: tip.x - (way.x / length) * gap + wobble * wobbleOf(drawing, -1), y: tip.y - (way.y / length) * gap + wobble * wobbleOf(drawing, -2)};
    const bend = {x: (base.x + end.x) / 2, y: (base.y + end.y) / 2};
    const [from, to] = [base.x - tail / 2, base.x + tail / 2];
    return `M${hundredths(from)} ${hundredths(base.y)} Q${hundredths(bend.x - tail / 4)} ${hundredths(bend.y)} ${hundredths(end.x)} ${hundredths(end.y)} Q${hundredths(bend.x + tail / 4)} ${hundredths(bend.y)} ${hundredths(to)} ${hundredths(base.y)} Z`;
}

const hundredths = (value) => Math.round(value * 100) / 100;
