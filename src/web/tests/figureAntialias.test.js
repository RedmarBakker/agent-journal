import {readFileSync} from "node:fs";
import {expect, test} from "vitest";

const figure = readFileSync("src/figure/figure.js", "utf8");
const draw = figure.split("    draw(")[1]?.split("\n    }\n")[0] ?? "";

test("the figure, its screen included, is drawn in one multisampled pass four times as wide as its canvas and halved twice with no blur", () => {
    expect(figure).toContain("const SUPERSAMPLE = 4;");
    expect(figure).toContain("new THREE.WebGLRenderer({antialias: true, alpha: true, preserveDrawingBuffer: true})");
    expect(figure).not.toContain("antialias: false");
    expect(figure).not.toContain("crispScreen");
    expect(draw).toContain("const size = canvas.width * SUPERSAMPLE;");
    expect(draw).toContain("this.halvedOnto(this.renderer.domElement, 0, 0, size, size, canvas);");
    expect(figure).toContain("this.half.width = canvas.width * 2;");
    expect(figure).toContain('context.filter = "none";');
    expect(draw).not.toContain("blur(");
    expect(draw).not.toContain("material.visible = false");
});
