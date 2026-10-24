from journal.features.updates.support.release_source import REPOSITORY
from journal.support.option import USER, Option
from journal.support.option_scope import OptionScope


class UpdatesOptions:
    REPOSITORY = Option("updates.repository", "Install from this repository", "The git address the journal installs itself from", REPOSITORY, kind="text", scope=OptionScope.MACHINE, setter=USER)
    BRANCH = Option("updates.branch", "Follow this branch", "Empty follows the releases of this major version; a branch name installs that branch's newest commit instead, with Install update, journal update and the check for a new release", "", kind="text", scope=OptionScope.MACHINE, setter=USER)
    AUTO = Option("updates.auto", "Install new releases on its own", "When a newer release of this major version is out, or a newer commit of the followed branch, install it and restart the journal; a new major version is never installed on its own; once a new version runs, every plugin installed from a release moves to its newest release that runs on it", False, kind="switch", scope=OptionScope.MACHINE, setter=USER)
    CHECK_INTERVAL = Option("updates.check_minutes", "Check for a new release every", "Minutes between two looks at GitHub for a newer release or a newer commit of the followed branch", 60, unit="minutes", scope=OptionScope.MACHINE)
