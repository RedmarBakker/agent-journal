// Intro and outro frames are not part of a held loop.
export function frameIn(clip, index, closing = null) {
    if (!clip.loops) return Math.min(index, clip.frames - 1);
    const intro = clip.intro || 0;
    const outro = clip.outro || 0;
    if (closing !== null && index >= closing) return Math.min(clip.frames - outro + index - closing, clip.frames - 1);
    return index < intro ? index : intro + ((index - intro) % (clip.frames - intro - outro));
}

// The frame of a clip `index` frames in when `stretch` ({from, to, extra}) holds a part of it longer: as it is up to frame `to`, then its
// frames `from` to `to` over again for `extra` frames more, then the rest of it from `to` on
export function stretchedFrame(index, stretch) {
    if (!stretch || index < stretch.to) return index;
    const {from, to, extra} = stretch;
    return index < to + extra ? from + ((index - to) % (to - from)) : index - extra;
}

// Close at a resting page, not halfway through a turn.
export function closeAt(clip, index) {
    const intro = clip.intro || 0;
    const unit = clip.leaves || clip.frames - intro - (clip.outro || 0);
    return intro + Math.ceil(Math.max(index - intro, 0) / unit) * unit;
}

// whether a clip on screen `seconds` has played the least it plays (figure.js CLIPS least)
export const playedLeast = (clip, seconds) => seconds >= (clip.least ?? 0);

// Whether the clip on screen gives way to another that is wanted: never before it has played its least, at once when it is interruptible
// (figure.js CLIPS), else once it has played out, between the frame it was at when last drawn, `last`, and the frame it is at now, `index`
export function canSwitch(clip, index, last) {
    if (!playedLeast(clip, index / clip.fps)) return false;
    if (clip.interruptible) return true;
    if (!clip.loops) return index >= clip.frames;
    const unit = clip.leaves || clip.frames;
    return Math.floor(index / unit) > Math.floor(last / unit);
}
