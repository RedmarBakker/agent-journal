import {FRAMED} from "./frame.js";

// One complete walking cycle, shared by the foot solver and the distance travelled on the page.
export const GAIT = {length: 1.36, planted: 0.6, clearance: 0.16};

export const strideAtDistance = (distance, size) => size > 0 ? distance * FRAMED.height / (size * GAIT.length) : 0;
