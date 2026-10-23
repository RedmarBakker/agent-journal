<script setup>
import ListBox from "../kit/ListBox.vue";
import "./team.css";

const LEAD = "Workers your own agents started from the team's pool. They run on a colleague's machine and report to you here.";
</script>

<template>
    <ListBox title="Your workers on other machines" :count="0" :lead="LEAD">
        <div class="team-block">
            <p class="team-fine">None of your workers runs on another machine.</p>
        </div>
    </ListBox>
</template>
