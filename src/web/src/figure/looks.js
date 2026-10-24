// The figure's head turns by weighted looks blended with its act. Each frame it is handed the things it could look at, each a look
// {key, kind, point} of a kind with its weight in LOOKS; every act declares how strongly it keeps its own head (its clip's `head`, one of
// HEAD). The head turns toward the strongest look, blended with the act's own head pose by the two weights (headBlend), and a new
// strongest look takes over only once it has led for SWITCH_SECONDS (leadingLook), the head easing toward it as it turns
// (reactions.js gazeAfter), so it never swings between targets in a moment.

// The weight of each kind of look: the pointer tickling it, a finished run's mark or its docked bar it waits to light the visor for, the UFO
// or the crane carrying a box, the bubble it reads or holds its glass to, a new message in the chat, the box it builds or pushes, a
// picture it admires, a progress bar it chose to watch, and its own idle glances
export const LOOKS = {pointer: 8, run: 7, carrier: 6, reading: 5, message: 4, work: 3, picture: 2, bar: 2, glance: 1};

// How strongly an act keeps its own head: hardly at all walking or standing, somewhat through a gesture that moves it, and almost wholly
// where the act's head is part of what it does, as climbing the ladder, under the parachute, rummaging or thinking
export const HEAD = {free: 1, gestures: 3, holds: 30};

// how long a new strongest look must lead before the head takes it up, in seconds
export const SWITCH_SECONDS = 2;

// how long a new message is a look after it comes into the chat, in seconds
export const MESSAGE_SECONDS = 4;

// whether `clip` keeps its head as its act poses it, never turned to the viewer for a look
export const holdsHead = (clip) => clip.head >= HEAD.holds;

// how far the head turns from the act's own pose toward `look`, 0 to 1, for the clip `clip`: the look's weight against the act's
export const headBlend = (look, clip) => (look ? LOOKS[look.kind] / (LOOKS[look.kind] + clip.head) : 0);

// The look the head is on at `now` seconds, from what it was on, `leading` ({look, challenger, since} or none), and `looks`, the looks it
// could take this frame: the strongest of them; but while the look it is on is still among them, a new strongest takes over only once it
// has led for SWITCH_SECONDS, the head keeping meanwhile to the look it is on, moved to where that look is now
export function leadingLook(leading, looks, now) {
    if (!looks.length) return {look: null, challenger: "", since: now};
    const held = leading?.look && looks.find((look) => look.key === leading.look.key);
    const top = Math.max(...looks.map((look) => LOOKS[look.kind]));
    const strongest = held && LOOKS[held.kind] === top ? held : looks.find((look) => LOOKS[look.kind] === top);
    if (!held || held === strongest) return {look: strongest, challenger: "", since: now};
    const since = leading.challenger === strongest.key ? leading.since : now;
    if (now - since >= SWITCH_SECONDS) return {look: strongest, challenger: "", since: now};
    return {look: held, challenger: strongest.key, since};
}

// The figure's own idle glances: every `every` seconds or so, a glance of `lasts` seconds to a point `aside` of its picture to one side
// of its head and `up` of it above, as shares of the picture
export const GLANCE = {every: [6, 14], lasts: 1.6, aside: 0.9, up: 0.12};

// The glance `glance` ({at, side}, `at` the seconds it begins) as it is at `now`: kept until it is over, then the next drawn with `random`
export function glanceAfter(glance, now, random) {
    if (glance && now < glance.at + GLANCE.lasts) return glance;
    return {at: now + GLANCE.every[0] + random() * (GLANCE.every[1] - GLANCE.every[0]), side: random() < 0.5 ? -1 : 1};
}

// the point a glance looks at `now` beside a head at `head` on the page, in a picture `size` pixels high, or null outside it
export function glancePoint(glance, now, head, size) {
    if (!glance || now < glance.at || now >= glance.at + GLANCE.lasts) return null;
    return {x: head.x + glance.side * GLANCE.aside * size, y: head.y - GLANCE.up * size};
}
