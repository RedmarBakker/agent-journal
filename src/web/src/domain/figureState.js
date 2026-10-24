import {stateOf} from "./agentState.js";
import {createdAt, refOf, seconds} from "./row.js";
import {EVERY_VOICE_FACES, VOICE_FACES} from "../figure/pile.js";
import {ChatMark} from "./chatMark.js";

// What the figure does, read from the same agent row and work rows as the status bar, so the two never disagree.
// Each held state names the clip the figure loops while it is true; a state with no clip of its own idles. The walk is never held: it plays only while the figure moves.
export const HELD = {
    idle: "idle",
    asleep: "sleep",
    thinking: "idle",
    quiet: "idle",
    searching: "search",
    reading: "read",
    writing: "type",
    testing: "idle",
    building: "work",
    running: "idle",
    waiting: "waiting",
    asking: "waiting",
    compacting: "compacting",
    paused: "idle",
    stopped: "sleep",
};

// The states in which the agent cannot act, so the figure stays seated on a corner of the edge at home instead of roaming
export const RESTS = new Set(["asleep", "compacting", "paused", "stopped"]);

// The states in which the agent is at work
export const WORKING = new Set(["thinking", "quiet", "searching", "reading", "writing", "testing", "building", "running"]);

// A tool in flight says what the agent is doing with it; the providers report their own tools under these names.
const TOOL_STATES = {
    Read: "reading",
    Grep: "searching",
    Glob: "searching",
    WebSearch: "searching",
    WebFetch: "searching",
    Edit: "writing",
    MultiEdit: "writing",
    Write: "writing",
    NotebookEdit: "writing",
    Bash: "running",
};

// What a shell line says it does (the agent row's tool_work): a test run or a build is built as a parcel; a search, a grep, a find or the
// journal's own, is searching as the search tools are; any other command, moving files, reading or git alike, is plain running, which
// plays neither the parcel nor the laptop
const SHELL_STATES = {testing: "testing", building: "building", searching: "searching"};

const BAR_STATES = {paused: "paused", stopped: "stopped", compacting: "compacting", waiting: "waiting", running: "waiting"};

// An idle agent's figure falls asleep after this many seconds of nothing.
export const ASLEEP_AFTER = 600;

// A tool's pose stays this many seconds after it finishes, so a tool that runs for a moment is still seen.
export const TOOL_LINGERS = 3;

// How long a wait on the user lasts before the figure makes its one pointed remark, in seconds.
export const POINTED_AFTER = 180;

// The held state at `now` (seconds), with when it began; `waitingSince` is when the oldest thing waiting on the user arrived, as its badges
// count it, or 0 when nothing waits
export function figureStateOf(agent, waitingSince, now = Date.now() / 1000) {
    const bar = stateOf(agent);
    const since = agent?.part_started_at || seconds(agent?.heard_at) || now;
    if (BAR_STATES[bar]) return {state: BAR_STATES[bar], since};
    // the pose says what the agent does, so it waits on the user only while it does nothing else; where it stands says what waits
    if (bar === "idle" && (waitingSince || agent?.awaiting)) return {state: "asking", since: waitingSince || since};
    if (bar === "idle") return {state: now - since >= ASLEEP_AFTER ? "asleep" : "idle", since};
    const tool = agent?.tool;
    const doing = agent.tool_work ? (SHELL_STATES[agent.tool_work] ?? "running") : TOOL_STATES[tool];
    const inFlight = Boolean(tool) && (agent.tool_running || now - since < TOOL_LINGERS) && doing;
    // between tools the agent is quiet, standing as it does idle, until the server says it is thinking (agent_activity thinking_at)
    return {state: inFlight || (agent.thinking_at ? "thinking" : "quiet"), since};
}

export const clipOf = (state) => HELD[state] || HELD.idle;

// When the oldest thing waiting on the user arrived, in seconds: `since` kept while anything waits, `now` when something has just begun to
// wait, 0 once nothing does. `counts` are the views' badge counts.
export const waitingSinceAt = (counts, since, now) => (counts.question + counts.waiting + counts.suggestion > 0 ? since || now : 0);

// What the figure plays now, by clip name, with the way it faces: its fall, under a parachute when it comes down on one, its run up the
// bubbles while it is `flying`, its entrance or exit, the landing, the leg of a trip it is on, its hang
// while it hangs, the clip it watches the UFO with while it is `watching` one, its eagerness for the bar under it to end while it is `eager`, a beat until it is done, pointing once it stands at a tab while the agent waits
// on the user, else what its body is doing,
// drawn in its place. `scene` says where things stand, `doing` being the clip of the stretch it is in and `doingFacing` the way it faces for
// it, as toward a parcel it pushes, else the viewer; `canDraw(name, posture)` whether a clip is drawn in a posture. A beat comes with the way
// it faces.
// A trip has `started` once the figure stands ready to travel and `moves` while a leg carries it; the hop of a leg or the walk is named
// only then, so the walk is never drawn on the spot. The clip of a leg that waits is marked `startsLeg`: the leg sets off the moment it is on screen.
// The body's mode, highest first: in the air, landing, on its way, or resting on its floor
export const AIRBORNE = "airborne";
export const LANDING = "landing";
export const TRAVELLING = "travelling";
export const GROUNDED = "grounded";
export const modeOf = ({airborne, landing, trip}) => (airborne ? AIRBORNE : landing ? LANDING : trip?.started ? TRAVELLING : GROUNDED);

// A figure lounging, its legs straight out along the floor, is only ever drawn side-on, turned the way its spot faces, whatever it plays
// there; on its way or in the air it faces as anywhere
export function clipFor(scene, canDraw) {
    const wanted = wantedClip(scene, canDraw);
    const lounging = scene.mode === GROUNDED && scene.place.posture === "lounge" && !scene.trip?.started;
    return lounging ? {...wanted, facing: scene.place.face} : wanted;
}

function wantedClip(scene, canDraw) {
    const {mode, leaving, arriving, trip, landing, place, beat, state, doing, doingFacing = 0} = scene;
    // a figure in the air on its feet falls before anything else, leaving included: it lands first, and then goes; one dropping with its
    // seat stays seated
    if (mode === AIRBORNE && place.posture === "stand") return {clip: scene.chute ? "chute" : "fall", facing: 0};
    // on its run up the bubbles it hops on and on, turned the way it goes
    if (scene.flying) return {clip: "hop_up", facing: scene.flying.way > 0 ? 90 : scene.flying.way < 0 ? 270 : 0};
    if (leaving) return {clip: "exit", facing: 0, once: true, departure: true};
    if (arriving) return {clip: "enter", facing: 0, once: true, arrival: true};
    if (landing) return {clip: "land", facing: 0, once: true, landed: true};
    if (trip?.started && trip.moves && !trip.hopping && beat?.clip === "stumble") {
        return {clip: "stumble", facing: trip.way > 0 ? 90 : 270, posture: "walk", once: true};
    }
    if (trip?.started) return {...legClip(trip, doing, canDraw), ...(trip.moves ? {} : {startsLeg: true})};
    // a hanging figure holds on until it is let go; a beat waits until it has dropped
    if (place.posture === "hang") return {clip: `hang_${place.grip}`, facing: place.face};
    // eager for a run's end it waits for nothing but that end
    if (scene.eager) return {clip: "eager", facing: 0};
    if (scene.watching) return {clip: scene.watching, facing: 0};
    // a beat to play on its chat mark waits while the figure is on its way there
    if (beat && !(beat.onto && trip)) return {clip: beat.clip, facing: beat.facing, once: true, ...(beat.holds && {holds: true}), ...(beat.stretch && {stretch: beat.stretch})};
    // standing at the tab of what waits on the user it points up at it; anywhere else it waits turned toward the compose box
    if (place.view && state === "asking") return {clip: "point", facing: 0};
    // building a box and pushing it go on while the agent waits as well
    if (["asking", "waiting"].includes(state) && !["work", "push"].includes(doing)) return {clip: "waiting", facing: scene.composeFacing ?? 0};
    return {clip: canDraw(doing, place.posture) ? doing : clipOf(state), facing: place.posture === "sit" ? place.face : doingFacing};
}

// the clip of a leg: its hop, or the walk, walked on with what the body is doing where that can be drawn on the move, its steps as much
// quicker as the trip's `pace` is above a walk
function legClip(trip, doing, canDraw) {
    if (trip.hopping) return {clip: trip.clip, facing: trip.facing ?? 0};
    const facing = trip.way > 0 ? 90 : 270;
    const steps = trip.pace > 1 ? {pace: trip.pace} : {};
    return doing !== "idle" && canDraw(doing, "walk") ? {clip: doing, facing, posture: "walk", ...steps} : {clip: "walk", facing, ...steps};
}

export {frameIn, closeAt, canSwitch, goesOnFacing, stretchedFrame} from "../figure/timeline.js";

// a worker's chat mark of the agent giving it work: its dispatch on a task, or its next job; a message to it, its start again and the
// mark's updates give it none (features/workers worker_process_card and worker_moment_cards)
const GIVEN_WORK = /: (started on|sent its next job)/;

// One-off beats, each fired by a card the journal wrote on the agent's row and played once before the held state resumes;
// the first rule a card matches names its beat
const BEATS = [
    // a sin the commandments plugin found in the agent's change, and one it found repented, as its cards in the chat say
    {beat: "sin_committed", matches: (card) => card.pluginCard === "sin-found"},
    {beat: "sin_fixed", matches: (card) => card.pluginCard === "sin-resolved"},
    {beat: "committed", matches: (card) => card.tone === "commit"},
    {beat: "failed", matches: (card) => card.icon === "check" && card.tone === "danger"},
    {beat: "refused", matches: (card) => card.tone === "danger"},
    {beat: "answered", matches: (card) => card.icon === "question"},
    {beat: "task_finished", matches: (card) => card.icon === "todos" && card.tone === "good"},
    {beat: "question_asked", matches: (card) => card.kind === "question"},
    {beat: "messaged", matches: (card) => card.icon === "agents" && GIVEN_WORK.test(card.label)},
    {beat: "fact_filed", matches: (card) => card.icon === "check" && /^(Fact|Reminder) \d+ recorded/.test(card.label)},
    {beat: "check_passed", matches: (card) => card.icon === "check" && card.tone === "good"},
];

// the beat for what the agent says in the chat, by the message's kind: a report
const SAYINGS = {report: "reported"};

// the messages of the agent's session, or of none, as the system's cards and a worker's reports are
const ofSession = (agent, message) => [undefined, null, "", agent.session].includes(message.session);

// The beats for what the agent has said in the chat since `seenAt` (seconds), oldest first, each turned to its message
export const sayingsAfter = (agent, messages, seenAt) =>
    agent
        ? messages
              .filter((m) => m.author === "agent" && SAYINGS[m.data?.kind] && ofSession(agent, m) && createdAt(m) > seenAt)
              .map((m) => ({beat: SAYINGS[m.data.kind], time: createdAt(m), card: refOf(m)}))
              .sort((a, b) => a.time - b.time)
        : [];

// The beats for the user's messages the agent has read since `seenAt` (seconds), oldest first, each turned to its message
export const readingsAfter = (messages, seenAt) =>
    messages
        .filter((m) => m.author === "user" && seconds(m.read_at) > seenAt)
        .map((m) => ({beat: "read_message", time: seconds(m.read_at), card: refOf(m)}))
        .sort((a, b) => a.time - b.time);

// the moment a face on a message is, by who put it there: the user's is aimed at the figure, the agent's is the figure's own to play out
const FACE_MOMENTS = {user: "reacted", agent: "agent_reacted"};

// The beats for faces the user or the agent has put on messages since `seenAt` (seconds), oldest first; `reactions` are the journal's
// reaction rows. The card is the message the face is on.
export function facesAfter(reactions, seenAt) {
    return reactions
        .filter((row) => FACE_MOMENTS[row.author] && createdAt(row) > seenAt)
        .map((row) => ({beat: `${FACE_MOMENTS[row.author]}:${row.emoji}`, time: createdAt(row), card: `messages:${row.message_id}`}))
        .sort((a, b) => a.time - b.time);
}

// every face an agent's act answers, its voice's own and the ones every voice plays (figure/pile.js)
const ACTED_FACES = [...new Set([...Object.values(VOICE_FACES).flatMap((faces) => Object.keys(faces)), ...Object.keys(EVERY_VOICE_FACES)])];

// The beats for faces the agent wrote in its own messages since `seenAt` (seconds), oldest first: a face written counts as one the agent put
// on a message, so it plays the same act; the first acted face in a message is the one played. The card is the message it is in.
export function writtenFacesAfter(agent, messages, seenAt) {
    if (!agent) return [];
    return messages
        .filter((m) => m.author === "agent" && !m.data?.kind && ofSession(agent, m) && createdAt(m) > seenAt)
        .map((m) => ({m, face: ACTED_FACES.map((face) => [face, m.text.indexOf(face)]).filter(([, at]) => at >= 0).sort((a, b) => a[1] - b[1])[0]?.[0]}))
        .filter(({face}) => face)
        .map(({m, face}) => ({beat: `agent_reacted:${face}`, time: createdAt(m), card: refOf(m)}))
        .sort((a, b) => a.time - b.time);
}

// A test run is a chat mark the server guessed is one
const isTestRun = (card) => new ChatMark(card).isTest();

// A test run's ending: its watch card's, or a process card's tone once it is no longer active
const endingOf = (card) => card.watch?.ending || (card.process && !card.active && {good: "finished", bad: "failed"}[card.tone]) || "";

// A pass this many seconds or fewer after a failed test run is that failure fixed
export const FIX_SECONDS = 30 * 60;

// The test run's beat: a failure, a pass, or a pass that fixed the test run before it, which failed within FIX_SECONDS
const testBeat = (card, ended) => {
    if (endingOf(card) !== "finished") return "tests_failed";
    const before = ended.filter((other) => Number(other.time) < Number(card.time)).sort((a, b) => Number(b.time) - Number(a.time))[0];
    const fixed = before && endingOf(before) !== "finished" && Number(card.time) - Number(before.time) <= FIX_SECONDS;
    return fixed ? "tests_fixed" : "tests_passed";
};

// The beats for each test run that has ended since `known` (card key to the ending it had, empty while it ran) was last filled in,
// which this fills in: one seen running, or one that began after `since` (seconds, when the figure began to watch) and ended between
// two looks. An old run's mark that comes back into the chat, already ended, is no ending.
export function testResultsAfter(agent, known, since) {
    const runs = (agent?.data?.cards || []).filter(isTestRun);
    const ended = runs.filter((card) => endingOf(card));
    const fresh = ended.filter((card) => known.get(card.key) === "" || (!known.has(card.key) && Number(card.time) > since));
    runs.forEach((card) => known.set(card.key, endingOf(card)));
    return fresh.map((card) => ({beat: testBeat(card, ended), time: Number(card.time), card: card.key}));
}

// The process cards that have ended since `known` (card key to whether it was active) was last filled in, which this fills in: each one
// seen running and now ended with a tone of good or bad, as {tone, time, card}. A card first seen already ended is not an end.
export function processEndsAfter(agent, known) {
    const cards = (agent?.data?.cards || []).filter((card) => card.process);
    const ended = cards.filter((card) => known.get(card.key) === true && !card.active && ["good", "bad"].includes(card.tone));
    cards.forEach((card) => known.set(card.key, card.active));
    return ended.map((card) => ({tone: card.tone, time: Number(card.time), card: card.key}));
}

// The agent's row with the system's cards for its session, or for no session, among its own, as messages carry them
export const withSystemCards = (agent, messages) =>
    agent && {
        ...agent,
        data: {
            ...(agent.data || {}),
            cards: [
                ...(agent.data?.cards || []),
                ...messages
                    .filter((m) => m.author === "system" && ofSession(agent, m))
                    .map((m) => ({
                        key: refOf(m),
                        time: createdAt(m),
                        icon: m.data.icon,
                        tone: m.data.tone,
                        kind: m.data.kind,
                        pluginCard: m.data.card || "",
                        label: m.text,
                        process: m.data.card_type === "process",
                        sentTo: m.data.sent_to || "",
                        row: m.data.row || "",
                        active: Boolean(m.data.active),
                        watch: m.data.output ? {figure: m.data.figure || "", ending: m.data.ending || ""} : null,
                        guesses: {test: Boolean(m.data.is_test), build: Boolean(m.data.is_build), upload: Boolean(m.data.is_upload)},
                    })),
            ],
        },
    };

export function cardsAfter(agent, known, since) {
    const cards = (agent?.data?.cards || []).filter((card) => card.key && !known.has(card.key));
    cards.forEach((card) => known.add(card.key));
    return cards.filter((card) => Number(card.time) > since).map((card) => ({beat: "card_arrived", time: Number(card.time), card: card.key}));
}

// The beats for what reached the agent's row after `seenAt` (seconds), oldest first: its cards, and the user's own message
export function beatsAfter(agent, seenAt) {
    const cards = (agent?.data?.cards || []).filter((card) => card.time > seenAt);
    const fired = cards
        .map((card) => ({beat: BEATS.find((rule) => rule.matches(card))?.beat, time: card.time, card: card.key}))
        .filter((fire) => fire.beat);
    const heard = Number(agent?.data?.person_at || 0);
    return [...fired, ...(heard > seenAt ? [{beat: "heard", time: heard}] : [])].sort((a, b) => a.time - b.time);
}

// The figure's easter eggs. Each belongs to one true moment read from the agent's row, as the status bar reads it - a beat that fired,
// or a held state that has lasted long enough - and never plays at random or on a timer of its own.
export const EGGS = [
    // the squire runs after a literal bug across the pane when a check goes red
    {clip: "squire_chase", voice: "squire", beat: "failed"},
    // each voice makes its one pointed remark when the user has kept it waiting a long while
    {clip: "pointed", state: "asking", lasted: POINTED_AFTER},
];

// A moment is a beat that fired ({beat, at}) or a held state ({state, since, lasted}); `at` or `since` tells one occurrence from the next
const occurrenceOf = (moment) => moment.time ?? moment.since;
const belongs = (egg, voice, moment) =>
    (!egg.voice || egg.voice === voice) &&
    (egg.beat ? egg.beat === moment.beat : egg.state === moment.state && moment.lasted >= egg.lasted);

// The egg this moment plays, or null: one belongs to it, it has not played for this occurrence, and it is not the egg played last.
// `played` lists the eggs played so far, oldest first, each as {clip, occurrence}.
export function eggFor(voice, moment, played) {
    const egg = EGGS.find((each) => belongs(each, voice, moment));
    if (!egg || played.at(-1)?.clip === egg.clip) return null;
    return played.some((each) => each.clip === egg.clip && each.occurrence === occurrenceOf(moment))
        ? null
        : {clip: egg.clip, occurrence: occurrenceOf(moment)};
}

// What the figure says on the telephone, as the lines of its speech bubble, from the chat mark `card` that set off the call: for a worker sent
// off its number, and the task it holds by its number and its title, read from the `workers` and `tasks` rows; for a message to another
// session that session's name; none for any other mark. The bubble wraps them and cuts what it cannot hold (figure/comicBubble.js).
export function callLines(card, workers) {
    const [table, id] = String(card.row).split(":");
    if (table !== "workers") return [];
    const held = workers.find((worker) => worker.id === Number(id))?.task?.task_id;
    return [`Worker ${id}`, ...(held ? [`Task ${held}!`] : [])];
}
