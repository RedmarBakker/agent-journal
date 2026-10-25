<script setup>
import {onMounted, ref} from "vue";
import {api} from "../api/client.js";
import {peek} from "../route.js";
import {standingLine} from "../domain/requests.js";

const requests = ref(null);
const filed = ref([]);
onMounted(async () => {
    requests.value = (await api.requests()).rows;
    filed.value = (await api.filedRequests()).rows;
});
</script>

<template>
    <div class="requests" data-requests-page>
        <h2 class="title">Requests</h2>
        <template v-if="requests && !requests.length">
            <p class="none">Nobody has asked anything of you.</p>
        </template>
        <template v-for="task in requests || []" :key="task.id">
            <button type="button" class="line" @click="peek('tasks', task.id)">Task {{ task.id }}: {{ task.title }}</button>
        </template>
        <template v-if="filed.length">
            <h3 class="head">You asked</h3>
            <template v-for="task in filed" :key="task.id">
                <button type="button" class="line" data-filed @click="peek('tasks', task.id)">Task {{ task.id }}: {{ task.title }} · {{ standingLine(task) }}</button>
            </template>
        </template>
    </div>
</template>

<style scoped>
.requests {
    padding: 16px 20px;
}

.title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 8px;
}

.head {
    margin-top: 12px;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-2);
}

.none {
    color: var(--text-3);
    font-size: 12.5px;
}

.line {
    display: block;
    text-align: left;
    padding: 4px 0;
    font-size: 12.5px;
    color: var(--text);
}
</style>
