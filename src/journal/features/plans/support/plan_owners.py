from journal.models.plan import Plan
from journal.repositories.users import Users


class PlanOwners:
    """The user who created a plan, if their account still exists."""

    def __init__(self, users: Users) -> None:
        self.users = users

    def number(self, plan: Plan) -> int:
        creator = plan.creator
        return creator.number() if creator and creator.is_user() else 0

    def name(self, plan: Plan) -> str:
        number = self.number(plan)
        if not number:
            return ""
        users = self.users.numbered([number])
        return users[0].name if users and users[0].name else f"user {number}"
