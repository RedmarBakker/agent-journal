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
# a script handed to a runner by its path, which a run is known by: python3 /tmp/scan.py is python3 scan.py
# the package managers whose flags may stand before their subcommand: pnpm -r build, yarn --silent test
PACKAGE_MANAGERS = {"npm", "pnpm", "yarn", "bun"}
SCRIPT_FILE = re.compile(r"\.(py|js|mjs|cjs|ts|sh|bash|zsh|rb|pl)$")
SHAPE_TOKEN_COUNT = 3
WRAPPER_PATTERN = re.compile(r"^\s*(?:perl -e '[^']*exec @ARGV[^']*'|timeout \d+[smh]?|lockf(?:\s+-[a-z](?:\s+\d+)?)*\s+\S+|flock(?:\s+-\S+)*\s+\S+|env(?:\s+(?:-u\s+\S+|-i|[A-Za-z_]\w*=\S*))+|nice(?:\s+-n\s*-?\d+)?)\s+")
# a loop that only waits for something, its body a sleep alone, which a run is known by as a wait: until ping -c1 h; do sleep 1; done
POLL_PATTERN = re.compile(r"^\s*(?:while|until)\b.*\bdo\s+sleep\s+[\d.]+[smh]?\s*;?\s*done\b", re.S)
# the shell's own words and tests a waiting loop may hold beside its sleep, which do no work of their own
IDLE_WORDS = {"while", "until", "true", ":", "do", "if", "then", "else", "fi", "break", "continue", "done", "[", "[[", "test", "echo", "date", "sleep"}
# a group run as one, timed or not, which a run is known by the commands inside: time { make; } is make
GROUP_PATTERN = re.compile(r"^\s*(?:time\s+)?[({]")
# the shell's own words around the commands of a loop or a branch, which a run is never known by: while, do and done,
# a for or case header, and a value captured from a command, x=$(git log ...), which is that command
CONTROL_PATTERN = re.compile(r"^\s*(?:(?:while|until|if|elif|then|else|do|!)\s+)+")
HEADER_PATTERN = re.compile(r"^\s*(?:(?:done|fi|esac|;;)\b.*|(?:for|select|case)\s.*)$")
LOOP_PATTERN = re.compile(r"^\s*(?:while|until|for|if|case|select)\s")
CAPTURE_PATTERN = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_]*=\$\((.*)\)\s*$")
CONTAINER_PATTERN = re.compile(r"^\s*docker(?:\s+compose|-compose)?\s+exec\s+(?:(?:-[euw]|--(?:env|env-file|user|workdir))[ =]\S+\s+|-{1,2}[\w-]+\s+)*\S+\s+")
# git's own options before its subcommand, which a run is never known by: git -C repo push is git push
GIT_OPTION_PATTERN = re.compile(r"^(\s*git)(?:\s+(?:-C|-c|--git-dir|--work-tree)\s+\S+|\s+--no-pager)+(?=\s)")
VARIABLE_PATTERN = re.compile(r"^\s*(?:[A-Za-z_][A-Za-z0-9_]*=(?:'[^']*'|\"[^\"]*\"|\S*)(?:\s+|$))+")
# commands that only set the scene for the one that does the work: a line's shape is the first part past them
SETUP_COMMANDS = {"cd", "export", "unset", "set", "source", ".", "pushd", "popd", "true", "mkdir", "read", "rm"}
SEPARATORS = ("&&", "||", ";", "|")
CHAIN_SEPARATOR = re.compile(r"&&|\|\||;|\|")
SETUP_PREFIX = re.compile(r"^(?:(?:cd|export|unset|set|source|\.|pushd|popd|true)(?:\s[^&;|]*)?\s*(?:&&|;)\s*)+")


class CommandShape:
    """A command as its program and subcommands name it, with the values passed to it removed: pytest -k chat and pytest tests/a.py are both pytest, python3 -m pytest -q is python3 -m pytest, npm run test stays npm run test; a wrapper that only limits its time, perl -e 'alarm N; exec @ARGV' or timeout N, variables set before the command, such as REPLAY_FREEZE=1, and a run inside a container, docker compose exec or docker exec with its flags and its service, are seen through. A line's shape is that of its first part that does the work, after a cd, a variable assignment or an export."""

    @staticmethod
    def unwrapped(part: str) -> str:
        text = re.sub(r"^time\s+", "", part.strip())
        if text.startswith("("):
            return text.removeprefix("(").removesuffix(")").strip()
        return text.removeprefix("{").strip().removesuffix("}").strip().removesuffix(";").strip() if text.startswith("{") else text

    @classmethod
    def working(cls, part: str) -> str:
        if not GROUP_PATTERN.match(part) or part.strip().startswith("(("):
            return part
        commands = [bare for command in CHAIN_SEPARATOR.split(cls.unwrapped(part)) if (bare := cls.unbracketed(command))]
        return next((command for command in commands if command.split()[0] not in SETUP_COMMANDS), commands[0] if commands else part)

    @classmethod
    def shown(cls, part: str) -> str:
        return cls.inner(SETUP_PREFIX.sub("", cls.unwrapped(part))).strip()

    @staticmethod
    def inner(part: str) -> str:
        unlooped = CONTROL_PATTERN.sub("", part, count=1)
        if HEADER_PATTERN.match(unlooped):
            return ""
        captured = CAPTURE_PATTERN.match(unlooped)
        command = CommandShape.past_setup(captured.group(1)) if captured else unlooped
        return GIT_OPTION_PATTERN.sub(r"\1", CONTAINER_PATTERN.sub("", CommandShape.unwrapped_all(VARIABLE_PATTERN.sub("", command, count=1)), count=1), count=1)

    # every wrapper in front taken off, as env -u X lockf -k file pytest is pytest
    @staticmethod
    def unwrapped_all(command: str) -> str:
        bare = WRAPPER_PATTERN.sub("", command, count=1)
        return bare if bare == command else CommandShape.unwrapped_all(bare)

    @staticmethod
    def past_setup(chain: str) -> str:
        commands = [command.strip() for command in CHAIN_SEPARATOR.split(chain) if command.strip()]
        return next((command for command in commands if command.split()[0] not in SETUP_COMMANDS), commands[0] if commands else chain)

    @classmethod
    def chain_shape(cls, parts: tuple[str, ...]) -> str:
        shapes = [shape for shape in (cls.build(part) for part in parts) if shape]
        return next((shape for shape in shapes if shape.split()[0] not in SETUP_COMMANDS), shapes[0] if shapes else "")

    @classmethod
    def command_name(cls, part: str) -> str:
        if LOOP_PATTERN.match(part):
            looped = CONTROL_PATTERN.sub("", cls.looped(part), count=1)
            return cls.command_name(looped) if looped and not LOOP_PATTERN.match(looped) else ""
        if part.strip().startswith("(("):
            return ""
        if GROUP_PATTERN.match(part):
            commands = [command.strip("(){}; ") for command in cls.commands(cls.unwrapped(part)) if command.strip("(){}; ")]
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
    def looped(cls, part: str) -> str:
        commands = [cls.unbracketed(CONTROL_PATTERN.sub("", command, count=1)) for command in cls.commands(part)]
        return next((command for command in commands if (shape := cls.plain_shape(command)) and shape.split()[0] not in SETUP_COMMANDS), "")

    # a loop whose every command is a sleep or the shell's own words and tests, so all it does is wait
    @classmethod
    def is_waiting_loop(cls, part: str) -> bool:
        if not LOOP_PATTERN.match(part) or part.strip().startswith(("for", "case", "select")):
            return False
        programs = {words[1] if words[0] in {"do", "then", "else"} and len(words) > 1 else words[0] for command in cls.commands(part) if (words := command.split())}
        return "sleep" in programs and programs <= IDLE_WORDS

    @staticmethod
    def unbracketed(command: str) -> str:
        bare = command.strip().lstrip("(").strip()
        while bare.endswith(")") and bare.count(")") > bare.count("("):
            bare = bare[:-1].strip()
        return bare

    @classmethod
    def build(cls, part: str) -> str:
        if POLL_PATTERN.match(part) or cls.is_waiting_loop(part):
            return "sleep"
        if LOOP_PATTERN.match(part):
            return cls.plain_shape(cls.looped(part))
        return cls.plain_shape(cls.working(part))

    @classmethod
    def plain_shape(cls, part: str) -> str:
        tokens = TOKEN_PATTERN.findall(cls.inner(part).split("<<", 1)[0])
        if not tokens:
            return ""
        if len(tokens) > 1 and tokens[0].rsplit("/", 1)[-1] in RUNNERS and SCRIPT_FILE.search(tokens[1]):
            return f"{tokens[0]} {tokens[1].rsplit('/', 1)[-1]}"
        shape_parts = [tokens[0]]
        for token in tokens[1:SHAPE_TOKEN_COUNT]:
            is_module = token == MODULE_FLAG and shape_parts[-1].rsplit("/", 1)[-1] in RUNNERS
            # a package manager's flag before its subcommand is passed over, as pnpm -r build is pnpm build
            if token.startswith("-") and "=" not in token and len(shape_parts) == 1 and shape_parts[0].rsplit("/", 1)[-1] in PACKAGE_MANAGERS:
                continue
            if not is_module and not WORD_PATTERN.fullmatch(token):
                break
            shape_parts.append(token)
        return " ".join(shape_parts)
