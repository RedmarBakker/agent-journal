import {patched} from "../sync/rows.js";

// Takes a message down from above the chat: drawn undocked at once, and told to the journal through the scope's own address.
export function undock(scope, message) {
    patched(
        message,
        (row) => (row.data = {...row.data, docked: false}),
        () => scope.api.act("messages", message.id, "undock")
    );
}

// Keeps a card the journal docked by itself above the chat once the user has opened it: it no longer leaves when its run ends,
// only when the user closes it.
export function keepDocked(scope, message) {
    patched(
        message,
        (row) => (row.data = {...row.data, auto_docked: false, undock_at: null}),
        () => scope.api.act("messages", message.id, "dock")
    );
}

// Holds a card the journal docked by itself in place while the user points at it, in this viewer alone: its time to close waits
// until the pointer leaves, and then goes on for as long as it had left.
export function holdDock(message) {
    message.data = {...message.data, held_at: Date.now() / 1000};
}

export function releaseDock(message) {
    const {held_at: since, ...data} = message.data;
    message.data = {...data, undock_at: data.undock_at && data.undock_at + (Date.now() / 1000 - since)};
}
