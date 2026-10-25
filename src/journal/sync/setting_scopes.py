from journal.features.registry import Registry
from journal.models.model import Model
from journal.models.setting import Setting
from journal.support.option_scope import OptionScope


class SettingScopes:
    """Which rows a shared journal shares with the team: a model that is shared, but for a row it withholds, such as a local copy of a hub document, and a setting only by its option's scope, team unless it says otherwise; a setting of one machine or one person stays on the machine that holds it."""

    def __init__(self, registry: Registry) -> None:
        self.registry = registry

    def is_team(self, key: str) -> bool:
        return all(option.scope == OptionScope.TEAM for option in self.registry.options() if option.key == key)

    def is_team_row(self, model: Model) -> bool:
        return model.shared and not model.is_withheld() and (not isinstance(model, Setting) or self.is_team(model.key))
