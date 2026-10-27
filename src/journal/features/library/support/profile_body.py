from journal.features.library.support.portable_body import PortableBody
from journal.providers.support.profile import Profile
from journal.providers.support.profile_type import ProfileType

PROFILE_FIELDS = ("name", "description", "tools", "body")


class ProfileBody:
    """A worker's or subagent's profile as the library carries it: its name, what it does, its tools, its instructions and its type, never the model a machine sets for it, which each provider writes into its own file; and back into a profile."""

    @staticmethod
    def text(profile: Profile) -> str:
        return PortableBody.text({**{name: getattr(profile, name) for name in PROFILE_FIELDS}, "profile_type": str(profile.profile_type)})

    @staticmethod
    def profile(text: str) -> Profile:
        fields = PortableBody.fields(text)
        return Profile(**{name: str(fields[name]) for name in PROFILE_FIELDS}, profile_type=ProfileType(fields["profile_type"]))
