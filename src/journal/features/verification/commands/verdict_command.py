from argparse import Namespace
from datetime import datetime, timezone

from journal.console.command import WORKER_KINDS, Command
from journal.features.verification.support.verifier_dispatch import VerifierDispatch
from journal.repositories.reader_reports import ReaderReports
from journal.support.caller import Caller
from journal.support.rejection import Rejection

SOUND_VERDICT, REFUTED_VERDICT = "yes", "no"


class VerdictCommand(Command):
    """journal verdict yes|no "<reason>": a verifier's one answer on the dismissal it judges, yes when the dismissal is sound, no when the run's output contradicts it; a no opens the report again and holds the agent's writes until its reader is written anew, and either verdict ends the verifier's session."""

    noun = "verdict"
    default_verb = "give"
    callers = {"give": WORKER_KINDS}

    def __init__(self, dispatch: VerifierDispatch, reports: ReaderReports) -> None:
        self.dispatch, self.reports = dispatch, reports

    def arguments(self, verbs) -> None:
        giving = self.verb(verbs, "give", "your verdict on the dismissal you judge: yes, it is sound, or no, the run's output contradicts it, with one reason")
        giving.add_argument("verdict", choices=(SOUND_VERDICT, REFUTED_VERDICT))
        giving.add_argument("reason")

    def give(self, args: Namespace, caller: Caller) -> int:
        if caller.worker_number is None:
            raise Rejection("only a verifier the journal sent gives a verdict")
        report = self.reports.find(self.dispatch.judged(caller.worker_number).id)
        moment = datetime.now(timezone.utc)
        judged = report.judged_sound(args.reason, caller.agent_session, moment) if args.verdict == SOUND_VERDICT else report.refuted(args.reason, caller.agent_session, moment)
        self.reports.save(judged, caller.actor)
        print(f"verdict {args.verdict} on reader report {report.id}: {args.reason}; your session ends now")
        return 0
