from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.estimates.feature import Estimates
from journal.support.option import USER
from journal.support.option_scope import OptionScope


def test_work_in_progress_limits_are_registered_as_owner_settings():
    limits = (
        EstimatesOptions.EXECUTION_WIP_LIMIT,
        EstimatesOptions.PLAN_DELIVERY_WIP_LIMIT,
        EstimatesOptions.DOMAIN_DELIVERY_WIP_LIMIT,
        EstimatesOptions.WORKER_QUEUE_WIP_LIMIT,
    )

    for option in limits:
        assert option in Estimates.options
        assert option.setter == USER
        assert option.scope == OptionScope.PERSON
        assert option.option_type == "number"
        assert option.default == 0
