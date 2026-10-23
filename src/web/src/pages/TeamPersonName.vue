<script setup>
import {initial} from "../domain/team.js";
import "./team.css";

defineProps({person: Object, sub: String});
</script>

<template>
    <span class="team-initial">{{ initial(person.name) }}</span>
    <span class="team-row-main">
        <b>
            {{ person.name }}
            <template v-if="person.me">
                <span class="team-tag">You</span>
            </template>
        </b>
        <span class="team-row-sub">{{ sub }}</span>
    </span>
</template>
