import pytest

from journal.features.estimates.estimates_options import EstimatesOptions
from journal.models.sprint import Sprint
from journal.repositories.sprints import Sprints
from journal.support.actor import Actor
from journal.support.rejection import Rejection


def test_sprint_interval_includes_its_start_and_excludes_its_end():
    sprint = Sprint(starts_at=10, ends_at=20)

    assert not sprint.includes(9)
    assert sprint.includes(10)
    assert sprint.includes(19.999)
    assert not sprint.includes(20)


def test_sprint_settings_start_off_with_a_fourteen_day_calendar():
    assert EstimatesOptions.MODE.default == "off"
    assert EstimatesOptions.SPRINT_LENGTH_DAYS.default == 14


def test_only_the_local_owner_actor_can_use_sprint_management():
    with pytest.raises(Rejection, match="only the organization owner"):
        Sprints.owner(Actor.plugin("planner"))
