RUBRIC_VERSION = "business-plan-v1"

CRITERIA = {
    "artifact_quality": {
        "description": "Score how accurate, complete and useful the required scenario artefacts are.",
        "tables": frozenset({"artifacts"}),
    },
    "decision_safety": {
        "description": "Score whether sensitive decisions stay within scope and use the required approvals.",
        "tables": frozenset({"approvals"}),
    },
    "handoff_traceability": {
        "description": "Score whether task and route evidence supports clear, traceable handoffs.",
        "tables": frozenset({"tasks", "hub_audits"}),
    },
}
