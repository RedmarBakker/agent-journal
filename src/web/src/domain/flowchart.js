const NODE = {width: 160, height: 40, across: 200, down: 90, margin: 20};

// The drawing of a flowchart from its arrows, each [from, to, label]: a box for every name, a row for every step from the top, and an arrow
// between boxes; the top is every name no arrow leads to, or the first name when the arrows go round in a ring
export function layoutOf(edges) {
    const names = [...new Set(edges.flatMap(([from, to]) => [from, to]))];
    const led = new Set(edges.map(([, to]) => to));
    const tops = names.filter((name) => !led.has(name));
    const depth = new Map((tops.length ? tops : names.slice(0, 1)).map((name) => [name, 0]));
    for (const [name, at] of depth) edges.filter(([from]) => from === name).forEach(([, to]) => depth.has(to) || depth.set(to, at + 1));
    const rows = [];
    names.forEach((name) => (rows[depth.get(name) ?? 0] ||= []).push(name));
    const widest = Math.max(...rows.map((row) => row.length));
    const width = widest * NODE.across + NODE.margin * 2;
    const placed = new Map();
    rows.forEach((row, level) =>
        row.forEach((name, index) => placed.set(name, {name, x: (width - row.length * NODE.across) / 2 + index * NODE.across + (NODE.across - NODE.width) / 2, y: NODE.margin + level * NODE.down}))
    );
    const arrows = edges.map(([from, to, label]) => {
        const start = placed.get(from);
        const end = placed.get(to);
        return {from, to, label, x1: start.x + NODE.width / 2, y1: start.y + NODE.height, x2: end.x + NODE.width / 2, y2: end.y};
    });
    return {width, height: NODE.margin * 2 + (rows.length - 1) * NODE.down + NODE.height, size: NODE, nodes: [...placed.values()], arrows};
}
