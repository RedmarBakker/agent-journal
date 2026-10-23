from typing import TypedDict

AgentToolInput = TypedDict("AgentToolInput", {"subagent_type": str, "model": str, "description": str, "prompt": str, "run_in_background": bool}, total=False)
