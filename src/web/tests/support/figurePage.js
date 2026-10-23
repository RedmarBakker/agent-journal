// The page a figure test reads its floors from: a chat, its scrolled view and the compose box, with one bubble the test moves.
export const CHAT = {left: 200, top: 100, right: 900, bottom: 800};
export const VIEW = {left: 200, top: 100, right: 900, bottom: 540};
export const boxed = (box) => ({getBoundingClientRect: () => ({width: box.right - box.left, height: box.bottom - box.top, ...box}), querySelector: () => null});

export function page(bubble) {
    globalThis.window = {innerWidth: 1280, innerHeight: 800};
    globalThis.CSS = {escape: (text) => text};
    const scroll = {...boxed(VIEW), querySelectorAll: () => [bubble]};
    const thread = {...boxed(CHAT), querySelector: (selector) => (selector === ".thread-scroll" ? scroll : null)};
    const home = {...boxed({left: 300, right: 700, top: 600, bottom: 720}), closest: () => thread};
    globalThis.document = {querySelector: (selector) => (selector === "[data-figure-home]" ? home : null), querySelectorAll: () => []};
}
