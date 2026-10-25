from journal.features.profiles.support.profile_files import ProfileFiles
from journal.features.verification.support.verifier_runner import VerifierRunner
from journal.models.link import Link
from journal.models.scoped import Scoped
from journal.models.support.ref import Ref
from journal.models.verifier import Verifier
from journal.providers.providers import Providers
from journal.repositories.links import Links
from journal.repositories.verifiers import Verifiers
from journal.support.actor import Actor
from journal.support.rejection import Rejection

VERIFIES = "verifies"
DIOGENES = "Diogenes, lamp-bearer of the honest reason"
# the profile whose model a verifier runs on, the general one, for a careful judgement that invents nothing; its instructions are not given, since the brief is the verifier's whole instruction
MODEL_PROFILE = "journal-medior"


class VerifierDispatch:
    """Sends a verifier, as the journal and never an agent, on the general model or, for a light judgement, the program's fast one: the idle one on that model that judged last, in its own session with its memory of that judgement, else a new one named after Diogenes, handed the evidence as its whole brief, linked to the row whose dismissal it judges, and started by its own runner; and finds the row a verifier judges now, the last it was linked to."""

    def __init__(self, verifiers: Verifiers, links: Links, runner: VerifierRunner, providers: Providers, profiles: ProfileFiles) -> None:
        self.verifiers, self.links, self.runner, self.providers, self.profiles = verifiers, links, runner, providers, profiles

    def sent(self, target: Scoped, brief: str) -> Verifier:
        return self.sent_on(target, brief, self.general_model())

    def sent_fast(self, target: Scoped, brief: str) -> Verifier:
        return self.sent_on(target, brief, self.providers.default().question_model or self.general_model())

    def sent_on(self, target: Scoped, brief: str, model: str) -> Verifier:
        idle = [verifier for verifier in self.verifiers.idle() if verifier.model == model]
        if idle:
            return self.judging(idle[0].next_judgement(brief), target, idle[0].session)
        return self.judging(Verifier(environment_id=target.environment_id, name=DIOGENES, brief=brief, provider=self.providers.default().name, model=model), target, "")

    def general_model(self) -> str:
        return self.providers.default().profile_model(self.profiles.read(MODEL_PROFILE))

    def judging(self, verifier: Verifier, target: Scoped, resume: str) -> Verifier:
        verifier = self.verifiers.save(verifier, Actor.system())
        self.links.save(Link(source=Ref.build(verifier), target=Ref.build(target), kind=VERIFIES), Actor.system())
        return self.runner.start(verifier, resume)

    def judged(self, number: int) -> Ref:
        targets = self.links.targets(self.verifiers.find(number), VERIFIES)
        if not targets:
            raise Rejection(f"verifier {number} judges nothing: only a verifier the journal sent gives a verdict")
        return targets[-1]
