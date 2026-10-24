import re

RUNNERS = {"python", "python3", "node", "bash", "sh", "zsh", "env", "time", "nohup"}
# programs that only start the one that does the work, which a run is known by: npx vitest is vitest, uv run pytest is pytest
LAUNCHERS = RUNNERS | {"npx", "pnpx", "bunx", "exec", "nice", "caffeinate"}
# a redirection of a command's input or output, which is no part of the command a run is known by
REDIRECT_PATTERN = re.compile(r"\s\d*(?:>>?|<)&?\s*\S+")
# a shell handed its script with -c, which a run is known by: bash -c "make test" is make test
SCRIPT_PATTERN = re.compile(r"^\s*\S*\b(?:ba|z)?sh\s+-c\s+['\"]?(.*?)['\"]?\s*$")
LAUNCHER_SUBCOMMANDS = {"uv": "run", "poetry": "run", "pipenv": "run", "bundle": "exec"}
TOKEN_PATTERN = re.compile(r"[^\s|<>&;]+")
WORD_PATTERN = re.compile(r"[A-Za-z][\w.-]*")
MODULE_FLAG = "-m"
SHAPE_TOKEN_COUNT = 3
WRAPPER_PATTERN = re.compile(r"^\s*(?:perl -e '[^']*exec @ARGV[^']*'|timeout \d+[smh]?)\s+")
CONTAINER_PATTERN = re.compile(r"^\s*docker(?:\s+compose|-compose)?\s+exec\s+(?:(?:-[euw]|--(?:env|env-file|user|workdir))[ =]\S+\s+|-{1,2}[\w-]+\s+)*\S+\s+")
VARIABLE_PATTERN = re.compile(r"^\s*(?:[A-Za-z_][A-Za-z0-9_]*=(?:'[^']*'|\"[^\"]*\"|\S*)(?:\s+|$))+")
# commands that only set the scene for the one that does the work: a line's shape is the first part past them
SETUP_COMMANDS = {"cd", "export", "unset", "set", "source", ".", "pushd", "popd", "true"}
SEPARATORS = ("&&", "||", ";", "|")
CHAIN_SEPARATOR = re.compile(r"&&|\|\||;|\|")
SETUP_PREFIX = re.compile(r"^(?:(?:cd|export|unset|set|source|\.|pushd|popd|true)(?:\s[^&;|]*)?\s*(?:&&|;)\s*)+")


class CommandShape:
    """A command as its program and subcommands name it, with the values passed to it removed: pytest -k chat and pytest tests/a.py are both pytest, python3 -m pytest -q is python3 -m pytest, npm run test stays npm run test; a wrapper that only limits its time, perl -e 'alarm N; exec @ARGV' or timeout N, variables set before the command, such as REPLAY_FREEZE=1, and a run inside a container, docker compose exec or docker exec with its flags and its service, are seen through. A line's shape is that of its first part that does the work, after a cd, a variable assignment or an export."""

    @staticmethod
    def unwrapped(part: str) -> str:
        text = part.strip()
        return text.removeprefix("(").removesuffix(")").strip() if text.startswith("(") else text

    @classmethod
    def working(cls, part: str) -> str:
        if not part.strip().startswith("("):
            return part
        commands = [command.strip() for command in CHAIN_SEPARATOR.split(cls.unwrapped(part)) if command.strip()]
        return next((command for command in commands if command.split()[0] not in SETUP_COMMANDS), commands[0] if commands else part)

    @classmethod
    def shown(cls, part: str) -> str:
        return cls.inner(SETUP_PREFIX.sub("", cls.unwrapped(part))).strip()

    @staticmethod
    def inner(part: str) -> str:
        return CONTAINER_PATTERN.sub("", WRAPPER_PATTERN.sub("", VARIABLE_PATTERN.sub("", part, count=1), count=1), count=1)

    @classmethod
    def chain_shape(cls, parts: tuple[str, ...]) -> str:
        shapes = [shape for shape in (cls.build(part) for part in parts) if shape]
        return next((shape for shape in shapes if shape.split()[0] not in SETUP_COMMANDS), shapes[0] if shapes else "")

    @classmethod
    def command_name(cls, part: str) -> str:
        if part.strip().startswith("(("):
            return ""
        if part.strip().startswith("("):
            commands = [command.strip("() ") for command in cls.commands(part) if command.strip("() ")]
            return cls.command_name(next((command for command in commands if command.split()[0] not in SETUP_COMMANDS), commands[0] if commands else ""))
        text = REDIRECT_PATTERN.sub("", cls.inner(SETUP_PREFIX.sub("", part.strip())).split("<<", 1)[0])
        script = SCRIPT_PATTERN.match(text)
        if script:
            return cls.command_name(script.group(1))
        tokens = TOKEN_PATTERN.findall(text)
        start = cls.program_index(tokens)
        if start >= len(tokens) or "=" in tokens[start].split("/", 1)[0]:
            return ""
        if tokens[start].startswith("("):
            return cls.command_name(text[text.find(tokens[start]):])
        return cls.build(" ".join([tokens[start].rsplit("/", 1)[-1], *tokens[start + 1:]]))

    @staticmethod
    def commands(text: str) -> list[str]:
        commands, command_text, open_quote, index = [], "", "", 0
        while index < len(text):
            character = text[index]
            separator = "" if open_quote else next((symbol for symbol in SEPARATORS if text.startswith(symbol, index)), "")
            if separator:
                commands, command_text, index = [*commands, command_text], "", index + len(separator)
                continue
            open_quote = CommandShape.quote_state(open_quote, character)
            command_text, index = command_text + character, index + 1
        return [command.strip() for command in [*commands, command_text] if command.strip()]

    @staticmethod
    def quote_state(open_quote: str, character: str) -> str:
        if character == open_quote:
            return ""
        return character if not open_quote and character in "'\"" else open_quote

    @staticmethod
    def program_index(tokens: list[str]) -> int:
        index = 0
        while index < len(tokens):
            name = tokens[index].rsplit("/", 1)[-1]
            if name in LAUNCHERS and index + 1 < len(tokens):
                index += 2 if tokens[index + 1] == MODULE_FLAG else 1
            elif LAUNCHER_SUBCOMMANDS.get(name) == (tokens[index + 1] if index + 1 < len(tokens) else ""):
                index += 2
            elif index > 0 and (tokens[index].startswith("-") or VARIABLE_PATTERN.match(tokens[index] + " ")):
                index += 1
            else:
                return index
        return index

    @classmethod
    def build(cls, part: str) -> str:
        tokens = TOKEN_PATTERN.findall(cls.inner(part).split("<<", 1)[0])
        if not tokens:
            return ""
        shape_parts = [tokens[0]]
        for token in tokens[1:SHAPE_TOKEN_COUNT]:
            is_module = token == MODULE_FLAG and shape_parts[-1].rsplit("/", 1)[-1] in RUNNERS
            if not is_module and not WORD_PATTERN.fullmatch(token):
                break
            shape_parts.append(token)
        return " ".join(shape_parts)
