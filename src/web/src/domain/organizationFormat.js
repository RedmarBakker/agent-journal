export const cardinalityLine = (cardinality) => ({journal: "One for all plans", plan: "One per plan", many: "One per job"})[cardinality] || cardinality;

export const modelLine = (models = {}) => [
    models.claude && `Claude: ${models.claude}`,
    models.codex && `Codex: ${models.codex}`,
    models.effort && `Effort: ${models.effort}`,
].filter(Boolean).join(" · ") || "No model set";
