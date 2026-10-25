import {readFileSync} from "node:fs";
import {expect, test} from "vitest";

const figure = readFileSync("src/figure/figure.js", "utf8");
const method = (name) => figure.split(`    ${name}(`)[1]?.split("\n    }\n")[0] ?? "";

test("the body is drawn softened at twice its canvas, as before the smoothing, and only the screen is drawn four times as wide and halved twice", () => {
    expect(method("draw")).toContain("this.drawBody(figure, canvas);");
    expect(method("draw")).toContain("this.drawScreen(figure, canvas);");
    const body = method("drawBody");
    expect(figure).toContain("const BODY_SUPERSAMPLE = 2;");
    expect(body).toContain("canvas.width * BODY_SUPERSAMPLE");
    expect(body).toContain("material.visible = false");
    expect(body).toContain("blur(${softenOn(canvas)}px)");
    const screen = method("drawScreen");
    expect(figure).toContain("const SUPERSAMPLE = 4;");
    expect(screen).toContain("canvas.width * SUPERSAMPLE");
    expect(screen).toContain("material.colorWrite = false");
    expect(screen).toContain("this.halvedOnto(this.screenRenderer.domElement, 0, 0, size, size, this.screenCanvas);");
    expect(screen).not.toContain("blur(");
    expect(figure).not.toContain("antialias: false");
});
