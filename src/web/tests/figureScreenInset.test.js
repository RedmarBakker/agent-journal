import * as THREE from "three";
import {expect, test} from "vitest";

const {SCREEN_INSET, frontOf, setScreenIn} = await import("../src/figure/figure.js");

// A head and its screen shaped as every voice's are (public/voices/figures, face_screen and head_shell), in the model's own axes, +z its
// front: a round shell 0.9 across its middle about the head's middle at 3.2 high, and a screen 1.5 wide and 0.7 high over its front,
// curved with the head and standing 0.03 proud of it, as the models have it before it is set in
const MIDDLE = 3.2;
function head() {
    const shell = new THREE.SphereGeometry(0.9, 72, 54).translate(0, MIDDLE, 0);
    const screen = new THREE.PlaneGeometry(1.5, 0.7, 30, 14).translate(0, 3.1, 0);
    const at = screen.attributes.position;
    for (let index = 0; index < at.count; index++) at.setZ(index, Math.sqrt(0.93 ** 2 - at.getX(index) ** 2 - (at.getY(index) - MIDDLE) ** 2));
    return {shell, screen};
}

const points = (geometry) => {
    const at = geometry.attributes.position;
    return Array.from({length: at.count}, (_, index) => new THREE.Vector3(at.getX(index), at.getY(index), at.getZ(index)));
};

test("the visor screen is set into the head: its surface, at its most forward, the set inset behind the head's front surface, its shape kept", () => {
    const {shell, screen} = head();
    const surface = shell.clone();
    const before = points(screen);
    setScreenIn(screen, [shell]);
    const after = points(screen);
    // about half a centimetre on a human head, 15 cm across, on a head 1.83 of the figure's units across
    expect(SCREEN_INSET.depth).toBeCloseTo((0.005 / 0.15) * 1.83, 2);
    // no point of the screen nearer the front than the inset behind the head's own surface, and its most forward point just that
    const front = frontOf(surface);
    const gaps = after.map((point) => point.z - front(point.x, point.y));
    expect(Math.max(...gaps)).toBeCloseTo(-SCREEN_INSET.depth, 6);
    // moved straight back, every point by as much, so the screen keeps the head's curve and its outline
    const moved = after[0].z - before[0].z;
    expect(moved).toBeLessThan(-SCREEN_INSET.depth);
    after.forEach((point, index) => {
        expect(point.x).toBe(before[index].x);
        expect(point.y).toBe(before[index].y);
        expect(point.z - before[index].z).toBeCloseTo(moved, 9);
    });
});

test("the head behind the screen is set in with it: no point of the head within the screen's outline in front of it, the rest left as it was", () => {
    const {shell, screen} = head();
    const before = points(shell);
    setScreenIn(screen, [shell]);
    let within = 0;
    const glassAt = frontOf(screen);
    points(shell).forEach((point, index) => {
        const glass = glassAt(point.x, point.y);
        if (glass === null) return expect(point.equals(before[index]), `${index} outside the outline`).toBe(true);
        within += 1;
        expect(point.z, `${index} within the outline`).toBeLessThanOrEqual(glass - SCREEN_INSET.behind + 1e-9);
    });
    // the head's front within the screen's outline was there to set in, and was
    expect(within).toBeGreaterThan(100);
    expect(before.some((point) => point.z > 0.8 && Math.abs(point.y - 3.1) < 0.2)).toBe(true);
});

test("a helmet's shell worn over the head is set in with it, as the head's own shell is", () => {
    const {shell, screen} = head();
    const helmet = new THREE.SphereGeometry(0.92, 72, 54).translate(0, MIDDLE, 0);
    const worn = frontOf(helmet.clone());
    setScreenIn(screen, [shell, helmet]);
    const glassAt = frontOf(screen);
    for (const geometry of [shell, helmet]) {
        for (const point of points(geometry)) {
            const glass = glassAt(point.x, point.y);
            if (glass !== null) expect(point.z).toBeLessThanOrEqual(glass - SCREEN_INSET.behind + 1e-9);
        }
    }
    // the inset is measured from the head's surface at its most forward, the helmet's here
    expect(Math.max(...points(screen).map((point) => point.z - worn(point.x, point.y)))).toBeCloseTo(-SCREEN_INSET.depth, 6);
});
