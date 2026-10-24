from journal.models.template import TESTING, Template

CRITIQUE = "critique"

FUNCTIONAL = Template(
    title="Functional design",
    targets=("doc",),
    brief="A functional design says what is to be built, never how: anyone, the user or a colleague or another agent, can read it and know what the finished thing must do. Explore while you write it: read the code, look at packages, ask the questions through the journal. Keep it to what the user sees and does, in their words, and write every requirement as a point under Must have that someone can tick off. When the user approves it, the doc is made final and a plan is made from it whose tasks each name the points they cover.",
    parts=(
        "What it is for: who it is for and what it lets them do that they cannot now",
        "What the user sees and does: the screens, the steps and the words, as the user meets them",
        "Must have: - [ ] one requirement per line, each one something to tick off",
        "Open questions: what still has to be decided, each asked through the journal",
        "Not in this version: what is left out on purpose",
    ),
)
FIND_MISTAKES = Template(
    title="Find what is wrong",
    targets=("plan",),
    purpose=CRITIQUE,
    brief="Read the plan as someone who has to build it tomorrow and find what will go wrong: a phase that cannot be done in the order given, a task that is too big or too vague to finish, a goal no task reaches, a check that proves nothing. Name each problem with the phase or task it is in and say what to change.",
)
FIND_GAPS = Template(
    title="Find what is missing",
    targets=("plan",),
    purpose=CRITIQUE,
    brief="Read the plan against its goal and add what it leaves out: the step nobody wrote down, the migration, the test, the error case, the user who is not the author. Propose each addition as a task with the phase it belongs in.",
)
CHALLENGE = Template(
    title="Challenge the approach",
    targets=("plan",),
    purpose=CRITIQUE,
    brief="Question the plan's approach as a whole: is there a simpler way to reach the same goal, something that already exists and could be reused, a risk the plan takes without saying so. Give the alternative and what it would cost.",
)
ZERO_TESTS = Template(
    title="No tests",
    targets=("worker",),
    purpose=TESTING,
    brief="Run no tests. Write the tests that prove your change and name each, with the command that runs it, in your proof: the agent that merges your work runs them.",
)
SCOPED_TESTS = Template(
    title="Scoped tests",
    targets=("worker",),
    purpose=TESTING,
    brief="Run only the tests that cover your change, by name, and the new tests you write. Never run the full suite: the agent that sent you runs it once your work is back.",
)
FULL_SUITE = Template(
    title="Full suite",
    targets=("worker",),
    purpose=TESTING,
    brief="Run the tests that cover your change while you work, and the full suite once before you clock out.",
)
PLAN_ZERO_TESTS = Template(
    title="Never run tests",
    targets=("plan",),
    purpose=TESTING,
    brief="Run no tests while you follow this plan; write the tests that prove each task and leave them for the user to run.",
)
PLAN_PHASE_TESTS = Template(
    title="Tests at each phase end",
    targets=("plan",),
    purpose=TESTING,
    brief="Write the tests each task needs, and run the tests only at the end of each phase.",
)
PLAN_SCOPED_TESTS = Template(
    title="Scoped tests after each task",
    targets=("plan",),
    purpose=TESTING,
    brief="After each task run the tests that cover what it changed, by name, and the full suite at the end of each phase.",
)
PLAN_FULL_TESTS = Template(
    title="Test throughout",
    targets=("plan",),
    purpose=TESTING,
    brief="Run the full suite whenever it helps, and after every task at least.",
)
SHIPPED = (FUNCTIONAL, FIND_MISTAKES, FIND_GAPS, CHALLENGE, ZERO_TESTS, SCOPED_TESTS, FULL_SUITE, PLAN_ZERO_TESTS, PLAN_PHASE_TESTS, PLAN_SCOPED_TESTS, PLAN_FULL_TESTS)
PLAN_TESTING_TEMPLATES = (PLAN_ZERO_TESTS, PLAN_PHASE_TESTS, PLAN_SCOPED_TESTS, PLAN_FULL_TESTS)
