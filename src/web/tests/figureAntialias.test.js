import {readFileSync} from "node:fs";
import {expect, test} from "vitest";

const figure = readFileSync("src/figure/figure.js", "utf8");
const draw = figure.split("    draw(")[1]?.split("\n    }\n")[0] ?? "";

test("the figure, its screen included, is drawn in one multisampled pass three times as wide as its canvas and scaled down with no blur", () => {
    expect(figure).toContain("const SUPERSAMPLE = 3;");
    expect(figure).toContain("new THREE.WebGLRenderer({antialias: true, alpha: true, preserveDrawingBuffer: true})");
    expect(figure).not.toContain("antialias: false");
    expect(figure).not.toContain("crispScreen");
    expect(draw).toContain("const size = canvas.width * SUPERSAMPLE;");
    expect(draw).toContain('context.filter = "none";');
    expect(draw).toContain('context.imageSmoothingQuality = "high";');
    expect(draw).not.toContain("blur(");
    expect(draw).not.toContain("material.visible = false");
});
