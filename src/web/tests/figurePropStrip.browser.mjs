// Actual SVG props and the parcel's beam trajectory at their seams. FIGURE_ROOT renders an earlier source tree for comparison.
import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/props.png");
const imports = {
    name: "prop-strip-imports",
    resolveId: (id) => id === "/prop-strip-imports.js" ? id : null,
    load: (id) => id === "/prop-strip-imports.js" ? 'export {createApp, h, nextTick} from "vue"; export {default as PackBox} from "/src/chat/act/PackBox.vue"; export {default as VacuumCleaner} from "/src/chat/act/VacuumCleaner.vue";' : null,
};
const server = await createServer({root, plugins: [imports], logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox"]});

try {
    const page = await browser.newPage();
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const strip = await page.evaluate(async () => {
        const {createApp, h, nextTick, PackBox, VacuumCleaner} = await import("/prop-strip-imports.js");
        const {ACTS} = await import("/src/figure/acts.js");
        const {boxSway} = await import("/src/figure/parcels.js");
        const cell = {width: 240, height: 170};
        const header = 30;
        const sheet = document.createElement("canvas");
        sheet.width = cell.width * 6;
        sheet.height = (cell.height + header) * 3;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#15161a";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        const draw = async (component, props, viewBox, column, row, label) => {
            const host = document.createElement("div");
            const app = createApp({render: () => h("svg", {xmlns: "http://www.w3.org/2000/svg", viewBox, width: cell.width, height: cell.height, stroke: "#272936", "stroke-width": 1}, [h(component, props)])});
            app.mount(host);
            await nextTick();
            const picture = new Image();
            const url = URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(host.querySelector("svg"))], {type: "image/svg+xml"}));
            picture.src = url;
            await picture.decode();
            const x = column * cell.width;
            const y = row * (cell.height + header);
            paint.drawImage(picture, x, y + header);
            paint.fillStyle = "#c9ccd7";
            paint.font = "12px monospace";
            paint.fillText(label, x + 8, y + 21);
            URL.revokeObjectURL(url);
            app.unmount();
        };
        const box = ACTS.pack_box;
        const total = box.intro + box.hold + box.outro;
        for (const [column, puff] of [0, 0.18, 0.36, 0.54, 0.72, 0.9].entries()) {
            const u = (box.intro + box.hold + box.outro * (box.pops + 0.4 * puff)) / total;
            await draw(PackBox, {u, middle: 56, floor: 108}, "0 42 112 80", column, 0, `box fragments · ${puff.toFixed(2)}`);
        }
        const vacuum = ACTS.vacuum;
        const vacuumFrames = vacuum.intro + vacuum.hold + vacuum.outro;
        for (const [column, frame] of [0.001, 5, 29.99, 30.01, 55, 59.999].entries()) {
            await draw(VacuumCleaner, {u: frame / vacuumFrames, hand: {x: 64, y: 60}, middle: 56, floor: 108, out: 1, size: 112}, "15 5 170 120", column, 1, `vacuum · frame ${frame.toFixed(3)}`);
        }
        for (const [column, k] of [0, 0.0000001, 0.005, 0.025, 0.1, 0.3].entries()) {
            const dx = boxSway(k, 1);
            const x = column * cell.width;
            const y = 2 * (cell.height + header);
            paint.fillStyle = "#c9ccd7";
            paint.font = "12px monospace";
            paint.fillText(`beam k=${k} · dx=${dx.toFixed(3)}`, x + 8, y + 21);
            paint.save();
            paint.translate(x + cell.width / 2, y + header + 115);
            paint.scale(3, 3);
            paint.strokeStyle = "#5a6070";
            paint.setLineDash([2, 2]);
            paint.beginPath();
            paint.moveTo(0, -30);
            paint.lineTo(0, 6);
            paint.stroke();
            paint.setLineDash([]);
            paint.fillStyle = "#737c94";
            paint.fillRect(dx - 12, -27 - 45 * k, 24, 27);
            paint.strokeStyle = "#c0c6d2";
            paint.strokeRect(dx - 12, -27 - 45 * k, 24, 27);
            paint.restore();
        }
        return sheet.toDataURL("image/png");
    });
    mkdirSync(dirname(out), {recursive: true});
    writeFileSync(out, Buffer.from(strip.split(",")[1], "base64"));
    console.log(out);
} finally {
    await browser.close();
    await server.close();
}
