from argparse import Namespace
from datetime import datetime, timezone

from journal.console.command import VERIFIER_KINDS, Command
from journal.features.verification.support.model_fit_evidence import MODEL_VERDICTS
from journal.features.verification.support.verifier_dispatch import VerifierDispatch
from journal.models.reader_report import ReaderReport
from journal.models.worker import Worker
from journal.repositories.agents import Agents
from journal.repositories.reader_reports import ReaderReports
from journal.repositories.workers import Workers
from journal.support.caller import Caller
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource

SOUND_VERDICT, REFUTED_VERDICT = "yes", "no"


class VerdictCommand(Command):
    """journal verdict yes|no "<reason>" and journal verdict model too-strong|right|too-weak "<reason>": a verifier's one answer, on the dismissal it judges, or on whether a worker's model fit its merged work, kept on the worker and among its dispatcher's model fits; yes when the dismissal is sound, no when the run's output contradicts it; a no opens the report again and holds the agent's writes until its reader is written anew, and either verdict ends the verifier's session."""

    noun = "verdict"
    default_verb = "give"
    callers = {"give": VERIFIER_KINDS, "model": VERIFIER_KINDS}

    def __init__(self, dispatch: VerifierDispatch, reports: ReaderReports, workers: Workers, agents: Agents, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.dispatch, self.reports, self.workers, self.agents = dispatch, reports, workers, agents

    def arguments(self, verbs) -> None:
        giving = self.verb(verbs, "give", "your verdict on the dismissal you judge: yes, it is sound, or no, the run's output contradicts it, with one reason")
        giving.add_argument("verdict", choices=(SOUND_VERDICT, REFUTED_VERDICT))
        giving.add_argument("reason")
        fitting = self.verb(verbs, "model", "your verdict on whether a worker's model fit its merged work: too-strong, right or too-weak, with one line of reason")
        fitting.add_argument("verdict", choices=MODEL_VERDICTS)
        fitting.add_argument("reason")

    def give(self, args: Namespace, caller: Caller) -> int:
        if caller.verifier_number is None:
            raise Rejection("only a verifier the journal sent gives a verdict")
        judged = self.dispatch.judged(caller.verifier_number)
        if judged.type != ReaderReport.table():
            raise Rejection("you judge a worker's model: journal verdict model too-strong|right|too-weak \"<reason>\"")
        report = self.reports.find(judged.id)
        moment = self.time_source.moment()
        judged = report.judged_sound(args.reason, caller.agent_session, moment) if args.verdict == SOUND_VERDICT else report.refuted(args.reason, caller.agent_session, moment)
        self.reports.save(judged, caller.actor)
        print(f"verdict {args.verdict} on reader report {report.id}: {args.reason}; your session ends now")
        return 0

    def model(self, args: Namespace, caller: Caller) -> int:
        if caller.verifier_number is None:
            raise Rejection("only a verifier the journal sent gives a verdict")
        judged = self.dispatch.judged(caller.verifier_number)
        if judged.type != Worker.table():
            raise Rejection("you judge a dismissal: journal verdict yes|no \"<reason>\"")
        verdict = args.verdict.replace("-", " ")
        worker = self.workers.save(self.workers.find(judged.id).model_judged(verdict, args.reason, caller.agent_session, self.time_source.moment().timestamp()), caller.actor)
        dispatcher = self.agents.active_main_agent(worker.dispatcher) if worker.dispatcher else None
        if dispatcher is not None:
            self.agents.save(dispatcher.model_fit_kept(worker.row_id, verdict), caller.actor)
        print(f"verdict {verdict} on worker {worker.id}'s model: {args.reason}; your session ends now")
        return 0
