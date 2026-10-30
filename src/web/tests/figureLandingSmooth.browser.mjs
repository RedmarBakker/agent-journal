// Sample the browser's actual landing transform so touchdown, compression and recovery have no instantaneous scale or position jump.
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {chromium} from "playwright-core";
import {FALLS} from "../src/domain/falls.js";

const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage();
    await page.setContent("<div id='figure'></div>");
    await page.addStyleTag({content: readFileSync(new URL("../src/figure/falls.css", import.meta.url), "utf8")});
    const samples = await page.evaluate(async (falls) => {
        const result = [];
        for (const [voice, fall] of Object.entries(falls)) {
            const figure = document.body.appendChild(document.createElement("div"));
            const duration = fall.ms * 0.5;
            figure.style.cssText = `--squash:${fall.squash};--bounce:${fall.bounce}px;animation:figure-land ${duration}ms ease-out both;animation-play-state:paused`;
            const animation = figure.getAnimations()[0];
            await animation.ready;
            const at = (fraction) => {
                animation.currentTime = duration * fraction;
                const transform = new DOMMatrix(getComputedStyle(figure).transform);
                return [transform.a, transform.d, transform.e, transform.f];
            };
            result.push({voice, start: at(0), first: at(0.00001), squash: at(0.16), rebound: at(0.52), end: at(1), joins: [0.16, 0.52, 1].map((fraction) => [at(fraction - 0.00001), at(fraction)])});
            animation.cancel();
            figure.remove();
        }
        return result;
    }, FALLS);
    for (const sample of samples) {
        const {voice, start, first, squash, rebound, end, joins} = sample;
        assert.deepEqual(start, [1, 1, 0, 0], `${voice} starts from its unsquashed airborne shape`);
        assert.deepEqual(end, [1, 1, 0, 0], `${voice} settles back to identity`);
        assert.ok(Math.abs(squash[0] - 1 - FALLS[voice].squash) < 1e-6 && Math.abs(squash[1] - 1 + FALLS[voice].squash) < 1e-6, `${voice} retains its landing compression`);
        assert.ok(Math.abs(rebound[3] + FALLS[voice].bounce) < 1e-6, `${voice} retains its rebound height`);
        for (const [before, after] of [[start, first], ...joins]) assert.ok(before.every((value, index) => Math.abs(value - after[index]) < 0.001), `${voice} meets each phase continuously`);
    }
    console.log(JSON.stringify({voices: samples.length, discontinuities: 0, samples}));
} finally {
    await browser.close();
}
