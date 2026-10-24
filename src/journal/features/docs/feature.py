from journal.features.docs.commands.doc_command import DocCommand
from journal.features.docs.listeners.doc_revision_record import DocRevisionRecord
from journal.features.docs.listeners.document_card import DocumentCard
from journal.features.feature import Feature
from journal.support.skill import Skill
from journal.features.docs.docs_options import DocsOptions


class DocsFeature(Feature):
    name = "docs"
    title = "Documents"
    help = "What the project keeps knowing: documents shared by every environment, listed on the Documents page."
    commands = (DocCommand,)
    listeners = (DocumentCard, DocRevisionRecord)
    options = (DocsOptions.REVISION_WINDOW,)

    skill = Skill("docs", 'Store lasting knowledge of the project in a document; load it when something should still be known next month', """
# Documents

A document holds what the project must keep knowing; the result of a check goes in a report, ordered work in a plan.
Documents are the project's, the same in every environment.

- `journal doc create "<title>" --file <path> --abstract "<one line>"` writes one from a markdown file, its `##` headings
  as sections. `journal doc update <n> --file <path>` replaces its whole text and keeps its title.
- `journal doc show <n>` prints its outline, numbered headings with their length; read one section with
  `--section <n or heading>` (`--bullets` for its bullets alone), or find lines with `--grep "<words>"`. Read it whole with
  `--all` only when every section matters to the job; the outline and one section are the default. `journal doc list` names them.
- Every save that changes a document's text is stored as a revision. Saves within 30 minutes of the last merge into the
  open revision, each change noted section by section; `journal doc keep <n>` closes the open revision as it is, and the next edit
  opens a new one. `journal doc revisions <n>` lists them, number, time, author and change; `journal doc revision <n> <k>`
  prints one in full. An old revision can be read but never restored.
- `journal doc import <folder>` imports the documents version 3 stored, each folder's doc.md.
""", keywords=("doc", "docs", "document", "documents"))
