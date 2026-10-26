from tests.simulation.hold_lifts import HoldLifts
from tests.simulation.no_contradiction import NoContradiction
from tests.simulation.no_faults import NoFaults
from tests.simulation.progress import Progress
from tests.simulation.stack_bounded import StackBounded
from tests.simulation.stop_releases import StopReleases
from tests.simulation.wait_ends import WaitEnds
from tests.simulation.worker_unlocks import WorkerUnlocks

ALL = (HoldLifts(), StopReleases(), StackBounded(), WaitEnds(), NoContradiction(), NoFaults(), WorkerUnlocks(), Progress())
