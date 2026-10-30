# @sin SentenceTypeNameDetector
class TaskOfTheDay:
    """A sample for the sentence names: a class, a method, a parameter and a variable named as sentences."""

    # @sin SentenceMethodNameDetector
    # @sin PoeticMethodNameDetector
    def titles_by_state(self, state: str) -> list[str]:
        return [state]

    # @sin SentenceParameterNameDetector
    def title(self, task_of_plan: str) -> str:
        return ""

    def count(self) -> int:
        # @sin SentenceVariableNameDetector
        count_of_tasks = 1
        return 1


# @righteous SentenceTypeNameDetector
class DailyTask:
    """A plain name of the same thing."""

    # @righteous SentenceMethodNameDetector
    def state_titles(self, state: str) -> list[str]:
        return [state]
