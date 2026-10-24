import {rowsOf} from "../domain/plans.js";
import {watchEffect} from "vue";
import {holding, rows} from "../sync/rows.js";
import {wholePlans} from "./wholePlans.js";

// The tasks of these plans, read when the viewer does not hold them yet; a plan held as a list row alone names none, so it is read whole first.
export function usePlanRows(plans) {
    wholePlans(() => plans().map((p) => p.id));
    watchEffect(() => {
        const known = new Set(rows("tasks").map((t) => t.id));
        const missing = plans()
            .flatMap(rowsOf)
            .filter((id) => !known.has(id));
        if (missing.length) holding("tasks", missing).catch((error) => console.error(error));
    });
}
