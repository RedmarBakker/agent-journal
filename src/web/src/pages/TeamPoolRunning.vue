<script setup>
import ListBox from "../kit/ListBox.vue";
import "./team.css";

const LEAD = "Workers that one person's agent started on another person's machine, from what that machine offers.";
</script>

<template>
    <ListBox title="Pool workers running" :count="0" :lead="LEAD">
        <div class="team-block">
            <p class="team-fine">No pool worker is running. No machine offers workers to the team yet.</p>
        </div>
    </ListBox>
</template>
