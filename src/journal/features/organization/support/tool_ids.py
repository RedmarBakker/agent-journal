from journal.features.organization.support.role_tools import ROLE_TOOLS


class ToolIds:
    """The tool ids a Role's contract may list, and the words of the provider's own tools each becomes; an id that is not one of these is an external system the organization names, which brings no tool word."""

    def is_known(self, tool: str) -> bool:
        return tool in ROLE_TOOLS

    def is_well_formed(self, tool: str) -> bool:
        return tool.replace("_", "").isalnum() and tool == tool.lower() and not tool[0].isdigit()

    def words(self, tools: tuple[str, ...]) -> str:
        return ", ".join(dict.fromkeys(word for tool in tools for word in ROLE_TOOLS.get(tool, ())))
