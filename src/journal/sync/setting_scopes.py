from journal.features.registry import Registry
from journal.models.model import Model
from journal.models.setting import Setting
from journal.support.option_scope import OptionScope


class SettingScopes:
    """Which settings a shared journal shares with the team, by key: every option's scope, team unless it says otherwise; a setting of one machine or one person stays on the machine that holds it."""

    def __init__(self, registry: Registry) -> None:
        self.registry = registry

    def is_team(self, key: str) -> bool:
        return all(option.scope == OptionScope.TEAM for option in self.registry.options() if option.key == key)

    def is_team_row(self, model: Model) -> bool:
        return model.shared and (not isinstance(model, Setting) or self.is_team(model.key))
