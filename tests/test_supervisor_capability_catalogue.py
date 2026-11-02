from journal.console.console import Console
from journal.features.supervisor.capability_catalogue import CAPABILITY_CATALOGUE, CAPABILITY_TIERS
from journal.support.agent_role import AgentRole


def coverage_gaps(commands, catalogue):
    entries = {
        (noun, verb)
        for area_name, area in catalogue.items()
        if area_name != "Its own grant"
        for noun, verbs in area.items()
        for verb in verbs
    }
    return sorted(commands - entries), sorted(entries - commands)


def named(pairs):
    return ", ".join(f"{noun} {verb}" for noun, verb in pairs)


def test_every_command_has_a_capability_entry_and_every_entry_names_a_command(app):
    console = app.container.get(Console)
    commands = {
        (noun, verb)
        for role in AgentRole
        for noun, command in console.table(role).items()
        for verb in console.verbs(command)
    }
    missing, stale = coverage_gaps(commands, CAPABILITY_CATALOGUE)
    assert not missing and not stale, (
        f"commands with no capability entry: {named(missing)}; "
        f"catalogue verbs with no command: {named(stale)}"
    )


def test_a_planted_command_without_a_tier_is_reported_by_noun_and_verb():
    missing, stale = coverage_gaps({("planted", "run")}, {"Checks": {"check": {"run": "tier 1"}}})
    assert missing == [("planted", "run")]
    assert stale == [("check", "run")]


def test_catalogue_entries_use_one_of_its_tiers():
    tiers = {
        tier
        for area in CAPABILITY_CATALOGUE.values()
        for verbs in area.values()
        for tier in verbs.values()
    }
    assert tiers <= CAPABILITY_TIERS


def test_memory_writes_and_grant_edits_are_never_allowed():
    memory = CAPABILITY_CATALOGUE["Rules and reminders"]["memory"]
    grant = CAPABILITY_CATALOGUE["Its own grant"]["grant"]
    assert memory["list"] == "read"
    assert "never" in memory.values()
    assert all(tier == "never" for tier in memory.values() if tier != "read")
    assert all(tier == "never" for tier in grant.values())
