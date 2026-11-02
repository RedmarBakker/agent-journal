# A stable supervisor smoke stall

The owner marks the smoke seed task `supervisor_reserved` before starting its
plan. The task stays open and unheld in the current phase. This mark requests
supervisor diagnosis; it is not a plan pause, checkpoint, external wait or grant
capability. The existing actionable-stall and driver-state rules stay unchanged.

Task selection excludes reserved tasks. The task's start guard also refuses an
explicit start or worker assignment and names the owner's way out. Only the
owner's task update can set or clear the mark, and only unstarted, unheld work can
be reserved. Ordinary task edits, block/unblock and driver session restart retain it.

A diagnostic created through the bounded supervisor route is an ordinary task.
The existing PlanWorkAvailable delivery and PlanTaskAssigner can select that task
while skipping the reserved seed. Clearing the reservation restores ordinary
execution. Cancelling the plan remains available to its owner.

This is smaller than admitting a busy driver or extending driver eligibility to
intermediate states: neither supervisor gate changes, and no prompt must persuade
the real driver to leave an executable task alone. Setup uses an owner task update
instead of a block/unblock race, verifies the reservation before enrollment and
after its deliberately failing check, and allows five minutes for driver startup.

Stories cover an idle stop, explicit start, worker assignment, block/unblock,
restart, owner release, ordinary diagnostic execution, invalid reservation data
and refusal to reserve work already in progress or assigned to a worker. The
supervisor driver test also exercises admission and diagnostic delivery with the
reserved seed in the enrolled phase.
