from journal.providers.claude import Claude


class VoidProvider:
    """The provider a story runs on unless the provider is what it tests: the journal's default program carries its hooks, and no step or expectation reads anything that program alone does."""

    name = Claude.name
