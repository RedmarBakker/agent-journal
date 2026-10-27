from journal.engine.nudge import Nudge


class LawsNudges:
    MISSING_MODEL = Nudge("laws", "name_the_model", "name a model in the dispatch: the least expensive one that reliably fits the work", "")
    MISSING_PROFILE = Nudge("laws", "name_a_profile", "the dispatch has no profile of this project: {{asked}}", "use one of: {{profiles|cap=200}}", longest_characters=285, longest_reason="it lists every profile the dispatch may name")
    UNBOUND_DISPATCH = Nudge("laws", "bind_the_job", "the dispatch has no concrete job", "give it a description and a bounded prompt")
    LONG_OUTPUT = Nudge("laws", "cap_the_output", "that result was {{lines}} lines", "cap output with grep, head or tail")
