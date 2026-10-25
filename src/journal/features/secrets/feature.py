from journal.features.feature import Feature
from journal.support.skill import Skill
from journal.features.secrets.commands.secret_command import SecretCommand
from journal.features.secrets.secrets_conduct import SecretsConduct
from journal.features.secrets.support.secrets_data_reader import SecretsDataReader
from journal.features.secrets.support.secrets_data import SecretsData
from journal.features.secrets.listeners.leak_alarm import LeakAlarm
from journal.features.secrets.listeners.expiry_question import ExpiryQuestion
from journal.features.secrets.listeners.secret_purge import SecretPurge
from journal.features.secrets.seeds.secret_files import SecretFiles
from journal.features.secrets.secrets_nudges import SecretsNudges
from journal.features.secrets.secrets_part import SecretsPart


class Secrets(Feature[SecretsData]):
    name = SecretsPart.name
    title = "Secrets"
    help = "A key or a login the agent may use without seeing it: its values live in a file in your home folder, never in the journal, and you fill them in on the Secrets page."
    nudges = (SecretsNudges.PRIVATE_SECRETS, SecretsNudges.SECRET_PROGRAM_GRANT)
    commands = (SecretCommand,)
    seeds = (SecretFiles,)
    skill = Skill("secrets", 'Keys and logins the agent uses without seeing them; load it when a task needs a key, a login or a site you must be logged in to', """
# Secrets

A secret is a key or a login you may use without ever seeing it. Its values are stored in a file in the user's home folder,
outside the project, and never in the journal; the journal masks a value anywhere it would be written.

- A task needs a key you do not have: `journal secret request "<name>" --why "<what for>"`, with `--kind login` for a
  username and password. The user fills it on the Secrets page; never ask for a value in the chat.
- `journal secret create "<title>" [--kind <kind>] [--brief "<how it is used>"]` makes an empty one;
  `journal secret update <n> [--title "<title>"] [--brief "<how it is used>"]` changes it.
- `journal secret list` names the secrets and what each is waiting for; `journal secret show <n>` shows its fields, which are
  filled in and the programs it may go to.
- Use one with `journal secret run <n or name> -- <program> <args>`: the program receives the hidden value on its input,
  `--stdin "Authorization: Bearer {key}"` sends that text with the fields filled in, and `--env` provides the fields in their
  variables too. It runs in the journal's own process with a home of its own and nothing of your shell, and what it prints
  comes back with every form of the value masked.
- A secret goes only to the programs the user allowed, named bare, never to a shell, an interpreter, a build tool or a
  program that echoes what it is given. Propose one with `journal secret propose <n> <program>`; you are informed when the user
  allows it. A worker gets a secret only when the user allows helpers to have it.
- A site you use in a browser: `journal secret request "<site>" --kind "browser login" --url <address> --why "<what for>"`.
  The user logs in with the Log in button on the Secrets page, in a browser on their computer, and your browser starts
  logged in from its next start. Where the user lets you log in on your own, `journal secret login <n>` opens it, and
  `journal secret login <n> --wait` waits until it is done.
- The secrets folder and the MCP keys are out of your reach: a tool that names them is refused.
- Masking cannot catch a value inside another encoding, such as Basic auth, nor a file the program writes, nor its
  variables while it runs.
- A value you made yourself, such as a generated password, goes in with `journal secret store <n> <field> <file>`,
  which deletes the file.
- `journal secret folder` names the file the values are stored in; `journal secret delete <n>` removes one.
- A deleted secret keeps its values for thirty days for `journal secret restore <n>`, then they are removed.
""", keywords=("secret", "secrets", "api key", "token", "password", "login"), commands=('secret',))
    listeners = (LeakAlarm, ExpiryQuestion, SecretPurge)
    data = (SecretsDataReader,)
    conduct = (SecretsConduct,)
