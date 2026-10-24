from journal.engine.nudge import Nudge


class LawsNudges:
    MISSING_MODEL = Nudge("laws", "name_the_model", "the dispatch names no model", "name the least expensive model that reliably fits the work")
    MISSING_PROFILE = Nudge("laws", "name_a_profile", "the dispatch names no profile of this project: {{asked}}", "use one of: {{profiles}}")
    UNBOUND_DISPATCH = Nudge("laws", "bind_the_job", "the dispatch binds the agent to no concrete job", "give it a description and a bounded prompt")
    LONG_OUTPUT = Nudge("laws", "cap_the_output", "that result was {{lines}} lines", "cap output with grep, head or tail")
