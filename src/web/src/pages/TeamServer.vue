<script setup>
import TeamAddressFact from "./TeamAddressFact.vue";
import ListBox from "../kit/ListBox.vue";
import StateDot from "../kit/StateDot.vue";
import "./team.css";

defineProps({standing: {type: Object, required: true}});
</script>

<template>
    <ListBox title="Team server">
        <div class="team-block">
            <dl class="team-facts">
                <TeamAddressFact label="Address" :address="standing.address" />
                <div>
                    <dt>State</dt>
                    <dd><StateDot state="done" />Running</dd>
                </div>
            </dl>
        </div>
    </ListBox>
</template>
