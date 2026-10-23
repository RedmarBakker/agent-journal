<script setup>
import CopyButton from "../kit/CopyButton.vue";
import ListBox from "../kit/ListBox.vue";
import StateDot from "../kit/StateDot.vue";
import "./team.css";

defineProps({standing: {type: Object, required: true}});
</script>

<template>
    <ListBox title="Team server">
        <div class="team-block">
            <dl class="team-facts">
                <div class="wide">
                    <dt>Address</dt>
                    <dd>
                        <span>{{ standing.address }}</span>
                        <CopyButton :text="standing.address" />
                    </dd>
                </div>
                <div>
                    <dt>State</dt>
                    <dd><StateDot state="done" />Running</dd>
                </div>
            </dl>
        </div>
    </ListBox>
</template>
