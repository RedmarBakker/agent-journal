from tests.stories.fixtures.worker.role_peer_workers import RolePeerWorkers


class RoleCrossDomainWorkers(RolePeerWorkers):
    """An alpha builder works while a beta Role is idle with a resumable session."""

    peer_role = "reviewer"
    peer_task = "beta review"
