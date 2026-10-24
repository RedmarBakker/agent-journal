import {api} from "../api/client.js";
import {pageOf} from "../sync/paging.js";

// flagged: the whole table
export const everyPlugin = () => api.list("plugins");

// flagged: options, but no limit
export const closedSecrets = () => api.list("secrets", {closed: true});

// kept: a page
export const plugins = () => api.list("plugins", {limit: pageOf("plugins")});

// kept: the rows it holds
export const held = (ids) => api.list("tasks", {ids});
