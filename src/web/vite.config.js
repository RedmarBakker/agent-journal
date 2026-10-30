import vue from "@vitejs/plugin-vue";
import {execFileSync} from "node:child_process";
import {existsSync, writeFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {defineConfig} from "vite";

const builtFrom = () => ({
    name: "built-from",
    apply: "build",
    closeBundle() {
        if (!existsSync(new URL("../../scripts/checks/viewer_built.py", import.meta.url))) {
            this.warn("Standalone viewer build: scripts/checks/viewer_built.py is not included, so the repository built-from stamp is not generated.");
            return;
        }
        const digest = execFileSync("python3", ["scripts/checks/viewer_built.py", "--digest"], {cwd: fileURLToPath(new URL("../..", import.meta.url)), timeout: 30000});
        writeFileSync(new URL("./dist/built-from", import.meta.url), digest.toString());
    },
});

export default defineConfig({
    plugins: [vue(), builtFrom()],
    base: "./",
    build: {rollupOptions: {input: {main: "index.html", share: "share.html", phone: "phone.html"}}},
    server: {proxy: {"/journal": "http://127.0.0.1:8430"}},
});
