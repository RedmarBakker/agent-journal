from journal.support.option import Option


class SkillsOptions:
    """The options of the skills feature."""

    START_SKILLS = Option("skills.session_start", "Skills read at session start", "The skills an agent must read when its session starts, before it may use any other tool", ["journal", "etiquette"], option_type="lines")
    COMPACTION_SKILLS = Option("skills.after_compaction", "Skills read after a compaction", "The skills an agent must read again when its session resumes after a compaction, before it may use any other tool", ["journal", "etiquette"], option_type="lines")
