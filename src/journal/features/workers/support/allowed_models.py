from journal.features.workers.workers_options import WorkersOptions
from journal.providers.providers import Providers
from journal.repositories.setting_rows import SettingRows

FALLBACK_ROLE = "journal-medior"


class AllowedModels:
    """The models each role may run on for each provider, from the user's setting, one line each; a model asked for outside them is moved to the nearest allowed, the stronger when two are as near, and a role with no line of its own takes the line of journal-medior."""

    def __init__(self, settings: SettingRows, providers: Providers) -> None:
        self.settings, self.providers = settings, providers

    def lines(self) -> dict[tuple[str, str], tuple[str, ...]]:
        parsed = {}
        for line in self.settings.texts(WorkersOptions.ALLOWED_MODELS):
            head, _, models = line.partition(":")
            names = head.split()
            if len(names) == 2:
                parsed[(names[0], names[1])] = tuple(model.strip() for model in models.split(",") if model.strip())
        return parsed

    def allowed(self, provider: str, role: str) -> tuple[str, ...]:
        lines = self.lines()
        return lines.get((provider, role)) or lines.get((provider, FALLBACK_ROLE)) or self.providers.lookup(provider).model_ranking

    def strongest(self, provider: str, role: str) -> str:
        ranking = self.providers.lookup(provider).model_ranking
        return max(self.allowed(provider, role), key=lambda model: ranking.index(model) if model in ranking else -1)

    def clamped(self, provider: str, role: str, model: str) -> tuple[str, str]:
        ranking, allowed = self.providers.lookup(provider).model_ranking, self.allowed(provider, role)
        requested = next((word for word in ranking if word in model.lower()), "")
        if not requested or requested in allowed:
            return model, ""
        nearest = min((word for word in allowed if word in ranking), key=lambda word: (abs(ranking.index(word) - ranking.index(requested)), -ranking.index(word)), default=requested)
        moved = model.lower().replace(requested, nearest)
        return moved, f"{model} is not allowed for {role} on {provider}, which may run on {', '.join(allowed)}: moved to {moved}"
