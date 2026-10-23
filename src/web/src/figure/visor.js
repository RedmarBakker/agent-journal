// The figure's visor lit as a screen when a process card ends, red for one that ends bad and green for one that ends good, coming on as an
// old CRT television powers up and never while the figure sleeps. Over `seconds`: the eyes go out over `eyesOut`; a bright line comes on
// across the middle, widening out from its centre over `line`; the line opens out top and bottom to fill the visor over `open`, its white
// flash fading into the colour by the end of `flash`; the glow holds, fades over `fade`, and the eyes come back over `eyesBack`. Its red
// and green are its own, a glowing screen's, brighter to the core by `core` and with a soft halo about the visor as strong as `halo`, and the
// server units' lights shine in the same two. Every number of it is here, in seconds.
export const VISOR = {
    seconds: 2.4, eyesOut: 0.14, line: [0.14, 0.3], open: [0.3, 0.52], flash: [0.3, 0.7], fade: 0.35, eyesBack: 0.15, thin: 0.05,
    colours: {bad: [1, 0.06, 0.1], good: [0.08, 1, 0.32]}, core: 0.45, halo: 0.75,
};

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

// The visor as the page draws it `now` seconds, for a glow `lit` ({tone, at}) or none, while the figure is `asleep` or not: its colour
// with how it stands (crtAt), or null when it shows the eyes
export function visorAt(lit, now, asleep) {
    const crt = lit && !asleep ? crtAt(now - lit.at) : null;
    return crt && {colour: VISOR.colours[lit.tone], ...crt};
}

// The glow a process card ending lights, from `ends` (figureState.js processEndsAfter), the newest of them, or `lit` as it was
export const visorFor = (ends, lit, now) => (ends.length ? {tone: ends.at(-1).tone, at: now} : lit);
