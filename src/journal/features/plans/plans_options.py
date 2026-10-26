from journal.support.option import Option
from journal.features.templates.shipped import PLAN_TESTING_TEMPLATES


class PlansOptions:
    """The options of the plans feature."""

    TESTING = Option("plans.testing", "Testing template for new plans", "How a new plan's agent is asked to test, until the plan page changes it", "none", kind="choice", choices=("none", *(template.title for template in PLAN_TESTING_TEMPLATES)))
    REVIEW_TOOL_USE_LIMIT = Option("plans.review_ready_within", "Ready a reviewed plan within", "Tool uses after a plan's reviewers are all back before every write but plan and task commands waits until the plan is readied", 10, unit="tool uses")
    TEST_COMMANDS = Option("plans.test_commands", "Test commands", "The command lines that run this project's tests, separated by commas, such as journal suite, python3 -m pytest: a plan task waits until they are set, and a plan that tests at its phase ends refuses them in the middle of a phase", "")
