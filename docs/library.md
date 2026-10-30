# The library

A team shares its working parts through a library: one small server holds the sequences, templates, profiles, readers,
skills, documents, files and plan outlines its people publish, each with its versions. Every journal stays on its own
machine and keeps its own tasks, messages, plans and environments; nothing of them goes to the server. A person
publishes an item when it is ready to share, and the others import it into their own journal and update it when a newer
version comes out.

## Hosting the library server

The library server is one Docker container. On a machine with Docker, run:

    curl -fsSL https://github.com/jessegall/agent-journal/releases/latest/download/install.sh | sh

or, from your project, on a machine you reach over ssh with a key:

    journal remote install root@203.0.113.5

It asks for the project's name and the address the team reaches the server at, and listens on ports 8443 (HTTPS) and
8080 (HTTP), so a web server already on 80 and 443 keeps them. On those ports the server makes its own certificate, which
a journal trusts on its first connect. A domain gets a public certificate only when the server is given 443 and 80
(TEAM_HTTPS_PORT, TEAM_HTTP_PORT, or journal remote install --https-port 443 --http-port 80). Everything the server
keeps, its accounts, the items and their files, lives in one Docker volume. At the end it prints the server's URL.

Connect to that URL first, before anyone else: the first journal to connect to a new server becomes its admin. Give
the URL, your email, your name and a password in Settings, Library, or run `journal library connect <URL>`.

Back up a running server with `docker exec agent-journal-<project> python -m sync_server backup --data /data/team`; the
backup keeps the items' files beside the database.

## Connecting

An admin invites a person with Settings, Library, Invite, or `journal library invite <email>`, and sends them the
invitation URL. Paste it in Settings, Library, with your email, name and a password, or run
`journal library connect <invitation URL>`. A machine whose device was revoked logs in again with
`journal library login`. `journal library status` says which library this journal is connected to, as whom and in which
role, and `journal library disconnect` lets it go; what you imported stays.

## Publishing

Publish from the item's own panel in the viewer, or with `journal library publish`: a sequence or a template by its
number, a profile, a reader or a skill by its name, a document or a plain file by its path, or a plan as its outline,
its title, phases and task titles only. Each publish is the next version of the item, with a note saying what changed.
A reader is a script that runs on your commands' output, so whoever imports one is shown its script first and confirms
it. `journal library withdraw` takes an item off the list, whose versions stay readable to whoever imported them, and an
admin deletes one version for good with `journal library delete`, as one published with a secret in it.

## Importing and updating

The Library page lists the items by kind, with a search, the newest version of each and the version you imported. Open
one to read its versions and import it, or run `journal library import`. A newer version is taken with Update, or
`journal library update`; a copy you have edited here is not written over unless you replace it on purpose with
`--replace`. A plan outline is imported once, as a draft plan, and never updated.

## People

`journal library people` lists the library's people and their roles. An admin lists the devices with
`journal library devices`, revokes one with `journal library revoke`, removes a person with `journal library remove`
and gives a person a new password with `journal library reset`. Anyone changes their own password with
`journal library password`.
