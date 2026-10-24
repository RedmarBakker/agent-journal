from journal.support.option import Option


class DocsOptions:
    REVISION_WINDOW = Option("docs.revision_window", "Save an open revision after no edits for",
                             "Edits within this many minutes of the last fold into the document's open revision; after it, the next edit opens a new one", 30, unit="minutes")
