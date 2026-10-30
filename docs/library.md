# The library

A team shares its working parts through its library: its server holds the sequences, templates, profiles, readers,
skills, documents, files and plan outlines its people publish, each with its versions. A person publishes an item when
it is ready to share, and the others import it into their own journal and update it when a newer version comes out.
How a team server is set up and connected, and how a project connects to several teams, is in
[teams](shared-journal.md). With several teams connected, every `journal library` verb names the team it acts on with
`--team`, and the Team page shows each team's items under that team.

## Publishing

Publish from the item's own panel in the viewer, which shows while one team is connected, or with
`journal library publish`: a sequence or a template by its number, a profile, a reader or a skill by its name, a document or a plain file
by its path, or a plan as its outline, its title, phases and task titles only. Each publish is the next version of the
item, with a note saying what changed. A reader is a script that runs on your commands' output, so whoever imports one
is shown its script first and confirms it. `journal library withdraw` takes an item off the list, whose versions stay
readable to whoever imported them, and an admin deletes one version for good with `journal library delete`, as one
published with a secret in it.

## Importing and updating

The Team page lists the chosen team's items by kind, with a search, the newest version of each and the version you
imported. Open one to read its versions and import it, or run `journal library import`. A newer version is taken with
Update, or `journal library update`; a copy you have edited here is not written over unless you replace it on purpose
with `--replace`. A plan outline is imported once, as a draft plan, and never updated.