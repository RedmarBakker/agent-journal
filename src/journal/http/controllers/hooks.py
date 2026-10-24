from journal.repositories.setting_rows import SettingRows
from journal.support.announced_commands import AnnouncedCommands
from journal.support.actor import Actor
from journal.support.actor_kind import ActorKind
from journal.support.hook import Hook
from journal.support.hook_kind import HookKind
from journal.hooks.hook_arrivals import HookArrivals
from journal.hooks.receiver import Receiver
from journal.hooks.support.tool_calls import ToolCalls
from journal.http.support.request import REQUEST_TIME_HEADER, Request
from journal.support.response import Response
from journal.providers.providers import Providers
from journal.features.faults.faults_options import FaultsOptions

LAUNCH_HEADER = "x-journal-launch"
ACTOR_HEADER = "x-journal-actor"
ACTOR_TOKEN_HEADER = "x-journal-actor-token"


class HookController:
    def __init__(self, receiver: Receiver, providers: Providers, announced: AnnouncedCommands, calls: ToolCalls, settings: SettingRows, arrivals: HookArrivals) -> None:
        self.receiver, self.providers, self.announced, self.calls, self.settings, self.arrivals = receiver, providers, announced, calls, settings, arrivals

    def receive(self, request: Request) -> Response:
        self.arrivals.record_arrival(request.environment)
        parsed = Hook.parse(request.body, request.environment, request.params["agent"], request.headers.get(LAUNCH_HEADER, ""))
        stamp = request.headers.get(REQUEST_TIME_HEADER)
        stamped = (parsed.stamped(int(request.request_at * 1000)) if stamp else parsed).boot_delayed(request.boot_wait_seconds)
        hook = self.sender_stamped(stamped, request)
        if hook.subagent and hook.kind == HookKind.PRE_TOOL_USE:
            return self.announce(hook)
        if hook.kind == HookKind.PRE_TOOL_USE:
            self.announced.withdraw(hook.environment, hook.session, self.shell_parts(hook))
        provider, decision = self.providers.lookup(hook.provider), self.receiver.receive(hook)
        return provider.answer(hook, decision) if self.is_copy_shown() else provider.agent_answer(hook, decision)

    @staticmethod
    def sender_stamped(hook: Hook, request: Request) -> Hook:
        actor, token = request.headers.get(ACTOR_HEADER, ""), request.headers.get(ACTOR_TOKEN_HEADER)
        worker, verifier = Actor.stamp_number(actor, ActorKind.WORKER), Actor.stamp_number(actor, ActorKind.VERIFIER)
        if worker is not None:
            return hook.worker_hook(worker, token)
        return hook.verifier_hook(verifier, token) if verifier is not None else hook

    def is_copy_shown(self) -> bool:
        return bool(self.settings.option(FaultsOptions.HOOK_LINE_COPY))

    def announce(self, hook: Hook) -> Response:
        if parts := self.shell_parts(hook):
            self.announced.note(hook.environment, hook.session, parts)
        return Response.json({})

    def shell_parts(self, hook: Hook) -> tuple[str, ...]:
        return tuple(part.text for part in self.calls.build(hook).parts)
