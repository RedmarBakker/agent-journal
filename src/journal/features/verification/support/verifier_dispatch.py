from journal.features.profiles.support.profile_files import ProfileFiles
from journal.features.workers.support.worker_launch import WorkerLaunch
from journal.models.agent_role import AgentRole
from journal.models.link import Link
from journal.models.scoped import Scoped
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.providers.providers import Providers
from journal.repositories.links import Links
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.rejection import Rejection

VERIFIES = "verifies"
DIOGENES = "Diogenes, lamp-bearer of the honest reason"
# the profile whose model a verifier runs on, the general one, for a careful judgement that invents nothing; its instructions are not given, since the brief is the verifier's whole instruction
MODEL_PROFILE = "journal-medior"


class VerifierDispatch:
    """Sends a verifier, as the journal and never an agent: a worker named after Diogenes, in the verifier's role, handed the evidence as its whole brief, linked to the row whose dismissal it judges, and launched like any worker; and finds the row a verifier judges."""

    def __init__(self, workers: Workers, links: Links, launch: WorkerLaunch, providers: Providers, profiles: ProfileFiles) -> None:
        self.workers, self.links, self.launch, self.providers, self.profiles = workers, links, launch, providers, profiles

    def sent(self, target: Scoped, brief: str) -> Worker:
        provider = self.providers.default()
        worker = self.workers.save(Worker(environment_id=target.environment_id, name=DIOGENES, brief=brief, role=AgentRole.VERIFIER, provider=provider.name, model=provider.profile_model(self.profiles.read(MODEL_PROFILE))), Actor.system())
        self.links.save(Link(source=Ref.build(worker), target=Ref.build(target), kind=VERIFIES), Actor.system())
        return self.launch.launched(worker, Actor.system())

    def judged(self, number: int) -> Ref:
        targets = self.links.targets(self.workers.find(number), VERIFIES)
        if not targets:
            raise Rejection(f"worker {number} is no verifier: only a verifier the journal sent gives a verdict")
        return targets[0]
