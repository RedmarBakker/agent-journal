from journal.support.card_family import CardFamily
from journal.support.card_type_entry import CardTypeEntry
from journal.support.mark_kinds import WORK
from journal.support.card_type import CardType
from journal.features.feature import Feature
from journal.features.git.listeners.commit_detection import CommitDetection
from journal.features.git.listeners.commit_card import CommitCard
from journal.features.git.listeners.push_card import PushCard
from journal.features.git.listeners.branch_change_card import BranchChangeCard
from journal.features.git.listeners.renamed_worktree_folders import RenamedWorktreeFolders
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
    card_families = (CardFamily("git", "Git", "branch", WORK),)
    card_kinds = (CardTypeEntry(CardType.COMMITS, "Commits", "git"), CardTypeEntry(CardType.WORKTREES, "Worktrees", "git"), CardTypeEntry(CardType.PUSHES, "Pushes", "git"), CardTypeEntry(CardType.BRANCH_SWITCHES, "Branch switches", "git"),)
    title = "Git"
    help = "Every commit the agent makes is a badge in the chat."
    listeners = (CommitDetection, CommitCard, PushCard, BranchChangeCard, WorktreeSessionLink, WorktreeTipRecord, RenamedWorktreeFolders)
    data = (GitDataReader, BranchEnvironmentsReader)
    conduct = (GitConduct,)
    commands = (WorktreeCommand,)
    seeds = (OldMainWorktree, WorktreeTidying)

    nudges = (GitNudges.WORKER_TASK_REFUSAL, GitNudges.BRANCH_CONFLICT)
