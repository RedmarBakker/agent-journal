from types import MappingProxyType

import pytest

from journal.console.support.hub_rows import HubRows
from journal.features.messages.support.mentions import Mentions
from journal.models.support.ref import Ref
from journal.support.rejection import Rejection


def test_team_named_plan_in_text_is_a_hub_row():
    assert Mentions.found("see acme plan 12 and task 3", MappingProxyType({"acme": "acme"})) == [Ref("acme/plans", 12), Ref("tasks", 3)]
    assert Mentions.found("acme plan 12") == [Ref("plans", 12)]


def test_hub_row_number_on_the_cli():
    assert HubRows.resolve("acme:12", ["acme"]) == 12
    assert HubRows.resolve("31", []) == 31


def test_unknown_or_shared_team_name_is_refused():
    with pytest.raises(Rejection, match="no team is named beta"):
        HubRows.resolve("beta:1", ["acme"])
    with pytest.raises(Rejection, match="more than one team is named acme"):
        HubRows.resolve("acme:1", ["acme", "acme"])
