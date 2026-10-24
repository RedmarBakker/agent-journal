from journal.features.feature import Feature
from journal.features.git.listeners.commit_detection import CommitDetection
from journal.features.git.listeners.worktree_session_link import WorktreeSessionLink
from journal.features.git.listeners.worktree_tip_record import WorktreeTipRecord
from journal.features.git.git_conduct import GitConduct
from journal.features.git.support.git_data_reader import GitDataReader
from journal.features.git.support.git_data import GitData
from journal.features.git.support.branch_environments_reader import BranchEnvironmentsReader
from journal.features.git.git_nudges import GitNudges
from journal.features.git.commands.worktree_command import WorktreeCommand
from journal.features.git.seeds.old_main_worktree import OldMainWorktree
from journal.features.git.seeds.worktree_tidying import WorktreeTidying


class Git(Feature[GitData]):
    """What the agent does in git, as the chat shows it: every commit is a badge, and a session in a worktree is marked with its branch."""

    name = "git"
    title = "Git"
    help = "Every commit the agent makes is a badge in the chat."
    listeners = (CommitDetection, WorktreeSessionLink, WorktreeTipRecord)
    data = (GitDataReader, BranchEnvironmentsReader)
    conduct = (GitConduct,)
    commands = (WorktreeCommand,)
    seeds = (OldMainWorktree, WorktreeTidying)

    nudges = (GitNudges.WORKER_TASK_REFUSAL, GitNudges.BRANCH_CONFLICT)
