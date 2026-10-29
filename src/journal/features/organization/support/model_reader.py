from journal.features.organization.support.role_models import RoleModels
from journal.features.organization.support.toml_fields import TomlFields
from journal.providers.providers import Providers

WRITER_CODEX = ("gpt-6-luna", "max")
JUDGE_CODEX = ("gpt-6.1-sol", "xhigh")


class ModelReader:
    """Reads a contract's [model] table: the Claude model must be one the provider ranks, and Codex is luna on max for what writes and sol on xhigh for everything else, nothing between."""

    def __init__(self, providers: Providers) -> None:
        self.providers = providers

    def read(self, fields: TomlFields, writes: bool) -> RoleModels:
        table = fields.table("model")
        codex = table.table("codex")
        claude, model, effort = table.text("claude"), codex.text("model"), codex.text("effort")
        table.unknown(("claude", "codex"))
        codex.unknown(("model", "effort"))
        fields.absorbed(table)
        fields.absorbed(codex)
        self.check(fields, claude, (model, effort), writes)
        return RoleModels(claude, model, effort)

    def check(self, fields: TomlFields, claude: str, codex: tuple[str, str], writes: bool) -> None:
        if claude and claude not in self.providers.lookup("claude").model_ranking:
            fields.problem("model", f"model.claude is {claude}; use one of {', '.join(self.providers.lookup('claude').model_ranking)}")
        wanted = WRITER_CODEX if writes else JUDGE_CODEX
        if all(codex) and codex != wanted:
            fields.problem("model", f"model.codex is {codex[0]} on {codex[1]}; a Role that {'writes' if writes else 'does not write'} uses {wanted[0]} on {wanted[1]}")
