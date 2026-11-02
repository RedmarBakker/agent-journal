from journal.console.console import Console
from journal.features.supervisor.capability_catalogue import CAPABILITY_CATALOGUE, CAPABILITY_TIERS


def test_every_command_has_a_capability_entry(app):
    console = app.container.get(Console)
    commands = {
        (noun, verb)
        for noun, command in console.commands.items()
        for verb in console.verbs(command)
    }
    catalogue = {
        (noun, verb)
        for area in CAPABILITY_CATALOGUE.values()
        for noun, verbs in area.items()
        for verb in verbs
    }
    missing = sorted(commands - catalogue)
    assert not missing, f"commands with no capability entry: {', '.join(f'{noun} {verb}' for noun, verb in missing)}"


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
