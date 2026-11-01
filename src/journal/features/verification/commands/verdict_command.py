from argparse import Namespace
from journal.console.command import Command
from journal.features.verification.support.verifier_dispatch import VerifierDispatch
from journal.models.reader_report import ReaderReport
from journal.repositories.reader_reports import ReaderReports
from journal.support.caller import Caller
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource

SOUND_VERDICT, REFUTED_VERDICT = "yes", "no"


class VerdictCommand(Command):
    """journal verdict yes|no "<reason>": a verifier's one answer on the dismissal it judges; yes when the dismissal is sound, no when the run's output contradicts it; a no opens the report again and holds the agent's writes until its reader is written anew, and either verdict ends the verifier's session."""

    noun = "verdict"
    default_verb = "give"

    def __init__(self, dispatch: VerifierDispatch, reports: ReaderReports, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.dispatch, self.reports = dispatch, reports

    def arguments(self, verbs) -> None:
        giving = self.verb(verbs, "give", "your verdict on the dismissal you judge: yes, it is sound, or no, the run's output contradicts it, with one reason")
        giving.add_argument("verdict", choices=(SOUND_VERDICT, REFUTED_VERDICT))
        giving.add_argument("reason")
    def give(self, args: Namespace, caller: Caller) -> int:
        judged = self.dispatch.judged(caller.verifier_number)
        if judged.type != ReaderReport.table():
            raise Rejection("you judge only the reader report dismissal you were sent")
        report = self.reports.find(judged.id)
        moment = self.time_source.moment()
        judged = report.judged_sound(args.reason, caller.agent_session, moment) if args.verdict == SOUND_VERDICT else report.refuted(args.reason, caller.agent_session, moment)
        self.reports.save(judged, caller.actor)
        print(f"verdict {args.verdict} on reader report {report.id}: {args.reason}; your session ends now")
        return 0

