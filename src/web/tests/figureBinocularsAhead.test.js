// @vitest-environment node
import {expect, test} from "vitest";
import {BINOCULAR_HOLD, SCREEN_INSET} from "../src/figure/figure.js";

// the visor's glass is at most about 0.9 of the figure's units ahead of the model's eye points, so the eyepieces held `ahead` of the eyes
// must lie beyond it, or the screen drawn over the body hides the barrels and the hands under them
const GLASS_AHEAD_OF_EYES = 0.9;

test("the binoculars are held beyond the visor's glass, so the screen never covers the barrels or the hands under them", () => {
    expect(BINOCULAR_HOLD.ahead).toBeGreaterThanOrEqual(GLASS_AHEAD_OF_EYES);
    expect(SCREEN_INSET.depth).toBeGreaterThan(0);
});
