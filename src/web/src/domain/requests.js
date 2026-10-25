// What a request its filer asked stands at, in one line: its state and why when it was declined, who it is for, who drives it, and when it was done.
export function standingLine(task) {
    const state = task.reason ? `${task.standing}: ${task.reason}` : task.standing || task.state;
    return [state, task.for_whom && `for ${task.for_whom}`, task.driver && `driven by ${task.driver}`, task.done_at && `done ${task.done_at.replace("T", " ").slice(0, 16)}`].filter(Boolean).join(" · ");
}
