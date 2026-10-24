import {draw} from "./pile.js";

// The figure's visor lit as a screen when a process card ends, red for one that ends bad and green for one that ends good, coming on as an
// old CRT television powers up and never while the figure sleeps. Over `seconds`: the eyes go out over `eyesOut`; a bright line comes on
// across the middle, widening out from its centre over `line`; the line opens out top and bottom to fill the visor over `open`, its white
// flash fading into the colour by the end of `flash`; the glow holds, fades over `fade`, and the eyes come back over `eyesBack`. Its red
// and green are its own, a glowing screen's, brighter to the core by `core` and with a soft halo about the visor as strong as `halo`, and the
// server units' lights shine in the same two. It lights only once the figure has turned its head to the chat mark of the run that ended
// (lightOnce), or `waits` on when it cannot. Every number of it is here, in seconds.
export const VISOR = {
    seconds: 2.4, waits: 1.5, looks: 1, eyesOut: 0.14, line: [0.14, 0.3], open: [0.3, 0.52], flash: [0.3, 0.7], fade: 0.35, eyesBack: 0.15, thin: 0.05,
    colours: {bad: [1, 0.06, 0.1], good: [0.08, 1, 0.32]}, core: 0.45, halo: 0.75,
};

// Now and then a run's end shows in the eyes themselves instead (pile.js run_end): two red crosses for a failure, two green ticks for a
// pass, glowing in the visor's own red and green. Over `seconds` they come on as an old CRT warms up, flickering on and off `flickers`
// times over `flicker`, each time a little brighter; flash white and bright over `flash`, settling into their colour; hold; and fade back
// into the usual eyes over `fade`.
export const SIGN = {seconds: 2.4, flicker: [0, 0.6], flickers: 4, flash: [0.6, 0.9], fade: [1.95, 2.4], dim: 0.12, signs: {bad: "cross", good: "tick"}};

const span = (k, from, to) => Math.min(Math.max((k - from) / (to - from), 0), 1);
const ease = (k) => k * k * (3 - 2 * k);

// How the visor stands `seconds` after it lit up, or null once its time is over: how much of the eyes still shows, 0 to 1; how far the
// lit band reaches across the visor from its centre and how far it has opened up and down from the middle, shares of the visor; how
// white its flash still is; and how strong the glow is, the band dark at 0
export function crtAt(seconds) {
    if (seconds < 0 || seconds >= VISOR.seconds) return null;
    const off = VISOR.seconds - VISOR.eyesBack;
    return {
        eyes: Math.max(1 - span(seconds, 0, VISOR.eyesOut), span(seconds, off, VISOR.seconds)),
        across: ease(span(seconds, ...VISOR.line)),
        open: VISOR.thin + (1 - VISOR.thin) * ease(span(seconds, ...VISOR.open)),
        flash: seconds < VISOR.flash[0] ? 1 : 1 - ease(span(seconds, ...VISOR.flash)),
        glow: seconds < VISOR.line[0] ? 0 : 1 - ease(span(seconds, off - VISOR.fade, off)),
    };
}

// How the sign in the eyes stands `seconds` after it came on, or null once its time is over: how far the eyes are the sign rather than
// their usual shape, 0 to 1; how brightly it glows, 0 to 1; and how white its flash still is
export function signAt(seconds) {
    if (seconds < 0 || seconds >= SIGN.seconds) return null;
    const warming = span(seconds, ...SIGN.flicker);
    const on = Math.floor(warming * SIGN.flickers * 2) % 2 === 0;
    const lit = seconds < SIGN.flicker[1] ? (on ? 0.35 + 0.5 * warming : SIGN.dim) : 1;
    return {strength: 1 - ease(span(seconds, ...SIGN.fade)), lit, white: seconds < SIGN.flash[0] ? 0 : 1 - ease(span(seconds, ...SIGN.flash))};
}

// how far the figure turns toward the viewer while its visor is lit or its eyes are a sign, 0 to 1 (figure.js turnToViewer): round as its
// eyes go out, held all the while it glows, and back as the glow fades and the eyes return
export const glowTurn = (crt) => Math.max(crt.glow, 1 - crt.eyes, crt.sign?.strength ?? 0);

// The visor as the page draws it `now` seconds, for a glow `lit` ({tone, at, sign, card, since}) or none, dark while it waits to light, while the figure is `asleep` or not: its
// colour with how it stands (crtAt), or, for a sign, the visor dark and the eyes the sign of its tone as it stands (signAt); null when it
// shows the eyes
export function visorAt(lit, now, asleep) {
    if (!lit || lit.at === null || asleep) return null;
    if (lit.sign) {
        const sign = signAt(now - lit.at);
        return sign && {colour: VISOR.colours[lit.tone], eyes: 1, across: 0, open: 0, flash: 0, glow: 0, sign: {name: SIGN.signs[lit.tone], ...sign}};
    }
    const crt = crtAt(now - lit.at);
    return crt && {colour: VISOR.colours[lit.tone], ...crt};
}

// The glow a process card ending lights, from `ends` (figureState.js processEndsAfter), the newest of them, or `lit` as it was: waiting
// since `now` to light, its `at` null, while the figure turns to the run's chat mark `card`; whether it shows as a sign in the eyes is
// drawn from the pile with `random` (pile.js run_end)
export function visorFor(ends, lit, now, random = Math.random) {
    if (!ends.length) return lit;
    return {tone: ends.at(-1).tone, at: null, since: now, card: ends.at(-1).card, sign: draw({moment: "run_end"}, random)?.name === "sign"};
}

// The glow `lit` lit `now` once the figure has faced what told it of its run's end, its chat mark or the docked bar, `faces`, for VISOR
// looks seconds on end, or `waits` seconds after the run ended when it never faces it; as it was otherwise, noting when it began to face it
export function lightOnce(lit, faces, now) {
    if (!lit || lit.at !== null) return lit;
    const facedAt = faces ? (lit.facedAt ?? now) : null;
    if ((facedAt !== null && now - facedAt >= VISOR.looks) || (facedAt === null && now - lit.since >= VISOR.waits)) return {...lit, at: now};
    return {...lit, facedAt};
}

// The visor through a disco dance `u` of the way through it (acts.js disco): lit as a screen all the dance long, its colour stepping round
// the colour wheel each beat, the eyes out but at the dance's first and last few frames
export function discoScreen(u, beats) {
    const step = Math.floor(u * beats * 2);
    const hue = ((step * 137) % 360) / 360;
    const k = (n) => (n + hue * 12) % 12;
    const part = (n) => 0.5 - 0.5 * Math.max(-1, Math.min(k(n) - 3, 9 - k(n), 1));
    const shown = Math.min(u / 0.06, (1 - u) / 0.06, 1);
    return {colour: [part(0), part(8), part(4)], eyes: 1 - shown, across: shown, open: shown, flash: 0, glow: shown};
}
