const hasSize = (task) => Number.isInteger(task.size) && task.size > 0;

export function taskSizing(tasks) {
    const sized = tasks.filter(hasSize);
    const done = sized.filter((task) => task.state === "completed");
    return {
        taskCount: tasks.length,
        doneCount: tasks.filter((task) => task.state === "completed").length,
        totalPoints: sized.length ? sized.reduce((total, task) => total + task.size, 0) : null,
        donePoints: sized.length ? done.reduce((total, task) => total + task.size, 0) : null,
        sizedTasks: sized.length,
        unknownTasks: tasks.length - sized.length,
    };
}

export function pointLabel(plan) {
    const points = plan.story_points || {};
    const sized = points.sized_tasks;
    const known = points.total;
    if (!Number.isInteger(sized) || sized <= 0 || !Number.isInteger(known) || known <= 0) return "Size unknown";
    const done = Number.isInteger(points.done) && points.done >= 0 ? points.done : 0;
    return `${done} of ${known} points done${points.unknown_tasks ? ` · ${points.unknown_tasks} ${points.unknown_tasks === 1 ? "task" : "tasks"} size unknown` : ""}`;
}

export function sprintPointLabel(plans) {
    const total = plans.reduce((sum, plan) => {
        const points = plan.story_points || {};
        return Number.isInteger(points.total) && points.total > 0 && Number.isInteger(points.sized_tasks) && points.sized_tasks > 0 ? sum + points.total : sum;
    }, 0);
    const unknown = plans.reduce((sum, plan) => {
        const points = plan.story_points || {};
        const counted = Number.isInteger(points.unknown_tasks) && points.unknown_tasks >= 0 ? points.unknown_tasks : 0;
        const known = Number.isInteger(points.total) && points.total > 0 && Number.isInteger(points.sized_tasks) && points.sized_tasks > 0;
        return sum + (known ? counted : Math.max(counted, plan.tasks?.length || 1));
    }, 0);
    if (total && unknown) return `${total} points · ${unknown} ${unknown === 1 ? "task" : "tasks"} size unknown`;
    if (total) return `${total} points`;
    if (unknown) return `${unknown} ${unknown === 1 ? "task" : "tasks"} size unknown`;
    return "Size unknown";
}
