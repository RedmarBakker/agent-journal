class ScopedRepository:
    """A stand-in for the scoped base, so the samples below extend it."""


class Parcels(ScopedRepository):
    """A sample for scoped-read-around-scope and unscoped-read-outside-base: the first two reads skip the environment scope, the third goes through it."""

    def parcel_rows(self, query):
        return self.connection.all(*query.select())

    def unscoped(self, query):
        return self._selected(query)

    def scoped(self, query):
        return self.selected(query)
