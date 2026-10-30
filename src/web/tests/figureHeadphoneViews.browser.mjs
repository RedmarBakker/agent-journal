// Readable final-source views of the loose headset, the formerly oversized landing route and the concealed sleeve-route change.
import {createHash} from "node:crypto";
import {mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = resolve(process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url)));
const out = resolve(process.argv[2] ?? "tests/strips/headphone-views");
const paths = ["src/figure/figure.js", "src/figure/homie.js", "src/figure/headphoneClearance.js"];
const snapshots = new Map(paths.map((path) => [resolve(root, path), readFileSync(resolve(root, path), "utf8")]));
const sourceHashes = Object.fromEntries([...snapshots].map(([path, source]) => [path.slice(root.length + 1), createHash("sha256").update(source).digest("hex")]));
const server = await createServer({root, configFile: false, logLevel: "silent", plugins: [{name: "headphone-views-snapshot", enforce: "pre", load: (id) => snapshots.get(id) ?? null}], server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage(), browserErrors = [];
    page.on("pageerror", (error) => browserErrors.push(error.message));
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const pictures = await page.evaluate(async (selected) => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const figure = await figureOf(await (await fetch("/voices/figures/" + index.homie)).arrayBuffer(), "homie", "/voices/figures/draco/");
        const stage = new Stage(), size = 256, label = 24;
        const canvas = Object.assign(document.createElement("canvas"), {width: size, height: size});
        const groups = selected ?? [
            {name: "after", facings: [0, 90], poses: [{clip: "idle", u: 0}, {clip: "tantrum", u: 0.25}, {clip: "land", u: 0.15}]},
            {name: "route-front", facings: [0, 45, 90], poses: [{clip: "tantrum", u: 0.3769230769230769}, {clip: "tantrum", u: 0.3783216783216784}]},
            {name: "route-rear", facings: [180, 225, 270], poses: [{clip: "tantrum", u: 0.3769230769230769}, {clip: "tantrum", u: 0.3783216783216784}]},
            {name: "free-cup-motion", facings: [0, 90], poses: [{clip: "rummage", u: 0.82}, {clip: "rummage", u: 0.85}, {clip: "rummage", u: 0.87}]},
        ];
        const pictures = [];
        for (const group of groups) {
            const sheet = Object.assign(document.createElement("canvas"), {width: size * group.facings.length, height: (size + label) * group.poses.length});
            const paint = sheet.getContext("2d"); paint.fillStyle = "#252832"; paint.fillRect(0, 0, sheet.width, sheet.height);
            for (const [row, pose] of group.poses.entries()) for (const [column, facing] of group.facings.entries()) {
                const clip = CLIPS.find(({name}) => name === pose.clip);
                stage.draw(figure, clip, pose.u * (clip.frames - 1), facing, canvas, {posture: "stand"});
                paint.drawImage(canvas, column * size, row * (size + label));
                paint.fillStyle = "#e0e4ee"; paint.font = "13px sans-serif"; paint.textAlign = "center";
                paint.fillText(`${pose.clip} ${pose.u.toFixed(4)} · ${facing}°`, column * size + size / 2, row * (size + label) + size + 17);
            }
            pictures.push({...group, png: sheet.toDataURL("image/png")});
        }
        return pictures;
    }, process.env.HEADPHONE_VIEW_GROUPS ? JSON.parse(process.env.HEADPHONE_VIEW_GROUPS) : null);
    mkdirSync(out, {recursive: true});
    for (const picture of pictures) writeFileSync(resolve(out, picture.name + ".png"), Buffer.from(picture.png.split(",")[1], "base64"));
    writeFileSync(resolve(out, "views.json"), JSON.stringify({sourceHashes, views: pictures.map(({png, ...picture}) => picture), browserErrors}, null, 2) + "\n");
    if (browserErrors.length) throw new Error("Headphone view capture failed");
} finally {
    await browser.close();
    await server.close();
}
