// Needs a browser and a running journal, so it is not in the default run: node src/web/tests/chatScroll.browser.mjs [viewer address]
// The chat's scroll, driven in a real browser on the live viewer: scrolled up past a quarter of its height, rows above grow, arrive and
// fold away, and the row being read keeps its place on screen to the pixel, nothing takes the reader to the foot, and the line of what
// the agent is doing fades; at the foot, what arrives carries the reader down and folds no docked mark; scrolled up within a quarter and
// left alone, it settles at the foot after five seconds and not before.
import {chromium} from "playwright-core";

const address = process.argv[2] || "http://127.0.0.1:8420/";
const browser = await chromium.launch();
const failures = [];
const expect = (holds, what) => holds || failures.push(what);

try {
    const page = await browser.newPage({viewport: {width: 1280, height: 800}});
    await page.goto(address);
    await page.waitForSelector(".thread-scroll [data-ref]", {timeout: 20000});
    await page.waitForTimeout(2000);

    // scrolled up past a quarter: rows above grow, a row is added above, and the row read is folded away; the view never moves
    const reading = await page.evaluate(async () => {
        const frame = () => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)));
        const box = document.querySelector(".thread-scroll");
        box.scrollTop = box.scrollHeight - box.clientHeight - box.clientHeight * 0.6;
        box.dispatchEvent(new Event("scroll"));
        await new Promise((done) => setTimeout(done, 400));
        const top = () => box.getBoundingClientRect().top;
        const rows = () => [...box.querySelectorAll("[data-ref]")];
        const shown = () => rows().find((el) => el.getBoundingClientRect().bottom > top() + 40);
        const drifts = [];
        let held = shown();
        let at = held.getBoundingClientRect().top;
        const measure = async () => {
            await frame();
            drifts.push(Math.round(held.getBoundingClientRect().top - at));
        };
        const above = rows()[rows().indexOf(held) - 2];
        const grown = Object.assign(document.createElement("div"), {style: "height: 140px"});
        above.appendChild(grown);
        await measure();
        const added = Object.assign(document.createElement("div"), {style: "height: 90px"});
        added.dataset.ref = "messages:0";
        above.before(added);
        await measure();
        // the row read is folded away: what stays in view above it keeps its place, and what came after moves up into its room
        const before = rows()[rows().indexOf(held) - 1];
        at = before.getBoundingClientRect().top;
        held.remove();
        held = before;
        await measure();
        const scrollTop = box.scrollTop;
        await new Promise((done) => setTimeout(done, 6500));
        const faded = getComputedStyle(document.querySelector(".thread-turn.busy")).opacity;
        return {drifts, stayed: box.scrollTop === scrollTop, gap: box.scrollHeight - box.scrollTop - box.clientHeight, faded};
    });
    expect(reading.drifts.every((drift) => Math.abs(drift) <= 1), `the row read moved by ${reading.drifts.join(", ")} pixels as rows changed above it`);
    expect(reading.stayed && reading.gap > 100, "the reader scrolled up was taken toward the foot");
    expect(Number(reading.faded) === 0, `the line of what the agent is doing is not faded while scrolled up (opacity ${reading.faded})`);

    // at the foot, something arriving carries the reader down and folds no docked mark: they fold only on a scroll up
    await page.reload();
    await page.waitForSelector(".thread-scroll [data-ref]", {timeout: 20000});
    await page.waitForTimeout(2000);
    const arriving = await page.evaluate(async () => {
        const box = document.querySelector(".thread-scroll");
        box.scrollTop = box.scrollHeight;
        box.dispatchEvent(new Event("scroll"));
        await new Promise((done) => setTimeout(done, 600));
        const folded = () => document.querySelectorAll(".chat-dock-body.folded").length;
        const before = folded();
        const rows = [...box.querySelectorAll("[data-ref]")];
        rows.at(-1).appendChild(Object.assign(document.createElement("div"), {style: "height: 400px"}));
        await new Promise((done) => setTimeout(done, 1500));
        return {before, after: folded(), gap: box.scrollHeight - box.scrollTop - box.clientHeight};
    });
    expect(arriving.after <= arriving.before, `docked marks folded as something arrived at the foot (${arriving.before} folded before, ${arriving.after} after)`);
    expect(arriving.gap <= 24, `the reader at the foot was not carried down to what arrived (gap ${arriving.gap})`);

    // the reader's hand wins: a wheel during the chat's own glide to the foot stops it where the wheel left it
    await page.reload();
    await page.waitForSelector(".thread-scroll [data-ref]", {timeout: 20000});
    await page.waitForTimeout(2000);
    const box = await page.locator(".thread-scroll").boundingBox();
    await page.evaluate(() => {
        const pane = document.querySelector(".thread-scroll");
        pane.scrollTop = pane.scrollHeight;
        pane.dispatchEvent(new Event("scroll"));
    });
    await page.waitForTimeout(400);
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    await page.mouse.wheel(0, -900);
    await page.waitForTimeout(150);
    const wheeled = await page.evaluate(async () => {
        const pane = document.querySelector(".thread-scroll");
        const rows = [...pane.querySelectorAll("[data-ref]")];
        rows.at(-1).appendChild(Object.assign(document.createElement("div"), {style: "height: 300px"}));
        const left = pane.scrollTop;
        await new Promise((done) => setTimeout(done, 1200));
        return {left, now: pane.scrollTop};
    });
    expect(Math.abs(wheeled.now - wheeled.left) <= 1, `the chat moved itself from where the reader's wheel left it (${wheeled.left} to ${wheeled.now})`);

    // scrolled up within a quarter and left alone: it settles at the foot after five seconds, not before
    await page.reload();
    await page.waitForSelector(".thread-scroll [data-ref]", {timeout: 20000});
    await page.waitForTimeout(2000);
    const settling = await page.evaluate(async () => {
        const box = document.querySelector(".thread-scroll");
        const gap = () => box.scrollHeight - box.scrollTop - box.clientHeight;
        box.scrollTop = box.scrollHeight - box.clientHeight - box.clientHeight * 0.15;
        box.dispatchEvent(new Event("scroll"));
        await new Promise((done) => setTimeout(done, 4000));
        const early = gap();
        await new Promise((done) => setTimeout(done, 2500));
        return {early, late: gap()};
    });
    expect(settling.early > 40, `the chat settled at the foot before five seconds (gap ${settling.early})`);
    expect(settling.late <= 24, `the chat did not settle at the foot after five seconds (gap ${settling.late})`);
} finally {
    await browser.close();
}

if (failures.length) {
    console.error(failures.map((failure) => `failed: ${failure}`).join("\n"));
    process.exit(1);
}
console.log("the chat's scroll holds the reader's place and settles only near the foot");
