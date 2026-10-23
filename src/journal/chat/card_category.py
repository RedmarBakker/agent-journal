from dataclasses import dataclass


@dataclass(frozen=True)
class CardCategory:
    """What a chat mark is most likely about, guessed once from its title when it is written and kept in its metadata as is_test, is_build and is_upload: a test run, a build or an upload, each when the title holds that word in any case."""

    test: bool
    build: bool
    upload: bool

    @classmethod
    def read(cls, title: str) -> "CardCategory":
        lowered = title.lower()
        return cls("test" in lowered, "build" in lowered, "upload" in lowered)

    def fields(self) -> dict[str, bool]:
        return {"is_test": self.test, "is_build": self.build, "is_upload": self.upload}
