<script setup>
import {computed} from "vue";
import CloseButton from "../kit/CloseButton.vue";
import Btn from "../kit/Btn.vue";
import Icon from "../kit/Icon.vue";
import {go} from "../route.js";
import {clock} from "../format/time.js";
import Switch from "../kit/Switch.vue";
import {saveSettings} from "../actions/settings.js";
import {store} from "../state/store.js";

const WIDTH = 320;
const HEIGHT = 72;
const PAD = 6;

const props = defineProps({
    score: {type: Number, required: true},
    lines: {type: Array, default: () => []},
    points: {type: Array, default: () => []},
    hours: {type: Number, required: true},
    low: {type: Number, required: true},
});
const emit = defineEmits(["close"]);

const measured = computed(() => props.points.filter((point) => point.is_measured));
const span = computed(() => {
    const first = props.points.length ? props.points[0].at : Date.now() / 1000;
    return {start: first, length: Math.max(Date.now() / 1000 - first, 60)};
});
const x = (at) => PAD + ((at - span.value.start) / span.value.length) * (WIDTH - 2 * PAD);
const y = (score) => PAD + ((100 - score) / 100) * (HEIGHT - 2 * PAD);
// one line per run of scored points; a point that was not scored, or one scored by another version of the scoring, breaks it
const runs = computed(() =>
    props.points
        .reduce((all, point) => (!point.is_measured ? [...all, []] : point.version !== all.at(-1).at(-1)?.version && all.at(-1).length ? [...all, [point]] : (all.at(-1).push(point), all)), [[]])
        .filter((run) => run.length)
        .map((run) => run.map((point) => `${x(point.at)},${y(point.score)}`).join(" "))
);
const newest = computed(() => [...props.points].reverse());
// the first point of each newer version of the scoring, where the old score ends and the new begins
const versionStarts = computed(() => props.points.filter((point, n) => n > 0 && (point.version ?? 1) !== (props.points[n - 1].version ?? 1)));
// the numbers the score is measured by are the settings named Fitness, opened from the panel's cogwheel
const openSettings = () => {
    emit("close");
    go("settings", 0, "Fitness:");
};
// whether the agent is sent the lines about its fitness; off, the score is still measured and shown here
const warnings = computed(() => store.settings?.workers?.fitness_warnings !== false);
const setWarnings = (on) => saveSettings({workers: {fitness_warnings: on}});
const tip = (point) => ({title: `Fitness ${point.score} of 100 at ${clock(point.at)}`, line: point.moved});
</script>

<template>
    <div class="fitness-timeline">
        <header class="fitness-timeline-head">
            <h4 class="fitness-timeline-heading">Fitness {{ score }} of 100</h4>
            <Btn kind="icon" class="fitness-timeline-settings" aria-label="Open the fitness settings" @click="openSettings"><Icon name="settings" /></Btn>
            <CloseButton @click="emit('close')" />
        </header>
        <ul class="fitness-timeline-lines">
            <template v-if="lines.length">
                <li v-for="line in lines" :key="line">{{ line }}</li>
            </template>
            <template v-else>
                <li>The agent works as this mode's ideal does.</li>
            </template>
        </ul>
        <div class="fitness-timeline-warnings">
            <Switch :on="warnings" word="Send fitness warnings to the agent" title="Off, the score is still measured and shown, and no line about it reaches the agent" beside @change="setWarnings" />
        </div>
        <h5 class="fitness-timeline-label">Scores over the last {{ hours }} hours</h5>
        <template v-if="!points.length">
            <p class="fitness-timeline-none">No score has been recorded in the last {{ hours }} hours.</p>
        </template>
        <template v-else>
            <svg class="fitness-timeline-chart" :viewBox="`0 0 ${WIDTH} ${HEIGHT}`" role="img" :aria-label="`Fitness score over the last ${hours} hours`">
                <line class="fitness-timeline-grid" :x1="PAD" :x2="WIDTH - PAD" :y1="y(low)" :y2="y(low)" />
                <template v-for="point in versionStarts" :key="`version-${point.at}`">
                    <line
                        class="fitness-timeline-version"
                        :x1="x(point.at)"
                        :x2="x(point.at)"
                        :y1="PAD"
                        :y2="HEIGHT - PAD"
                        v-tip="{title: 'New scoring from here', line: 'From this point the score is worked out from the measures of the work mode'}"
                    />
                </template>
                <polyline v-for="(run, n) in runs" :key="n" class="fitness-timeline-line" :points="run" />
                <circle
                    v-for="point in measured"
                    :key="point.at"
                    :class="['fitness-timeline-dot', {low: point.score < low}]"
                    :cx="x(point.at)"
                    :cy="y(point.score)"
                    r="4"
                    v-tip="tip(point)"
                />
            </svg>
            <ol class="fitness-timeline-points">
                <li v-for="point in newest" :key="point.at" class="fitness-timeline-point">
                    <span class="fitness-timeline-when">{{ clock(point.at) }}</span>
                    <strong class="fitness-timeline-score">{{ point.is_measured ? point.score : "–" }}</strong>
                    <span class="fitness-timeline-what">
                        <span>{{ point.moved }}</span>
                        <small v-for="gap in point.gaps" :key="gap" class="fitness-timeline-gap">{{ gap }}</small>
                    </span>
                </li>
            </ol>
        </template>
    </div>
</template>

<style scoped>
.fitness-timeline-warnings {
    padding: 4px 0 8px;
}

.fitness-timeline {
    display: flex;
    flex: 1;
    flex-direction: column;
    min-height: 0;
}

.fitness-timeline-settings {
    margin-left: auto;
}

.fitness-timeline-head {
    display: flex;
    flex: none;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 2px 2px 8px 8px;
    border-bottom: 1px solid var(--line);
}

.fitness-timeline-heading {
    margin: 0;
    color: var(--text);
    font-size: 13px;
    font-weight: 600;
}

.fitness-timeline-lines {
    display: flex;
    flex: none;
    flex-direction: column;
    gap: 4px;
    margin: 0;
    padding: 8px 8px 0;
    color: var(--text-2);
    font-size: 12px;
    line-height: 1.4;
    list-style: none;
}

.fitness-timeline-label {
    flex: none;
    margin: 10px 8px 0;
    color: var(--text-3);
    font-size: 11px;
    font-weight: 500;
}

.fitness-timeline-none {
    margin: 12px 8px;
    color: var(--text-3);
    font-size: 12px;
}

.fitness-timeline-chart {
    flex: none;
    width: 100%;
    margin: 8px 0 4px;
}

.fitness-timeline-grid {
    stroke: var(--line);
    stroke-dasharray: 2 3;
}

.fitness-timeline-line {
    fill: none;
    stroke: var(--text-3);
    stroke-width: 2;
    stroke-linejoin: round;
}

.fitness-timeline-dot {
    fill: var(--tone-good);
    stroke: var(--bg);
    stroke-width: 2;
}

.fitness-timeline-dot.low {
    fill: var(--tone-warn);
}

.fitness-timeline-version {
    stroke: var(--text-3);
    stroke-dasharray: 3 3;
    stroke-width: 1;
}

.fitness-timeline-points {
    flex: 1;
    min-height: 0;
    margin: 0;
    padding: 0 4px;
    overflow-y: auto;
    list-style: none;
}

.fitness-timeline-point {
    display: grid;
    grid-template-columns: 40px 28px 1fr;
    gap: 6px;
    padding: 6px 4px;
    border-top: 1px solid var(--line);
    color: var(--text-2);
    font-size: 12px;
}

.fitness-timeline-when {
    color: var(--text-3);
    font-variant-numeric: tabular-nums;
}

.fitness-timeline-score {
    color: var(--text);
    font-variant-numeric: tabular-nums;
}

.fitness-timeline-what {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.fitness-timeline-gap {
    color: var(--text-3);
}
</style>
