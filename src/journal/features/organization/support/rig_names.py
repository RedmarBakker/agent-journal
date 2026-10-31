from journal.support.secret_values import SecretValues


class RigNames:
    """Names organization rigs with this project's identity and reads legacy plan names."""

    def __init__(self, secrets: SecretValues) -> None:
        self.project = secrets.project_id()

    def plan(self, plan_id: int) -> str:
        return f"plan-{self.project}-{plan_id}"

    def organization(self, environment_id: int) -> str:
        return f"organization-{self.project}-{environment_id}"

    @staticmethod
    def legacy_plan(plan_id: int) -> str:
        return f"plan-{plan_id}"

    @staticmethod
    def legacy_organization(environment_id: int) -> str:
        return f"organization-{environment_id}"

    def plan_id(self, rig: str) -> int | None:
        if rig.startswith(f"plan-{self.project}-"):
            value = rig.removeprefix(f"plan-{self.project}-")
        elif rig.startswith("plan-"):
            value = rig.removeprefix("plan-")
        else:
            return None
        return int(value) if value.isdigit() else None
