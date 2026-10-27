// Render both Newest motions from the production curves: node tests/figureNewestStrip.browser.mjs output-directory.
import {mkdirSync, writeFileSync} from "node:fs";
import {join, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = resolve(process.env.FIGURE_PROJECT_ROOT ?? fileURLToPath(new URL("..", import.meta.url)));
const out = resolve(process.argv[2] ?? join(root, "tests", "strips"));
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({executablePath: process.env.CHROMIUM_EXECUTABLE_PATH || process.env.CHROMIUM_PATH || undefined, args: ["--no-sandbox", "--disable-dev-shm-usage", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
const failures = [];
try {
    const page = await (await browser.newContext({deviceScaleFactor: 1})).newPage();
    page.on("pageerror", (error) => failures.push(error.message));
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const rendered = await page.evaluate(async () => {
        const {CLIPS, GROUND, Stage, figureOf} = await import("/src/figure/figure.js");
        const {NEWEST_ASIDE, newestScootAt} = await import("/src/figure/newest.js");
        const {strideAtDistance} = await import("/src/figure/gait.js");
        const {boxAt, newestAsideSpot, tripBetween} = await import("/src/figure/places.js");
        const manifest = await (await fetch("/voices/figures/figures.json")).json();
        const stage = new Stage();
        const cell = {width: 332, height: 250};
        const figureSize = {size: 160, below: GROUND};
        const floor = {left: 10, right: 322, top: 187};
        const button = {left: 95, right: 185, top: 165, bottom: 195};
        const origin = {x: 150, y: floor.top, face: 0, posture: "stand"};
        document.body.innerHTML = '<div class="thread"><div data-figure-home></div></div>';
        document.querySelector(".thread").getBoundingClientRect = () => ({left: 0, right: cell.width, top: 0, bottom: cell.height});
        const destination = newestAsideSpot(figureSize, origin, floor, button);
        const way = Math.sign(destination.x - origin.x);
        const walk = tripBetween({x: origin.x, y: floor.top}, {x: destination.x, y: floor.top}, figureSize.size, {random: () => 1}).legs.find((leg) => !leg.hopping);
        const seated = CLIPS.find((clip) => clip.name === "newest_scoot");
        const idle = CLIPS.find((clip) => clip.name === "idle");
        const walking = CLIPS.find((clip) => clip.name === "walk");
        const times = [0, 0.10, 0.22, 0.32, 0.43, 0.55, 0.67, 0.78, 0.90, 1];
        const smooth = (value) => {
            const k = Math.min(Math.max(value, 0), 1);
            return k * k * (3 - 2 * k);
        };
        const pictures = [];
        for (const motion of ["standing", "seated"]) {
            const sheet = document.createElement("canvas");
            sheet.width = cell.width * times.length;
            sheet.height = cell.height * Object.keys(manifest).length;
            const paint = sheet.getContext("2d");
            paint.fillStyle = "#15161a";
            paint.fillRect(0, 0, sheet.width, sheet.height);
            for (const [row, [voice, filename]] of Object.entries(manifest).entries()) {
                const figure = await figureOf(await (await fetch(`/voices/figures/${filename}`)).arrayBuffer(), voice, "/voices/figures/draco/");
                for (const [column, u] of times.entries()) {
                    const canvas = document.createElement("canvas");
                    canvas.width = canvas.height = figureSize.size;
                    const scoot = motion === "seated";
                    const seconds = u * (NEWEST_ASIDE.notice + 0.25 + walk.ms / 1000 + 0.2);
                    const moved = scoot ? newestScootAt(u).across : Math.min(Math.max((seconds - NEWEST_ASIDE.notice - 0.25) / (walk.ms / 1000), 0), 1);
                    const x = origin.x + (destination.x - origin.x) * moved;
                    const spot = {...origin, x, posture: scoot ? "sit" : "stand"};
                    const box = boxAt(spot, figureSize);
                    const stride = strideAtDistance(Math.abs(x - origin.x), figureSize.size);
                    const clip = scoot ? seated : moved > 0 && moved < 1 ? walking : idle;
                    const frame = scoot ? u * (seated.frames - 1) : clip === walking ? ((stride % 1 + 1) % 1) * walking.frames : 0;
                    const facing = scoot ? 0 : way * 90 * smooth((seconds - NEWEST_ASIDE.notice) / 0.25);
                    const noticing = !scoot && seconds < NEWEST_ASIDE.notice;
                    const notice = seconds / NEWEST_ASIDE.notice;
                    const at = noticing ? {x: ((button.left + button.right) / 2 - box.left) / figureSize.size, y: ((button.top + button.bottom) / 2 - box.top) / figureSize.size, amount: smooth(notice / 0.3) * (1 - smooth((notice - 0.75) / 0.25)), most: 0} : null;
                    stage.draw(figure, clip, frame, facing, canvas, {posture: spot.posture, stride: scoot ? Math.abs(destination.x - origin.x) / figureSize.size : stride, walkWay: scoot ? way : 0, at});
                    paint.save();
                    paint.translate(column * cell.width, row * cell.height);
                    paint.strokeStyle = "#4d5262";
                    paint.beginPath();
                    paint.moveTo(floor.left, floor.top);
                    paint.lineTo(floor.right, floor.top);
                    paint.stroke();
                    paint.fillStyle = "#6366f1";
                    paint.beginPath();
                    paint.roundRect(button.left, button.top, button.right - button.left, button.bottom - button.top, 12);
                    paint.fill();
                    paint.fillStyle = "#ffffff";
                    paint.font = "13px sans-serif";
                    paint.textAlign = "center";
                    paint.fillText("↓ Newest", (button.left + button.right) / 2, button.top + 20);
                    paint.drawImage(canvas, box.left, box.top, figureSize.size, figureSize.size);
                    paint.fillStyle = "#b7bbca";
                    paint.font = "12px sans-serif";
                    paint.textAlign = "left";
                    paint.fillText(`${voice} · ${scoot ? `shuffle ${(u * 100).toFixed(0)}%` : `${seconds.toFixed(2)} s`}`, 12, 238);
                    paint.restore();
                }
            }
            pictures.push({name: `newest-${motion}-strip.png`, png: sheet.toDataURL("image/png")});
        }
        stage.renderer.dispose();
        stage.screenRenderer.dispose();
        return pictures;
    });
    mkdirSync(out, {recursive: true});
    for (const each of rendered) {
        writeFileSync(join(out, each.name), Buffer.from(each.png.split(",")[1], "base64"));
        console.log(join(out, each.name));
    }
} finally {
    await browser.close();
    await server.close();
}
if (failures.length) throw new Error(failures.join("\n"));
