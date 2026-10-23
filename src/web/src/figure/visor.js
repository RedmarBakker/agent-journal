// The figure's visor lit as a screen when a process card ends: red for one that ends bad, green for one that ends good, glowing for about
// `seconds`, coming on over `rise` and going back to the eyes over `fade`, never while the figure sleeps. Every number of it is here.
export const VISOR = {seconds: 2, rise: 0.15, fade: 0.4, colours: {bad: [1, 0.16, 0.14], good: [0.18, 1, 0.38]}};

// how lit the visor is `seconds` after it lit up, 0 to 1, and 0 once its time is over
export function visorLit(seconds) {
    if (seconds < 0 || seconds >= VISOR.seconds) return 0;
    return Math.min(seconds / VISOR.rise, 1, (VISOR.seconds - seconds) / VISOR.fade);
}

// The visor as the page draws it `now` seconds, for a glow `lit` ({tone, at}) or none, while the figure is `asleep` or not: its colour and
// how lit it is, or null when it shows the eyes
export function visorAt(lit, now, asleep) {
    const amount = lit && !asleep ? visorLit(now - lit.at) : 0;
    return amount > 0 ? {colour: VISOR.colours[lit.tone], amount} : null;
}

// The glow a process card ending lights, from `ends` (figureState.js processEndsAfter), the newest of them, or `lit` as it was
export const visorFor = (ends, lit, now) => (ends.length ? {tone: ends.at(-1).tone, at: now} : lit);
