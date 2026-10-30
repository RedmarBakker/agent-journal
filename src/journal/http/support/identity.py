from journal.http.support.plugin_claim import PluginClaim
from journal.support.plugin_tokens import PluginTokens
from journal.support.actor import Actor
from journal.support.caller import LOCAL_USER


class Identity:
    """Reads who a request is from: the viewer or phone carries the user's token, and the local viewer with no token is this machine's person, user 1, and a plugin's program names itself with the token it was given. A hook names its agent in its body, not here."""

    def __init__(self, tokens: PluginTokens) -> None:
        self.tokens = tokens

    def build(self, headers: dict) -> Actor:
        claim = PluginClaim.header_claim(headers)
        if claim.plugin and self.tokens.matches(claim.plugin, claim.token):
            return Actor.plugin(claim.plugin)
        return Actor.user(LOCAL_USER)
