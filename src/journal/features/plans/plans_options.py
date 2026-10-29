from journal.support.option import USER, Option
from journal.support.option_scope import OptionScope
from journal.features.templates.shipped import PLAN_TESTING_TEMPLATES


class PlansOptions:
    """The options of the plans feature."""

    TESTING = Option("plans.testing", "Testing template for new plans", "How a new plan's agent is asked to test, until the plan page changes it", "none", option_type="choice", choices=("none", *(template.title for template in PLAN_TESTING_TEMPLATES)))
    TEST_COMMANDS = Option("plans.test_commands", "Test commands", "The command lines that run this project's tests, separated by commas, such as journal suite, python3 -m pytest: a plan task waits until they are set, and a plan that tests at its phase ends refuses them in the middle of a phase", "", option_type="text")
    PLAN_AGENTS = Option("plans.plan_agents", "Plan agents instead of work modes", "On: the main agent coordinates every plan and writes no code, each plan has its own Plan agent and a mode, organization or solo, and the Work mode setting is not used. Off: the agent works in the Work mode set, builder, orchestrator or solo. While the Plan agents are being built, turn it on only to try them", False, option_type="switch", scope=OptionScope.PERSON, setter=USER)
