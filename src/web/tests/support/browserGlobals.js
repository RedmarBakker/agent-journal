// what a browser has and jsdom lacks, set for every test file since each runs in a process of its own
globalThis.ResizeObserver ??= class {
    observe() {}

    unobserve() {}

    disconnect() {}
};
