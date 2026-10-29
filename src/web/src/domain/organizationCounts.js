import {rows} from "../sync/rows.js";

// What the organization's sidebar reads: each domain's live figures, a row apiece in domain_counts, by the domain's id.
export const domainCounts = () => Object.fromEntries(rows("domain_counts").map((row) => [row.name, {plansActive: row.plans_active, roles: row.roles}]));

export const runningIn = (counts, domain) => Object.values((counts[domain] || {roles: {}}).roles).reduce((total, role) => total + role.instances, 0);
