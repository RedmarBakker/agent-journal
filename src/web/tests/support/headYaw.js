import * as THREE from "three";

// how many degrees round from the body's front the head of a posed figure, its `moves`, looks
export function headYaw(moves) {
    const ahead = new THREE.Vector3(0, -1, 0).transformDirection(moves.get("head"));
    return THREE.MathUtils.radToDeg(Math.atan2(ahead.x, -ahead.y));
}
