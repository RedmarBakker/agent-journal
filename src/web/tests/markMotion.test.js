import {nextTick, ref} from "vue";
import {expect, test} from "vitest";
import {useMarkMotion} from "../src/composables/markMotion.js";

test("a mark's contents leave before it changes size, it changes size held from its old size, and the new contents come after", async () => {
    window.matchMedia = () => ({matches: false});
    const wanted = ref(true);
    const style = {};
    const el = {style, offsetWidth: 200, offsetHeight: 24};
    const steps = [];
    let release = () => {};
    const later = () => new Promise((done) => (release = done));
    const {folded, phase} = useMarkMotion(ref(el), () => wanted.value, later);
    wanted.value = false;
    await nextTick();
    steps.push([phase.value, folded.value, style.width, style.height]);
    el.offsetWidth = 560;
    el.offsetHeight = 120;
    release();
    await nextTick();
    await nextTick();
    await nextTick();
    steps.push([phase.value, folded.value, style.width, style.height]);
    release();
    await nextTick();
    await nextTick();
    steps.push([phase.value, folded.value, style.width, style.height]);
    expect(steps).toEqual([
        ["leaving", true, "200px", "24px"],
        ["resizing", false, "560px", "120px"],
        ["entering", false, "", ""],
    ]);
});
