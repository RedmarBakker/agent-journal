// @vitest-environment node
import {existsSync, readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, Posing} from "../src/figure/figure.js";
import {answerTo} from "../src/figure/reactions.js";
import {EVERY_VOICE_FACES, PILE, VOICE_FACES} from "../src/figure/pile.js";
import {facesAfter} from "../src/domain/figureState.js";

// the figures' own skeleton and what each voice carries, as figure.js figureOf reads them from the voices' glbs
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {
    order: rig.order,
    parents: new Map(Object.entries(rig.parents)),
    heads: vectors(rig.heads),
    along: vectors(rig.along),
    eyes: rig.eyes.map((at) => new THREE.Vector3(...at)),
};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

// The standalone viewer archive includes the rig and frontend faces, but not the server catalogue.
const cataloguePath = new URL("../../journal/features/voices/support/builtin_catalogue.py", import.meta.url);

const clipNamed = (name) => CLIPS.find((clip) => clip.name === name);

function posed(clip, voice, t, posture = "stand") {
    const pose = new Posing(RIG, posture, 0);
    clip.pose(pose, stanceOf(voice), t);
    return pose;
}

// every bone's move, to compare a pose with the figure at rest
const movesOf = (pose) => [...pose.moves(0)].map(([name, move]) => [name, move.elements.map((n) => Math.round(n * 1e4) / 1e4 + 0)]);

test("every configured voice face has a clip of that voice's own, which the agent's face on a message calls for", () => {
    expect(Object.keys(VOICE_FACES).sort()).toEqual(Object.keys(stances).sort());
    for (const [voice, faces] of Object.entries(VOICE_FACES)) {
        for (const [face, name] of Object.entries(faces)) {
            const clip = clipNamed(name);
            expect(clip, `${voice} ${face}`).toBeDefined();
            expect(clip.voices, `${voice} ${face}`).toEqual([voice]);
            expect(PILE.find((each) => each.when.moment === `agent_reacted:${face}` && each.when.voices?.includes(voice)).name).toBe(clip.name);
        }
    }
    const clips = Object.values(VOICE_FACES).flatMap((faces) => Object.values(faces));
    expect(new Set(clips).size).toBe(14);
});

test("the server's built-in voice catalogue is covered by the viewer's reaction clips", ({skip}) => {
    if (!existsSync(cataloguePath)) skip("Standalone archive omits journal/features/voices/support/builtin_catalogue.py; the server-to-viewer catalogue cross-check requires the full repository.");
    const catalogue = readFileSync(cataloguePath, "utf8");
    const builtIn = Object.fromEntries(
        [...catalogue.matchAll(/Voice\("(\w+)",[\s\S]*?emoji="([^"]+)"\)/g)].map(([, voice, emoji]) => [voice, emoji.split(" ")])
    );
    expect(Object.keys(builtIn).sort()).toEqual(["butler", "coach", "colleague", "homie", "squire"]);
    for (const [voice, faces] of Object.entries(builtIn)) {
        expect(faces.length, voice).toBe(3);
        for (const face of faces) {
            const name = VOICE_FACES[voice][face] ?? EVERY_VOICE_FACES[face];
            expect(clipNamed(name), `${voice} ${face}`).toBeDefined();
        }
    }
});

test("the agent's 🙏 on a message plays the thanks for every voice: the hands pressed together before the chest, fingers up", () => {
    const thanks = clipNamed("thanks");
    expect(thanks.voices).toBeUndefined();
    for (const voice of Object.keys(stances)) {
        const has = (name) => clipNamed(name) && (!clipNamed(name).voices || clipNamed(name).voices.includes(voice));
        expect(answerTo({beat: "agent_reacted:🙏", time: 1}, voice, {reacted: new Map(), played: []}, 200, () => 0.99, has), voice).toEqual({beat: {clip: "thanks", card: ""}});
        const pose = posed(thanks, voice, 0.5);
        const moves = pose.moves(0);
        const [left, right] = ["l", "r"].map((side) => pose.grip(side, [0, 0, 0]).applyMatrix4(moves.get(`hand_${side}`)));
        expect(left.distanceTo(right), voice).toBeLessThan(0.3);
        const chest = pose.head("chest", moves.get("chest"));
        expect(left.z, voice).toBeGreaterThan(chest.z - 0.4);
        expect(left.y, voice).toBeLessThan(chest.y - 0.3);
        for (const side of ["l", "r"]) {
            const fingers = RIG.along.get(`hand_${side}`).clone().transformDirection(moves.get(`hand_${side}`));
            expect(fingers.z, `${voice} ${side}`).toBeGreaterThan(0.8);
        }
    }
});

test("both agent anger faces call every voice's tantrum while a user's anger remains a look", () => {
    const tantrum = clipNamed("tantrum");
    expect(tantrum).toBeDefined();
    expect(tantrum.voices).toBeUndefined();
    expect(tantrum.postures).toEqual(["stand"]);
    expect(tantrum.loops).toBe(false);
    for (const voice of Object.keys(stances)) {
        const has = (name) => clipNamed(name) && (!clipNamed(name).voices || clipNamed(name).voices.includes(voice));
        for (const face of ["😠", "😡"]) {
            const moment = {beat: `agent_reacted:${face}`, time: 1, card: "messages:7"};
            expect(answerTo(moment, voice, {reacted: new Map(), played: []}, 200, () => 0.99, has), `${voice} ${face}`).toEqual({
                beat: {clip: "tantrum", card: "", mark: "messages:7"},
            });
            expect(answerTo(moment, voice, {reacted: new Map(), played: []}, 200, () => 0, (name) => name !== "tantrum")).toBe(null);
        }
        expect(answerTo({beat: "reacted:😠", time: 1}, voice, {reacted: new Map(), played: []}, 200, () => 0.99, has)).toEqual({look: "angry"});
        expect(answerTo({beat: "reacted:😡", time: 1}, voice, {reacted: new Map(), played: []}, 200, () => 0, has)).toBe(null);
    }
});

test("each face's clip poses on every frame in every posture it is drawn in, and starts and ends at rest with nothing in hand", () => {
    for (const [voice, faces] of Object.entries(VOICE_FACES)) {
        const rest = movesOf(posed(clipNamed("idle"), voice, 0));
        for (const name of new Set(Object.values({...faces, ...EVERY_VOICE_FACES}))) {
            const clip = clipNamed(name);
            const steps = clip.frames * 5;
            for (const posture of clip.postures) {
                for (let step = 0; step <= steps; step++) expect(() => posed(clip, voice, step / steps, posture), `${name} ${posture} ${step}`).not.toThrow();
            }
            const moved = Array.from({length: clip.frames}, (_, frame) => JSON.stringify(movesOf(posed(clip, voice, frame / clip.frames))));
            expect(moved.slice(1).filter((each, frame) => each !== moved[frame]).length, name).toBeGreaterThan(clip.frames / 2);
            for (const t of [0, (clip.frames - 1) / clip.frames]) {
                const pose = posed(clip, voice, t);
                expect(movesOf(pose), `${name} at ${t}`).toEqual(rest);
                expect([Math.round(pose.eyes * 1e4) / 1e4, pose.eyeTint, pose.props.size, pose.stowed.size], `${name} at ${t}`).toEqual([1, null, 0, 0]);
            }
        }
    }
});

test("the agent's face plays its voice's clip once, the user's same face only changes the eyes, and a reload plays nothing again", () => {
    const at = (seconds) => new Date(seconds * 1000).toISOString();
    const rows = [
        {table: "reactions", id: 1, author: "agent", emoji: "🎩", message_id: 7, created_at: at(100)},
        {table: "reactions", id: 2, author: "user", emoji: "🎩", message_id: 8, created_at: at(101)},
    ];
    const memory = {reacted: new Map(), played: []};
    const answer = (moment) => answerTo(moment, "butler", memory, 200, () => 0.99, (clip) => Boolean(clipNamed(clip)));
    const seen = facesAfter(rows, 99);
    expect(seen.map((moment) => moment.beat)).toEqual(["agent_reacted:🎩", "reacted:🎩"]);
    expect(seen.map(answer)).toEqual([{beat: {clip: "hat_tip", card: "", mark: seen[0].card}}, {look: "amused"}]);
    // the next look starts from the newest face seen, so the face is not played twice
    expect(facesAfter(rows, Math.max(...seen.map((moment) => moment.time)))).toEqual([]);
    // a figure that mounts after the face was put on, as after a reload, starts its looks from then and so never sees it
    expect(facesAfter(rows, 150)).toEqual([]);
    // a face from another voice's set plays nothing on this one
    expect(answerTo({beat: "agent_reacted:🏆", time: 1}, "butler", memory, 200, () => 0, (clip) => clipNamed(clip)?.voices?.includes("butler"))).toBe(null);
});

test("a heart the user puts on the agent's message turns the figure's eyes to hearts, read from the reaction row as the server writes it", () => {
    const at = (seconds) => new Date(seconds * 1000).toISOString();
    // models/reaction.py: the face a reaction puts on is its emoji
    const rows = [{table: "reactions", id: 3, author: "user", emoji: "\u2764\ufe0f", message_id: 9, created_at: at(120)}];
    const memory = {reacted: new Map(), played: []};
    const [moment] = facesAfter(rows, 99);
    expect(moment).toEqual({beat: "reacted:\u2764\ufe0f", time: 120, card: "messages:9"});
    expect(answerTo(moment, "butler", memory, 200, () => 0.99, (clip) => Boolean(clipNamed(clip)))).toEqual({look: "hearts"});
});
