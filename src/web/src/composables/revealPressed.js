// How far a pane scrolls so a bubble that grew is seen whole above the pane's foot, where the docks and the composer begin; a bubble taller
// than the pane is brought only as far as its top. None when it is already in view.
export function revealOffset(turn, pane, margin = 8) {
    const below = turn.bottom - pane.bottom;
    if (below <= 0) return 0;
    return Math.max(0, Math.min(below + margin, turn.top - pane.top - margin));
}

const REVEAL_MS = 1500;

// The bubble the reader pressed, so that when it opens, as a chat mark or a card does on a click, the pane scrolls up until it is seen whole;
// one helper for every kind of bubble in the thread.
export function useRevealPressed(scroller) {
    let pressed = null;
    let pressedAt = 0;

    function press(event) {
        pressed = event.target?.closest?.(".thread-turn") || null;
        pressedAt = Date.now();
    }

    function reveal() {
        const pane = scroller.value;
        if (!pane || !pressed || !pressed.isConnected || Date.now() - pressedAt > REVEAL_MS) return;
        const offset = revealOffset(pressed.getBoundingClientRect(), pane.getBoundingClientRect());
        if (offset) pane.scrollTo({top: pane.scrollTop + offset, behavior: "smooth"});
    }

    return {press, reveal};
}
