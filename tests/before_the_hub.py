def before_the_hub(team) -> None:
    """Makes a new team server one from before the hub, whose journals send the team every shared row as they always have."""
    team.store.execute("DELETE FROM team_details WHERE name = 'hub'")
