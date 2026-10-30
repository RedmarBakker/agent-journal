from dataclasses import dataclass
import shlex

from tests.lab.trial_setting import TrialSetting


@dataclass(frozen=True)
class FindingTask:
    """A journal task command that turns a lab finding into a setting trial."""

    finding_id: str
    summary: str
    report_id: int
    metric_id: str
    metric_version: str
    scenario_ids: tuple[str, ...]
    trace_refs: tuple[str, ...]
    setting: TrialSetting

    def __post_init__(self) -> None:
        text = (self.finding_id, self.summary, self.metric_id, self.metric_version)
        if any(not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value for value in text):
            raise ValueError("a finding task needs single-line finding, metric and version details")
        if type(self.report_id) is not int or self.report_id < 1:
            raise ValueError("a finding task needs a positive report ID")
        if not isinstance(self.setting, TrialSetting):
            raise ValueError("a finding task needs its named trial setting")
        if not isinstance(self.scenario_ids, tuple) or not self.scenario_ids or any(not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value for value in self.scenario_ids) or len(set(self.scenario_ids)) != len(self.scenario_ids):
            raise ValueError("a finding task needs unique scenario IDs")
        if not isinstance(self.trace_refs, tuple) or not self.trace_refs or any(not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value for value in self.trace_refs):
            raise ValueError("a finding task needs replayable trace references")
        if len(set(self.trace_refs)) != len(self.trace_refs):
            raise ValueError("finding task trace references must be unique")

    @property
    def title(self) -> str:
        return f"Trial {self.setting.option.key} from report {self.report_id}: {self.summary}"

    @property
    def brief(self) -> str:
        setting = self.setting.manifest()
        return "\n".join((
            f"Finding: {self.finding_id} - {self.summary}",
            f"Lab report: report {self.report_id}",
            f"Metric: {self.metric_id} (version {self.metric_version})",
            f"Scenarios: {', '.join(self.scenario_ids)}",
            f"Replayable traces: {', '.join(self.trace_refs)}",
            f"Setting: {setting['key']}; owner: {setting['owner']}; default off; candidate on in design B only.",
            "Keep the default off. Keep the candidate behind this setting and keep both paths' stories valid.",
            "Before any confirmatory batch, copy and complete every field from `journal doc show 10 --section 19`; explain each not_applicable field.",
            "Freeze the manifest and decision rule before confirmatory outcomes. Real spending still needs the owner's L02 approval.",
            "After the recorded outcome, keep_eligible needs owner review plus explicit default-change and switch-removal tasks; drop needs candidate and switch removal; inconclusive needs a bounded follow-up or rollback deadline while A stays active and the setting stays off.",
            "Only the authorized owner records the outcome and report/task/rule references in NOTES.md. This task never flips a default or authorizes deployment or spend.",
        ))

    @property
    def journal_command(self) -> str:
        return shlex.join(("journal", "task", "create", self.title, "--report", str(self.report_id), "--brief", self.brief))
