import vue from "@vitejs/plugin-vue";
import {defineConfig} from "vitest/config";

export default defineConfig({
    plugins: [vue()],
    define: {__DEMO__: false, __DEMO_BUILD__: JSON.stringify("test")},
    // Component tests include their cold module imports in this budget, alongside the full model-geometry checks.
    test: {environment: "jsdom", pool: "forks", css: {include: [/UpdateOverlay\.vue/]}, include: ["tests/**/*.test.js"], globalSetup: ["tests/testRunMark.js"], setupFiles: ["tests/support/browserGlobals.js"], testTimeout: 30000, maxWorkers: 3},
});
