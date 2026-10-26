// Compare the pogo stick draw before and after a change: the hand travels from behind the back to the handles without a pose switch.
import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";
import vue from "@vitejs/plugin-vue";
import {createSSRApp, h} from "vue";
import {renderToString} from "@vue/server-renderer";

const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/pogo-draw.png");
const size = Number(process.env.FIGURE_SIZE ?? 144);
const cases = [0.09, 0.14, 0.18, 0.26, 0.4, 0.62, 0.8, 0.86].map((u) => ({label: `u = ${u}`, u}));
const server = await createServer({root, configFile: false, plugins: [vue()], logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const {default: PogoStick} = await server.ssrLoadModule("/src/chat/act/PogoStick.vue");
const {FRAMED} = await server.ssrLoadModule("/src/figure/frame.js");
for (const moment of cases) {
    moment.svg = await renderToString(createSSRApp({render: () => h("svg", {xmlns: "http://www.w3.org/2000/svg", width: size, height: size}, [h(PogoStick, {u: moment.u, middle: size / 2, floor: (0.5 + FRAMED.middle / FRAMED.height) * size, size})])}));
}
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage({deviceScaleFactor: 1});
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const png = await page.evaluate(async ({voices, size, cases}) => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const all = await (await fetch("/voices/figures/figures.json")).json();
        const index = Object.entries(all).filter(([name]) => !voices.length || voices.includes(name));
        const sheet = document.createElement("canvas");
        sheet.width = 80 + cases.length * size;
        sheet.height = 36 + index.length * size;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#15161a";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        paint.fillStyle = "#dddfea";
        paint.font = "13px sans-serif";
        cases.forEach(({label}, i) => paint.fillText(label, 84 + i * size, 23));
        const stage = new Stage();
        const clip = CLIPS.find((each) => each.name === "pogo");
        for (const [row, [voice, file]] of index.entries()) {
            const figure = await figureOf(await (await fetch(`/voices/figures/${file}`)).arrayBuffer(), voice, "/voices/figures/draco/");
            paint.fillText(voice, 8, 36 + row * size + size / 2);
            for (const [column, {u, svg}] of cases.entries()) {
                const cell = document.createElement("canvas");
                cell.width = cell.height = size;
                stage.draw(figure, clip, clip.frames * u, 0, cell);
                const overlay = new Image();
                const markup = new XMLSerializer().serializeToString(new DOMParser().parseFromString(svg, "text/html").querySelector("svg"));
                overlay.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(markup)}`;
                await overlay.decode();
                cell.getContext("2d").drawImage(overlay, 0, 0);
                paint.drawImage(cell, 80 + column * size, 36 + row * size);
            }
        }
        return sheet.toDataURL("image/png");
    }, {voices: (process.env.FIGURE_VOICES ?? "butler").split(",").filter(Boolean), size, cases});
    mkdirSync(dirname(out), {recursive: true});
    writeFileSync(out, Buffer.from(png.split(",")[1], "base64"));
    console.log(out);
} finally {
    await browser.close();
    await server.close();
}
