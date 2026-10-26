from typing import Callable

from journal.features.workers.support.allowed_models import AllowedModels
from journal.features.verification.support.verifier_runner import VerifierRunner
from journal.models.link import Link
from journal.models.scoped import Scoped
from journal.models.support.ref import Ref
from journal.models.verifier import Verifier
from journal.providers.providers import Providers
from journal.repositories.links import Links
from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.setting_rows import SettingRows
from journal.repositories.verifiers import Verifiers
from journal.support.actor import Actor
from journal.support.rejection import Rejection

VERIFIES = "verifies"
DIOGENES = "Diogenes, lamp-bearer of the honest reason"


class VerifierDispatch:
    """Sends a verifier, as the journal and never an agent, on the general model, Sonnet at the least, since a verdict on a job's model is a judgement: the idle one on that model that judged last and whose process has ended, in its own session with its memory of that judgement, else a new one named after Diogenes, handed the evidence as its whole brief, linked to the row whose dismissal it judges, and started by its own runner; and finds the row a verifier judges now, the last it was linked to."""

    def __init__(self, verifiers: Verifiers, links: Links, runner: VerifierRunner, providers: Providers, allowed: AllowedModels, settings: SettingRows) -> None:
        self.verifiers, self.links, self.runner, self.providers, self.allowed, self.settings = verifiers, links, runner, providers, allowed, settings
        self.waiting: list[tuple[Scoped, str, str, Callable[[], bool]]] = []

    def sent(self, target: Scoped, brief: str, pending: Callable[[], bool]) -> Verifier | None:
        return self.dispatched_with(target, brief, self.general_model(), pending)

    def dispatched_with(self, target: Scoped, brief: str, model: str, pending: Callable[[], bool]) -> Verifier | None:
        idle = [verifier for verifier in self.verifiers.idle() if verifier.model == model]
        if idle:
            return self.judging(idle[0].next_judgement(brief), target, idle[0].session)
        if len(self.verifiers.working()) >= self.settings.integer(WorkersOptions.VERIFIER_LIMIT):
            self.waiting.append((target, brief, model, pending))
            return None
        return self.judging(Verifier(environment_id=target.environment_id, name=DIOGENES, brief=brief, provider=self.providers.default().name, model=model), target, "")

    # a judgement still waiting is sent once a verifier is free; one whose row no longer waits for a verdict, judged meanwhile or its
    # dismissal taken back, is dropped
    def released(self) -> None:
        while self.waiting:
            target, brief, model, pending = self.waiting[0]
            if pending() and self.dispatched_with(target, brief, model, pending) is None:
                return
            self.waiting.pop(0)

    def general_model(self) -> str:
        return self.allowed.strongest(self.providers.default().name, "verifier")

    def judging(self, verifier: Verifier, target: Scoped, resume: str) -> Verifier:
        verifier = self.verifiers.save(verifier, Actor.system())
        self.links.save(Link(source=Ref.build(verifier), target=Ref.build(target), kind=VERIFIES), Actor.system())
        return self.runner.start(verifier, resume)

    def judged(self, number: int) -> Ref:
        targets = self.links.targets(self.verifiers.find(number), VERIFIES)
        if not targets:
            raise Rejection(f"verifier {number} judges nothing: only a verifier the journal sent gives a verdict")
        return targets[-1]
