<script setup>
import {api} from "../api/client.js";
import {pageOf} from "../sync/paging.js";

// @sin UnpagedViewerListPageDetector
// @sin UnpagedViewerListDetector
const plugins = api.list("plugins");
// @righteous UnpagedViewerListPageDetector
const secrets = api.list("secrets", {limit: pageOf("secrets")});
</script>

<template>
    <div>{{ plugins }} {{ secrets }}</div>
</template>
