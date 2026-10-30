# Teams

A team is a small server that holds accounts and the items a team shares: sequences, templates, profiles, readers,
skills, documents, files and plan outlines, each with its versions (see [the library](library.md)). Every journal stays
on its own machine and keeps its own tasks, messages, plans and environments; nothing of them goes to a team. A project
may be connected to several teams at once, each with its own people, devices, invitations and items.

The Team item in the sidebar opens the Team page. With no team connected it offers two things side by side: connect to
a server by its address, or set a new server up. With teams connected it lists them, shows the chosen one, and has an
Add a team button for one more.

## Setting a team server up

A team server is one Docker container. On a machine with Docker, run the command the Team page shows, which names this
journal's release:

    curl -fsSL https://github.com/jessegall/agent-journal/releases/download/v<release>/install.sh | sh

or, from your project, on a machine you reach over ssh with a key:

    journal remote install root@203.0.113.5

It installs Docker first when the machine has none, asks for the project's name and the address the team reaches the
server at, or reads them from TEAM_PROJECT and TEAM_ADDRESS, and listens on ports 8443 (HTTPS) and 8080 (HTTP) unless
TEAM_HTTPS_PORT and TEAM_HTTP_PORT say otherwise, so a web server already on 80 and 443 keeps them. On those ports the
server makes its own certificate, which a journal trusts on its first connect. A domain gets a public certificate only
when the server is given 443 and 80 (journal remote install --https-port 443 --http-port 80). Everything the server
keeps, its accounts, the items and their files, lives in one Docker volume. At the end it prints the server's URL.

The install prints the server's setup code once, with the line that claims it: `journal team connect "<url>/setup?code=<code>"` makes you its admin, and no journal can claim the server without the code. Read it again on the server while it has no admin with `docker exec <container> python -m sync_server setup-code --data /data/team`.

Back up a running server with `docker exec agent-journal-<project> python -m sync_server backup --data /data/team`; the
backup keeps the items' files beside the database.

## Connecting

On the Team page, give the server's address or an invitation URL, a name for the team in this journal, your email, your
name and a password; or run `journal team connect <URL> --email <you> --team <name>`. A new server's address makes you
its admin, an invitation URL makes you a member, and a server where you have an account logs you in. Left out, the
team's name is the server's host name. The same server twice, or a name another connected team has, is refused.

Each team keeps its own account file in the journal's `libraries` folder, with its own token and its own certificate
authority, so one team's token never reaches another team's server. The first team joined is the home team.

## People, devices and invitations

Everything about a team is read through that team's own account. On the Team page they show under the chosen team:
its people and their roles, and for an admin its devices and the invitation form. From the console,
`journal team people` lists the people, and an admin lists the devices with `journal team devices`, revokes one with
`journal team revoke`, invites a person with `journal team invite <email>` (who connects with the invitation URL it
prints), removes a person with `journal team remove` and gives a person a new password with `journal team reset`.
Anyone changes their own password with `journal team password`. A machine whose device was revoked logs in again with
`journal team login`.

## The --team option

Every `journal team` and `journal library` verb that reaches a team server takes `--team <name>`. With one team
connected it may be left out. With several, a command that names no team is refused with a line naming the teams and
the option, so no command picks a team on its own; an unknown name is refused naming it. `journal team status` lists
every connected team, or the one `--team` names.

## Disconnecting

Disconnect a team with its Disconnect button on the Team page, which asks first, or with
`journal team disconnect --team <name>`. Only that team's account file and certificate go; the other teams stay
connected, and what you imported from its library stays.
