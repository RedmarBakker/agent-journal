export const PUSH_MS = 280;
export const FADE_MS = 240;
const SLIDE_PX = 14;
const EASE = "cubic-bezier(0.2, 0.8, 0.2, 1)";

// A turn that arrives while the reader follows the foot: the chat first glides up by the turn's height, the turn still unseen in the room
// being made (the pane held at its foot every frame), and only then the turn fades in and slides up from a little below into that room.
// A reader who is away sees nothing move: `done` is called at once. `frame` and `clock` are the page's own, given so a test can step them.
export function arrive(el, {pane, follows, frame = requestAnimationFrame, clock = () => performance.now()}, done) {
    if (!pane || !follows()) return done();
    const height = el.offsetHeight;
    Object.assign(el.style, {boxSizing: "border-box", height: "0px", overflow: "hidden", opacity: "0", transform: `translateY(${SLIDE_PX}px)`});
    void el.offsetHeight;
    el.style.transition = `height ${PUSH_MS}ms ${EASE}`;
    el.style.height = `${height}px`;
    const began = clock();
    let fading = false;
    const hold = () => {
        if (follows()) pane.scrollTop = pane.scrollHeight;
        const elapsed = clock() - began;
        if (!fading && elapsed >= PUSH_MS) {
            fading = true;
            el.style.transition = `opacity ${FADE_MS}ms ease-out, transform ${FADE_MS}ms ${EASE}`;
            el.style.opacity = "1";
            el.style.transform = "translateY(0)";
        }
        if (elapsed < PUSH_MS + FADE_MS) return frame(hold);
        Object.assign(el.style, {boxSizing: "", height: "", overflow: "", opacity: "", transform: "", transition: ""});
        done();
    };
    frame(hold);
}
