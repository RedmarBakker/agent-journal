// The visor is a screen of GRID.columns by GRID.rows square pixels, column 0 on the viewer's left and row 0 at the top, each off or lit
// in a colour; the figure draws whatever is lit (figure.js screenMaterial). The eyes and everything shown in their place are pictures
// on that grid, and each of their changes steps from one picture to the next: the frames of an animation.
export const GRID = {columns: 24, rows: 11};

// where an eye's pictures are centred on the grid: the figure's right eye on the viewer's left, its left on the right, both on the
// middle row; a picture that points one way, as the squeezed eye pointing in toward the nose, is turned round for the eye on the right
export const EYE_SPOTS = [
    {column: 6, row: 5, mirrored: false},
    {column: 17, row: 5, mirrored: true},
];

// The pictures, each a list of rows of the same length: "#" lit in its colour, "o" in its highlight, "." off
export const PICTURES = {
    eye_wide: ["..#####..", ".#######.", "##.....##", "#.......#", "#.......#", "#.......#"],
    eye_open: ["..#####..", ".#######.", "##.....##", "#.......#"],
    eye_narrowed: ["..#####..", ".##...##.", "##.....##"],
    eye_half: [".#######.", "##.....##"],
    eye_shut: [".#######."],
    heart_big: [".##...##.", "#o##.####", "#########", "#########", ".#######.", "..#####..", "...###...", "....#...."],
    heart_small: [".##.##.", "#o#####", "#######", ".#####.", "..###..", "...#..."],
    heart_tiny: ["##.##", "#####", ".###.", "..#.."],
    star_big: ["....#....", "....#....", "...###...", "####o####", ".#######.", "..#####..", "..##.##..", ".##...##.", ".#.....#."],
    star_twinkle: ["o...#...o", "....#....", "...###...", "####o####", ".#######.", "..#####..", "..##.##..", ".##...##.", "o#.....#o"],
    star_small: ["..#..", ".###.", "##o##", ".###.", ".#.#."],
    squeezed: ["##....", ".###..", "...##.", "....##", "...##.", ".###..", "##...."],
    z_small: ["###", "..#", ".#.", "#..", "###"],
    z_big: ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    cross: ["##.....##", "###...###", ".###.###.", "..#####..", "...###...", "..#####..", ".###.###.", "###...###", "##.....##"],
    tick: [".......##", "......###", ".....###.", "##..###..", "######...", ".####....", "..##....."],
};

// The frames each picture family steps through, each with the least size it takes: the eyes by how open they are, so a blink, a squint
// or a wide look steps from one to the next; the hearts by their beat and the stars by their sparkle, each growing in from nothing
export const FRAMES = {
    eyes: [["eye_shut", 0], ["eye_half", 0.25], ["eye_narrowed", 0.55], ["eye_open", 0.82], ["eye_wide", 1.25]],
    hearts: [["heart_tiny", 0.05], ["heart_small", 0.6], ["heart_big", 1.08]],
    stars: [["star_small", 0.05], ["star_big", 0.6], ["star_twinkle", 1.12]],
    z: [["z_small", 0.05], ["z_big", 1.5]],
};

// the frame of the family `name` for `size`: the last whose least size it reaches, or none below the first
export const frameFor = (name, size) => FRAMES[name].filter(([, least]) => size >= least).at(-1)?.[0] ?? null;

// The colours of the pictures, red, green and blue from 0 to 1, and their highlights
export const COLOURS = {
    eyes: [1, 0.94, 0.81],
    hearts: [1, 0.3, 0.5],
    heartLight: [1, 0.78, 0.86],
    stars: [1, 0.86, 0.3],
    starLight: [1, 1, 1],
};

// how many pixels an eye's glance moves it for a glance of its whole height
const EYE_HEIGHT = PICTURES.eye_open.length;

// The pixels lit for a face, each {column, row, colour}: `face` says how open the `eyes` are (Posing.eyes) and whether they show at all
// (`eyed`), their `shift` aside and up as shares of their height (Posing.eyeShift), their `tint`, and what takes their place: `hearts`,
// `stars` or `squeezed` at their size, or a run's end as a `sign` ({name, colour, strength}), shown as far up and down from the middle
// as its strength; and a Z above them while it is `dozing`, at its size
export function litPixels(face) {
    if (!face.eyed) return [];
    const shown = shownPicture(face);
    const eyes = shown ? EYE_SPOTS.flatMap((spot) => placed(shown, spot, face)) : [];
    const z = face.dozing > 0 ? placed({name: frameFor("z", face.dozing), colour: COLOURS.eyes, light: COLOURS.eyes, reach: 1}, Z_SPOT, face) : [];
    return [...eyes, ...z];
}

// where the Z of a figure dozing is centred on the grid: high up between the eyes, toward its left
export const Z_SPOT = {column: 13, row: 2, mirrored: false};

// the picture shown in each eye's place, its colours, how far it reaches up and down from its middle (1 the whole picture), whether it
// glances with the eyes, and whether it points one way
function shownPicture(face) {
    const sign = face.sign?.strength >= 0.25 ? face.sign : null;
    if (sign) return {name: sign.name, colour: sign.colour, light: sign.colour, reach: sign.strength};
    if (face.hearts > 0) return {name: frameFor("hearts", face.hearts), colour: COLOURS.hearts, light: COLOURS.heartLight, reach: 1};
    if (face.stars > 0) return {name: frameFor("stars", face.stars), colour: COLOURS.stars, light: COLOURS.starLight, reach: 1};
    if (face.squeezed > 0) return {name: "squeezed", colour: COLOURS.eyes, light: COLOURS.eyes, reach: 1, points: true};
    const open = face.eyes * (1 - (face.sign?.strength ?? 0));
    const colour = face.tint ?? COLOURS.eyes;
    return {name: frameFor("eyes", open), colour, light: colour, reach: 1, glances: true};
}

// the lit pixels of `shown` centred on `spot`, moved by the eyes' glance when it glances
function placed(shown, spot, face) {
    const rows = PICTURES[shown.name];
    const width = rows[0].length;
    const [aside, up] = shown.glances ? face.shift.map((part) => Math.round(part * EYE_HEIGHT)) : [0, 0];
    const left = spot.column - Math.floor(width / 2) + aside;
    const top = spot.row - Math.floor(rows.length / 2) - up;
    const middle = (rows.length - 1) / 2;
    const pixels = [];
    rows.forEach((line, y) => {
        if (Math.abs(y - middle) > (shown.reach * rows.length) / 2) return;
        [...line].forEach((mark, x) => {
            if (mark === ".") return;
            const column = left + (shown.points && spot.mirrored ? width - 1 - x : x);
            const row = top + y;
            if (column >= 0 && column < GRID.columns && row >= 0 && row < GRID.rows) pixels.push({column, row, colour: mark === "o" ? shown.light : shown.colour});
        });
    });
    return pixels;
}
