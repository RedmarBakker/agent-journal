from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class BriefingNudges:
    JOURNAL_READY = Nudge("briefing", "journal_ready", "the journal is ready on {{env}}", repeat=Timeout.seconds(0))
    ACTIVE_RULES = Nudge("briefing", "rules_in_force", "{{count}} rules in force: {{rows|cap=3000}}", repeat=Timeout.seconds(0), longest_characters=3031, longest_reason="it lists every rule at the session start")
    ENVIRONMENT_MEMORIES = Nudge("briefing", "memories_here", "your memories, heaviest first: {{rows|cap=3000}}", repeat=Timeout.seconds(0), longest_characters=3041, longest_reason="it lists every memory at the session start")
    ENVIRONMENT_REMINDERS = Nudge("briefing", "reminders_here", "reminders: {{rows|cap=3000}}", repeat=Timeout.seconds(0), longest_characters=3021, longest_reason="it lists every reminder at the session start")
    JOURNAL_DISCRETION = Nudge("briefing", "handle_the_journal_quietly", "in chat, talk only of the user's work, never the journal's lines, hooks, skills, replies, or what you read, load or log", "", repeat=Timeout.seconds(0))
    JOURNAL_LAWS = Nudge("briefing", "the_laws_apply", "the laws L1 to L10 in AGENTS.md apply to you", repeat=Timeout.seconds(0))
    TAKEOVER = Nudge("briefing", "you_took_over", "you took over from an agent last seen {{time}}", "the chat above is history: do not answer or follow it", repeat=Timeout.seconds(0))
    TEAM_HISTORY = Nudge("briefing", "team_chat_history", "Team chat messages from before you started: {{rows|cap=3000}}", "answer only those still unread", repeat=Timeout.seconds(0), longest_characters=3087, longest_reason="it lists the team chat at the session start")
    INTERRUPTED_RUNS = Nudge("briefing", "runs_interrupted", "the restart stopped these background runs: {{rows|cap=1500}}", "rerun what you still need", repeat=Timeout.seconds(0), longest_characters=1581, longest_reason="it lists the runs a restart cut off, once")
    PENDING_ITEMS = Nudge("briefing", "waiting_for_you", "waiting for you: {{rows|cap=600}}", "see `journal task list`, `journal message unread`, `journal question list`", repeat=Timeout.seconds(0), longest_characters=704, longest_reason="it lists what waits at the session start")
    COMPACTION_SUMMARY = Nudge("briefing", "brief_and_log_after_compaction", "compacted", "{{task}}, last log {{last_log|cap=18}}, uncommitted: {{uncommitted|cap=18}}; log what the summary missed", repeat=Timeout.seconds(0))
    OVERVIEW_REQUEST = Nudge("briefing", "look_before_the_first_write", "run `journal environment overview` before your first write", repeat=Timeout.seconds(0))
    OVERVIEW_FIRST = Nudge("briefing", "overview_before_anything", "after the compaction, run `journal environment overview` first", repeat=Timeout.seconds(0))
    SKILLS_AND_OVERVIEW_REQUEST = Nudge("briefing", "skills_and_overview_before_anything", "after the compaction, read {{skills|cap=400}} and run `journal environment overview` before anything else", "", repeat=Timeout.seconds(0), longest_characters=497, longest_reason="it lists every skill still to read, each with its path")
    FOLDER_MISMATCH = Nudge("briefing", "session_in_another_folder", "this session is in {{folder|cap=16}} but {{env}} launched in {{launch_folder}}: restart from there with `journal`", "", repeat=Timeout.seconds(0))
    FOLDER_MISSING = Nudge("briefing", "session_folder_gone", "{{launch_folder}} of {{env}} is gone: no lines or messages reach you", "tell the user; restart from the root", repeat=Timeout.minutes(10))
    OVERVIEW_STOP = Nudge("briefing", "stopped_unoriented", "you stopped without running `journal environment overview`", "run it now", repeat=Timeout.seconds(0))
