import {expect, test} from "vitest";
import {MODES, showsApprovalToggle} from "../src/domain/modes.js";

test("the plan bar's approval toggle is shown in orchestrator mode only", () => {
    expect(MODES.filter((mode) => showsApprovalToggle(mode.key)).map((mode) => mode.key)).toEqual(["orchestrator"]);
});
