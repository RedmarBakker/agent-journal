from journal.support.option import USER, Option


class ReviewingOptions:
    REVIEWER = Option("reviewing.reviewer", "Orchestrator: a reviewer checks each worker's work", "In orchestrator mode, a worker's clock-out goes to a reviewer the journal sends, which reads the brief and each proof, runs the tests the proofs name, judges the changed files for sins and reports each point to the agent; the agent then sends the work back or merges it. Off, the agent checks each clock-out itself", False, kind="switch", setter=USER)
