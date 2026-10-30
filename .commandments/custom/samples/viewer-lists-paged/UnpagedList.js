import {api} from "../api/client.js";
import {pageOf} from "../sync/paging.js";

// @sin UnpagedViewerListDetector
export const everyPlugin = () => api.list("plugins");

// @sin UnpagedViewerListDetector
export const closedSecrets = () => api.list("secrets", {closed: true});

// @righteous UnpagedViewerListDetector
export const plugins = () => api.list("plugins", {limit: pageOf("plugins")});

// kept: the rows it holds
export const held = (ids) => api.list("tasks", {ids});
